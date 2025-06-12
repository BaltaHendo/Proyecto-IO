import networkx as nx
import matplotlib.pyplot as plt

# Crear el grafo dirigido
G = nx.DiGraph()

# Añadir nodos: (nombre, coordenadas y si tiene estación de carga)
nodos = {
    "Montevideo": {"pos": (-56.1645, -34.9011), "carga": True},
    "Maldonado": {"pos": (-54.9586, -34.9081), "carga": True},
    "Punta del Este": {"pos": (-54.9430, -34.9624), "carga": False},
    "Colonia": {"pos": (-57.8445, -34.4624), "carga": True},
    "Rocha": {"pos": (-54.3375, -34.4833), "carga": False},
    "Paysandú": {"pos": (-58.0756, -32.3214), "carga": True},
    "Salto": {"pos": (-57.9601, -31.3895), "carga": True},
    "Rivera": {"pos": (-55.5333, -30.9058), "carga": False},
    "Tacuarembó": {"pos": (-55.9964, -31.7131), "carga": False},
    "Florida": {"pos": (-56.2150, -34.0954), "carga": False},
    "Durazno": {"pos": (-56.5237, -33.3796), "carga": False},
    "Treinta y Tres": {"pos": (-54.3030, -33.2333), "carga": False},
    "Artigas": {"pos": (-56.4678, -30.4018), "carga": False},
    "Canelones": {"pos": (-55.7381, -34.5228), "carga": False}
}

# Agregar nodos al grafo
for ciudad, data in nodos.items():
    G.add_node(ciudad, pos=data["pos"], carga=data["carga"])

# Agregar aristas con distancia y velocidad
G.add_edge("Montevideo", "Maldonado", distancia=130, velocidad=90)
G.add_edge("Maldonado", "Punta del Este", distancia=10, velocidad=60)
G.add_edge("Montevideo", "Colonia", distancia=180, velocidad=100)
G.add_edge("Colonia", "Rocha", distancia=300, velocidad=100)
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
G.add_edge("Montevideo", "Paysandú", distancia=370, velocidad=110)
G.add_edge("Salto", "Artigas", distancia=200, velocidad=90)

# Visualizar el grafo
pos = nx.get_node_attributes(G, 'pos')

plt.figure(figsize=(10, 6))
nx.draw(G, pos, with_labels=True, node_color=["green" if G.nodes[n]['carga'] else "lightgray" for n in G.nodes],
        node_size=1000, font_size=10, arrows=True)
edge_labels = {(u, v): f"{d['distancia']} km" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue')
plt.title("Red de rutas con estaciones de carga en Uruguay")
plt.show()

# ---- Algoritmo A* considerando autonomía y carga ----
import heapq

# Parámetros del auto eléctrico
AUTONOMIA_KM = 300
VEL_CARGA_KM_H = 300  # km/h de carga rápida (simulado)
CONSUMO_BASE = 1.0  # consumo base por km
PENALIZACION_VELOCIDAD = 0.005  # penalización por km/h por encima de 80 km/h

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

            if G.nodes[actual]['carga']:
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

    print("No se encontró ruta.")
    return None, float("inf")

# Ejecutar algoritmo
camino, tiempo = a_estrella_ev("Montevideo", "Rocha", G)