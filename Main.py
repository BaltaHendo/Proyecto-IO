import matplotlib.image as mpimg
import networkx as nx
import matplotlib.pyplot as plt

# Crear el grafo no dirigido
G = nx.Graph()

# Añadir nodos: (nombre, coordenadas y si tiene estación de carga)
# Las coordenadas solo son para visualizar el grafo, no son necesarias para el algoritmo.
nodos = {
    "Artigas": {"pos": (-57.130, -30.8), "carga": False},
    "Canelones": {"pos": (-56.085, -34.777), "carga": False},
    "Cerro Largo": {"pos": (-54.72, -32.67), "carga": False},
    "Colonia": {"pos": (-57.8445, -34.4624), "carga": True},
    "Durazno": {"pos": (-56.5237, -33.3796), "carga": True},
    "Flores": {"pos": (-56.93, -33.865), "carga": False},
    "Florida": {"pos": (-56.2150, -34.0954), "carga": True},
    "Lavalleja": {"pos": (-55.28, -34.18), "carga": False},
    "Maldonado": {"pos": (-55.33, -35.08), "carga": True},
    "Montevideo": {"pos": (-56.393, -35.1), "carga": True},
    "Paysandú": {"pos": (-57.4, -32.38), "carga": True},
    "Rivera": {"pos": (-55.5333, -31.797), "carga": False},
    "Río Negro": {"pos": (-57.450, -33.04), "carga": False},
    "Rocha": {"pos": (-54.3375, -34.4833), "carga": False},
    "Salto": {"pos": (-57.19, -31.582), "carga": True},
    "San José": {"pos": (-56.82, -34.6), "carga": False},
    "Soriano": {"pos": (-57.77, -33.75), "carga": False},
    "Tacuarembó": {"pos": (-55.9, -32.4), "carga": False},
    "Treinta y Tres": {"pos": (-54.3030, -33.2333), "carga": False}
}

# Agregar nodos al grafo
for ciudad, data in nodos.items():
    G.add_node(ciudad, pos=data["pos"], carga=data["carga"])

# Agregar aristas con distancia y velocidad
G.add_edge("Montevideo", "Maldonado", distancia=130, velocidad=90)
G.add_edge("Montevideo", "Colonia", distancia=180, velocidad=100)
G.add_edge("Maldonado", "Rocha", distancia=90, velocidad=80)
G.add_edge("Montevideo", "Canelones", distancia=50, velocidad=90)
G.add_edge("Canelones", "Florida", distancia=70, velocidad=90)
G.add_edge("Florida", "Durazno", distancia=120, velocidad=100)
G.add_edge("Durazno", "Tacuarembó", distancia=130, velocidad=100)
G.add_edge("Tacuarembó", "Rivera", distancia=115, velocidad=100)
G.add_edge("Durazno", "Paysandú", distancia=190, velocidad=100)
G.add_edge("Paysandú", "Salto", distancia=120, velocidad=90)
G.add_edge("Durazno", "Treinta y Tres", distancia=170, velocidad=80)
G.add_edge("Treinta y Tres", "Rocha", distancia=110, velocidad=80)
G.add_edge("Salto", "Artigas", distancia=200, velocidad=90)

# Visualizar el grafo

pos = nx.get_node_attributes(G, 'pos')

# Mostrar el mapa de fondo
fig, ax = plt.subplots(figsize=(10, 6))
imagen = mpimg.imread("mapa_uruguay.jpeg")
ax.imshow(imagen, extent=[-58.5, -53.5, -35.3, -30.0], alpha=0.6)  # Ajustar 'extent' según el mapa

# Dibujar el grafo sobre la imagen
nx.draw(G, pos, with_labels=True,
        node_color=["lightgreen" if G.nodes[n]['carga'] else "lightgray" for n in G.nodes],
        node_size=100, font_size=10, ax=ax)

edge_labels = {(u, v): f"{d['distancia']} km" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue', ax=ax)

plt.title("Red de rutas con estaciones de carga")
plt.show()

# ---- Algoritmo A* considerando autonomía y carga ----
import heapq

# Parámetros del auto eléctrico
AUTONOMIA_KM = 400
VEL_CARGA_KM_H = 170  # Velocidad de carga en km/h
CONSUMO_BASE = 1  # Consumo del auto eléctrico
PENALIZACION_VELOCIDAD = 0.02  # penalización por km/h por encima de 80 km/h

def estimate_consumption(velocidad_kmh):
    return CONSUMO_BASE + PENALIZACION_VELOCIDAD * max(0, velocidad_kmh - 80)

def a_estrella_ev(inicio, destino, grafo):
    open_set = []
    heapq.heappush(open_set, (0, inicio, AUTONOMIA_KM, 0, [inicio]))

    visitado = {}

    while open_set:
        _, actual, bateria_restante, tiempo_total, camino = heapq.heappop(open_set)

        if (actual, round(bateria_restante)) in visitado:
            continue
        visitado[(actual, round(bateria_restante))] = tiempo_total

        if actual == destino:
            print(f"Ruta encontrada:")
            for paso in camino:
                print(f"  {paso}")
            print(f"Tiempo total estimado: {round(tiempo_total, 2)} h")
            print(f"Batería restante al llegar a destino: {round(bateria_restante, 2)} km")
            return camino, tiempo_total

        for vecino in grafo[actual]:
            datos = grafo[actual][vecino]
            distancia = datos['distancia']
            velocidad = datos['velocidad']
            consumo = estimate_consumption(velocidad)
            consumo_total = distancia * consumo
            tiempo_viaje = distancia / velocidad

            if bateria_restante >= consumo_total:
                nueva_bateria = bateria_restante - consumo_total
                heapq.heappush(open_set, (
                    tiempo_total + tiempo_viaje,
                    vecino,
                    nueva_bateria,
                    tiempo_total + tiempo_viaje,
                    camino + [vecino]
                ))

            if G.nodes[actual]['carga'] and bateria_restante < AUTONOMIA_KM * 0.99:
                # Simular carga completa
                energia_faltante = AUTONOMIA_KM - bateria_restante
                tiempo_carga = energia_faltante / VEL_CARGA_KM_H
                nueva_bateria = AUTONOMIA_KM - consumo_total
                if nueva_bateria >= 0:
                    heapq.heappush(open_set, (
                        tiempo_total + tiempo_carga + tiempo_viaje,
                        vecino,
                        nueva_bateria,
                        tiempo_total + tiempo_carga + tiempo_viaje,
                        camino + [f"Cargar en {actual}", vecino]
                    ))

                # Opción de carga parcial (solo lo necesario para el siguiente tramo, sin exceder la autonomía máxima)
                if bateria_restante < consumo_total:
                    energia_necesaria = consumo_total - bateria_restante
                    carga_destino = min(AUTONOMIA_KM, bateria_restante + energia_necesaria)
                    tiempo_carga_parcial = (carga_destino - bateria_restante) / VEL_CARGA_KM_H
                    heapq.heappush(open_set, (
                        tiempo_total + tiempo_carga_parcial + tiempo_viaje,
                        vecino,
                        carga_destino - consumo_total,
                        tiempo_total + tiempo_carga_parcial + tiempo_viaje,
                        camino + [f"Cargar parcialmente en {actual} hasta {round(carga_destino, 2)} km", vecino]
                    ))

    print("No se encontró ruta.")
    return None, float("inf")

# Ejecutar algoritmo
camino, tiempo = a_estrella_ev("Salto", "Maldonado", G)