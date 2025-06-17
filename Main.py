import matplotlib.image as mpimg
import networkx as nx
import matplotlib.pyplot as plt

# Crear el grafo no dirigido
G = nx.Graph()

# Añadir nodos: (nombre, coordenadas y si tiene estación de carga)
# Las coordenadas solo son para visualizar el grafo, no son necesarias para el algoritmo.
nodos = {
    "Artigas": {"pos": (-57.130, -30.8), "carga": True},
    "Canelones": {"pos": (-56.085, -34.777), "carga": False},
    "Cerro Largo": {"pos": (-54.72, -32.67), "carga": True},
    "Colonia": {"pos": (-57.8445, -34.4624), "carga": False},
    "Durazno": {"pos": (-56.5237, -33.3796), "carga": True},
    "Flores": {"pos": (-56.93, -33.865), "carga": False},
    "Florida": {"pos": (-56.2150, -34.0954), "carga": False},
    "Lavalleja": {"pos": (-55.28, -34.18), "carga": False},
    "Maldonado": {"pos": (-55.33, -35.08), "carga": False},
    "Montevideo": {"pos": (-56.393, -35.1), "carga": False},
    "Paysandu": {"pos": (-57.4, -32.38), "carga": False},
    "Rivera": {"pos": (-55.5333, -31.797), "carga": False},
    "Rio Negro": {"pos": (-57.450, -33.04), "carga": True},
    "Rocha": {"pos": (-54.3375, -34.4833), "carga": False},
    "Salto": {"pos": (-57.19, -31.582), "carga": True},
    "San Jose": {"pos": (-56.82, -34.6), "carga": False},
    "Soriano": {"pos": (-57.77, -33.75), "carga": True},
    "Tacuarembo": {"pos": (-55.9, -32.4), "carga": False},
    "Treinta y Tres": {"pos": (-54.3030, -33.2333), "carga": True}
}

# Agregar nodos al grafo
for ciudad, data in nodos.items():
    G.add_node(ciudad, pos=data["pos"], carga=data["carga"])

# Agregar aristas con distancia y velocidad
G.add_edge("Artigas", "Salto", distancia=120, velocidad=110)
G.add_edge("Canelones", "Florida", distancia=100, velocidad=110)
G.add_edge("Canelones", "Lavalleja", distancia=120, velocidad=110)
G.add_edge("Canelones", "Maldonado", distancia=150, velocidad=110)
G.add_edge("Colonia", "San Jose", distancia=120, velocidad=110)
G.add_edge("Cerro Largo", "Rivera", distancia=180, velocidad=110)
G.add_edge("Cerro Largo", "Tacuarembo", distancia=160, velocidad=110)
G.add_edge("Cerro Largo", "Treinta y Tres", distancia=120, velocidad=110)
G.add_edge("Durazno", "Rio Negro", distancia=100, velocidad=110)
G.add_edge("Durazno", "Tacuarembo", distancia=200, velocidad=110)
G.add_edge("Durazno", "Treinta y Tres", distancia=220, velocidad=110)
G.add_edge("Flores", "Florida", distancia=90, velocidad=110)
G.add_edge("Flores", "Soriano", distancia=90, velocidad=110)
G.add_edge("Florida", "Durazno", distancia=100, velocidad=110)
G.add_edge("Florida", "Lavalleja", distancia=100, velocidad=110)
G.add_edge("Lavalleja", "Maldonado", distancia=140, velocidad=110)
G.add_edge("Lavalleja", "Treinta y Tres", distancia=150, velocidad=110)
G.add_edge("Maldonado", "Rocha", distancia=120, velocidad=110)
G.add_edge("Montevideo", "Canelones", distancia=50, velocidad=110)
G.add_edge("Montevideo", "Maldonado", distancia=130, velocidad=110)
G.add_edge("Montevideo", "San Jose", distancia=110, velocidad=110)
G.add_edge("Paysandu", "Tacuarembo", distancia=150, velocidad=110)
G.add_edge("Rio Negro", "Paysandu", distancia=110, velocidad=110)
G.add_edge("Rio Negro", "Soriano", distancia=100, velocidad=110)
G.add_edge("Rivera", "Artigas", distancia=140, velocidad=110)
G.add_edge("Salto", "Paysandu", distancia=100, velocidad=110)
G.add_edge("Salto", "Rivera", distancia=200, velocidad=110)
G.add_edge("Soriano", "Colonia", distancia=120, velocidad=110)
G.add_edge("Treinta y Tres", "Rocha", distancia=160, velocidad=110)


# Visualizar el grafo

pos = nx.get_node_attributes(G, 'pos')

# ---- Algoritmo A* considerando autonomía y carga ----
import heapq

# Parámetros del auto eléctrico
AUTONOMIA_KM = 400
VEL_CARGA_KM_H = 170  # Velocidad de carga en km/h
CONSUMO_BASE = 1  # Consumo del auto eléctrico
PENALIZACION_VELOCIDAD = 0.02  # penalización por km/h por encima de 80 km/h
PENALIZACION_CARGA = 10  # Minutos agregados por cada parada a cargar

def estimate_consumption(velocidad_kmh):
    return CONSUMO_BASE + PENALIZACION_VELOCIDAD * max(0, velocidad_kmh - 80)

def a_estrella_ev(inicio, destino, grafo):
    open_set = []
    heapq.heappush(open_set, (0, inicio, AUTONOMIA_KM, 0, 0, [inicio]))  # (costo_estimado, nodo, bateria_restante, tiempo_real, carga_total, camino)

    visitado = {}

    while open_set:
        _, actual, bateria_restante, tiempo_real, carga_total, camino = heapq.heappop(open_set)

        estado_clave = (actual, round(bateria_restante))
        if estado_clave in visitado and visitado[estado_clave] <= tiempo_real:
            continue
        visitado[estado_clave] = tiempo_real

        if actual == destino:
            print(f"Ruta encontrada:")
            for paso in camino:
                print(f"  {paso}")
            total_horas = int(tiempo_real + carga_total)
            total_minutos = int((tiempo_real + carga_total - total_horas) * 60)
            print(f"Tiempo total estimado: {total_horas:02}:{total_minutos:02} h")
            print(f"Batería restante al llegar a destino: {round(bateria_restante, 2)} km")

            viaje_h = int(tiempo_real)
            viaje_m = int((tiempo_real - viaje_h) * 60)
            print(f"  Tiempo de viaje puro: {viaje_h:02}:{viaje_m:02} h")
            carga_h = int(carga_total)
            carga_m = int((carga_total - carga_h) * 60)
            print(f"  Tiempo de carga total: {carga_h:02}:{carga_m:02} h")
            return camino, tiempo_real + carga_total

        for vecino in grafo[actual]:
            datos = grafo[actual][vecino]
            distancia = datos['distancia']
            velocidad = datos['velocidad']
            consumo = estimate_consumption(velocidad)
            consumo_total = distancia * consumo
            tiempo_viaje = distancia / velocidad

            # Si puede llegar con la batería actual
            if bateria_restante >= consumo_total:
                heapq.heappush(open_set, (
                    tiempo_real + tiempo_viaje + carga_total,
                    vecino,
                    bateria_restante - consumo_total,
                    tiempo_real + tiempo_viaje,
                    carga_total,
                    camino + [vecino]
                ))

            # Evaluar cargar si hay estación
            if G.nodes[actual]['carga']:
                # Cargar solo si es necesario para llegar
                if bateria_restante < consumo_total:
                    energia_necesaria = consumo_total - bateria_restante
                    nueva_bateria = bateria_restante + energia_necesaria
                    tiempo_carga = energia_necesaria / VEL_CARGA_KM_H + PENALIZACION_CARGA / 60
                    heapq.heappush(open_set, (
                        tiempo_real + tiempo_viaje + carga_total + tiempo_carga,
                        vecino,
                        nueva_bateria - consumo_total,
                        tiempo_real + tiempo_viaje,
                        carga_total + tiempo_carga,
                        camino + [f"Cargar parcialmente en {actual} hasta {round(nueva_bateria, 2)} km", vecino]
                    ))

                # También considerar carga completa
                energia_faltante = AUTONOMIA_KM - bateria_restante
                tiempo_carga_full = energia_faltante / VEL_CARGA_KM_H + PENALIZACION_CARGA / 60
                nueva_bateria_full = AUTONOMIA_KM
                if nueva_bateria_full >= consumo_total:
                    heapq.heappush(open_set, (
                        tiempo_real + tiempo_viaje + carga_total + tiempo_carga_full,
                        vecino,
                        nueva_bateria_full - consumo_total,
                        tiempo_real + tiempo_viaje,
                        carga_total + tiempo_carga_full,
                        camino + [f"Cargar en {actual}", vecino]
                    ))

    print("No se encontró ruta.")
    return None, float("inf")

# Ejecutar algoritmo
camino, tiempo = a_estrella_ev("Montevideo", "Salto", G)

# Mostrar el mapa de fondo y grafo con ruta calculada
fig, ax = plt.subplots(figsize=(10, 6))
imagen = mpimg.imread("mapa_uruguay.jpeg")
ax.imshow(imagen, extent=[-58.5, -53.5, -35.3, -30.0], alpha=0.6)

# Dibujar todos los nodos (sin etiquetas)
nx.draw_networkx_nodes(G, pos,
        node_color=["lightgreen" if G.nodes[n]['carga'] else "lightgray" for n in G.nodes],
        node_size=100, ax=ax)

# Dibujar todas las aristas del grafo (sin etiquetas de distancia)
nx.draw_networkx_edges(G, pos, edge_color='gray', width=1, ax=ax)

# Si se encontró un camino, dibujarlo en rojo
if camino:
    # Limpiar el camino de instrucciones de carga
    camino_filtrado = [n for n in camino if not n.startswith("Cargar")]
    ruta = [
        (camino_filtrado[i], camino_filtrado[i+1])
        for i in range(len(camino_filtrado) - 1)
    ]

    nx.draw_networkx_edges(G, pos, edgelist=ruta, edge_color='red', width=4, ax=ax)

    # Dibujar solo las etiquetas de los nodos del camino encontrado
    nx.draw_networkx_labels(G, pos, labels={n: n for n in camino_filtrado}, font_size=10, ax=ax)

    # Mostrar tiempos de carga en los nodos del camino final
    from collections import defaultdict

    # Registrar y mostrar los tiempos de carga en los nodos
    tiempos_carga_por_nodo = defaultdict(float)

    i = 0
    while i < len(camino) - 1:
        paso = camino[i]
        siguiente = camino[i + 1]
        if paso.startswith("Cargar"):
            nodo = paso.split(" en ")[-1].split(" hasta")[0]
            if "parcialmente" in paso:
                km_objetivo = float(paso.split("hasta ")[-1].split(" km")[0])
                energia_agregada = km_objetivo - AUTONOMIA_KM if km_objetivo > AUTONOMIA_KM else km_objetivo
            else:
                energia_agregada = AUTONOMIA_KM  # carga completa
            tiempo_carga = energia_agregada / VEL_CARGA_KM_H
            tiempos_carga_por_nodo[nodo] += tiempo_carga
        i += 1

    # Mostrar los tiempos de carga como etiquetas adicionales
    for nodo, tiempo in tiempos_carga_por_nodo.items():
        x, y = pos[nodo]
        horas = int(tiempo)
        minutos = int((tiempo - horas) * 60)
        texto = f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"
        ax.text(x, y + 0.2, texto, fontsize=8, color="black", ha='center')

plt.title("Ruta calculada")
plt.show()