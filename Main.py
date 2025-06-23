import matplotlib.image as mpimg
import networkx as nx
import matplotlib.pyplot as plt



# Crear el grafo no dirigido
G = nx.Graph()

# Añadir nodos: (nombre, coordenadas y si tiene estación de carga)
# Las coordenadas solo son para visualizar el grafo, no son necesarias para el algoritmo.
nodos = {
    "Artigas": {"pos": (-57.130, -30.8), "carga": True},
    "Canelones": {"pos": (-56.085, -34.777), "carga": True},
    "Cerro Largo": {"pos": (-54.72, -32.67), "carga": True},
    "Colonia": {"pos": (-57.8445, -34.4624), "carga": True},
    "Durazno": {"pos": (-56.5237, -33.3796), "carga": True},
    "Flores": {"pos": (-56.93, -33.865), "carga": True},
    "Florida": {"pos": (-56.2150, -34.0954), "carga": True},
    "Lavalleja": {"pos": (-55.28, -34.18), "carga": True},
    "Maldonado": {"pos": (-55.33, -35.08), "carga": True},
    "Montevideo": {"pos": (-56.393, -35.1), "carga": True},
    "Paysandu": {"pos": (-57.4, -32.38), "carga": True},
    "Rivera": {"pos": (-55.5333, -31.797), "carga": True},
    "Rio Negro": {"pos": (-57.450, -33.04), "carga": True},
    "Rocha": {"pos": (-54.3375, -34.4833), "carga": True},
    "Salto": {"pos": (-57.19, -31.582), "carga": True},
    "San Jose": {"pos": (-56.82, -34.6), "carga": True},
    "Soriano": {"pos": (-57.77, -33.75), "carga": True},
    "Tacuarembo": {"pos": (-55.9, -32.4), "carga": True},
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
PENALIZACION_VELOCIDAD = 0.02  # Penalización por km/h por encima de 80 km/h (0.02 = 2% más de consumo por km/h extra)
PENALIZACION_CARGA = 10  # Minutos agregados por cada parada a cargar
MARGEN_AUTONOMIA = 0.1  # Porcentaje mínimo de autonomía para llegar a cada nodo (0.1 = 10%)
PORCENTAJE_CARGA_INICIAL = 1  # Porcentaje de carga inicial del vehículo (1 = 100% de batería)

def estimate_consumption(velocidad_kmh):
    return 1 + PENALIZACION_VELOCIDAD * max(0, velocidad_kmh - 80)

def a_estrella_ev(inicio, destino, grafo):
    open_set = []
    heapq.heappush(
        open_set,
        (
            0,
            inicio,
            AUTONOMIA_KM * PORCENTAJE_CARGA_INICIAL,
            0,
            0,
            [inicio],
            [AUTONOMIA_KM * PORCENTAJE_CARGA_INICIAL],
        ),
    )  # (costo_estimado, nodo, bateria_restante, tiempo_real, carga_total, camino, historial_bateria)

    visitado = {}

    while open_set:
        _, actual, bateria_restante, tiempo_real, carga_total, camino, historial_bateria = heapq.heappop(open_set)

        # Si el nodo ya fue visitado con mejor tiempo, saltar
        estado_clave = (actual, round(bateria_restante))
        if estado_clave in visitado and visitado[estado_clave] <= tiempo_real:
            continue
        visitado[estado_clave] = tiempo_real

        # Si llegamos al destino
        if actual == destino:
            print(f"Ruta encontrada:")
            for i, paso in enumerate(camino):
                if paso.startswith("Cargar"):
                    print(f"  {paso}")
                else:
                    print(f"  {paso} ({round(historial_bateria[i], 2)} km)")
            total_horas = int(tiempo_real + carga_total)
            total_minutos = int((tiempo_real + carga_total - total_horas) * 60)
            print(f"Tiempo total estimado: {total_horas:02}:{total_minutos:02} h")
            print(f"Batería restante al llegar a destino: {round(bateria_restante, 2)} km")

            # Calcular tiempos de viaje y carga
            viaje_h = int(tiempo_real)
            viaje_m = int((tiempo_real - viaje_h) * 60)
            print(f"  Tiempo de viaje puro: {viaje_h:02}:{viaje_m:02} h")
            carga_h = int(carga_total)
            carga_m = int((carga_total - carga_h) * 60)
            print(f"  Tiempo de carga total: {carga_h:02}:{carga_m:02} h")
            return camino, tiempo_real + carga_total, historial_bateria

        # Explorar vecinos
        for vecino in grafo[actual]:
            datos = grafo[actual][vecino]
            distancia = datos['distancia']
            velocidad = datos['velocidad']
            consumo = estimate_consumption(velocidad)
            consumo_total = distancia * consumo
            tiempo_viaje = distancia / velocidad

            # Si puede llegar con la batería actual
            if bateria_restante - consumo_total >= 0:
                autonomia_restante = bateria_restante - consumo_total
                if autonomia_restante >= MARGEN_AUTONOMIA * AUTONOMIA_KM:
                    heapq.heappush(open_set, (
                        tiempo_real + tiempo_viaje + carga_total,
                        vecino,
                        autonomia_restante,
                        tiempo_real + tiempo_viaje,
                        carga_total,
                        camino + [vecino],
                        historial_bateria + [autonomia_restante]
                    ))

            # Evaluar cargar si hay estación
            if G.nodes[actual]['carga']:
                # Cargar solo si es necesario para llegar
                if bateria_restante < consumo_total:
                    energia_necesaria = consumo_total - bateria_restante
                    nueva_bateria = bateria_restante + energia_necesaria
                    tiempo_carga = energia_necesaria / VEL_CARGA_KM_H + PENALIZACION_CARGA / 60
                    autonomia_restante = nueva_bateria - consumo_total
                    if autonomia_restante >= MARGEN_AUTONOMIA * AUTONOMIA_KM:
                        heapq.heappush(open_set, (
                            tiempo_real + tiempo_viaje + carga_total + tiempo_carga,
                            vecino,
                            autonomia_restante,
                            tiempo_real + tiempo_viaje,
                            carga_total + tiempo_carga,
                            camino + [f"Cargar parcialmente en {actual} hasta {round(nueva_bateria, 2)} km ({round(tiempo_carga, 2)} h)", vecino],
                            historial_bateria + [nueva_bateria, autonomia_restante]
                        ))

                # Considerar carga parcial hasta justo lo necesario
                energia_requerida_margen = consumo_total + MARGEN_AUTONOMIA * AUTONOMIA_KM - bateria_restante
                if energia_requerida_margen > 0 and energia_requerida_margen <= AUTONOMIA_KM - bateria_restante:
                    nueva_bateria_parcial = bateria_restante + energia_requerida_margen
                    tiempo_carga_parcial = energia_requerida_margen / VEL_CARGA_KM_H + PENALIZACION_CARGA / 60
                    autonomia_restante_parcial = nueva_bateria_parcial - consumo_total
                    heapq.heappush(open_set, (
                        tiempo_real + tiempo_viaje + carga_total + tiempo_carga_parcial,
                        vecino,
                        autonomia_restante_parcial,
                        tiempo_real + tiempo_viaje,
                        carga_total + tiempo_carga_parcial,
                        camino + [f"Cargar parcialmente en {actual} hasta {round(nueva_bateria_parcial, 2)} km ({round(tiempo_carga_parcial, 2)} h)", vecino],
                        historial_bateria + [nueva_bateria_parcial, autonomia_restante_parcial]
                    ))

                # Solo considerar carga completa si la carga parcial no es suficiente
                energia_faltante = AUTONOMIA_KM - bateria_restante
                nueva_bateria_full = AUTONOMIA_KM
                autonomia_restante_full = nueva_bateria_full - consumo_total
                if autonomia_restante_full >= MARGEN_AUTONOMIA * AUTONOMIA_KM and (energia_requerida_margen <= 0 or energia_requerida_margen > energia_faltante):
                    tiempo_carga_full = energia_faltante / VEL_CARGA_KM_H + PENALIZACION_CARGA / 60
                    heapq.heappush(open_set, (
                        tiempo_real + tiempo_viaje + carga_total + tiempo_carga_full,
                        vecino,
                        autonomia_restante_full,
                        tiempo_real + tiempo_viaje,
                        carga_total + tiempo_carga_full,
                        camino + [f"Cargar en {actual} desde {round(bateria_restante, 2)} km hasta {nueva_bateria_full} km ({round(tiempo_carga_full, 2)} h)", vecino],
                        historial_bateria + [nueva_bateria_full, autonomia_restante_full]
                    ))

    print("No se encontró ruta.")
    return None, float("inf")

# Ejecutar algoritmo
camino, tiempo, historial_bateria = a_estrella_ev("Artigas", "Maldonado", G)

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

    # historial_bateria ya proviene de a_estrella_ev

    # Registrar y mostrar los tiempos de carga en los nodos
    tiempos_carga_por_nodo = defaultdict(float)

    total_carga_mapa = 0

    indice_bateria = 0
    tiempos_carga_por_nodo = defaultdict(float)
    total_carga_mapa = 0

    for i, paso in enumerate(camino):
        if paso.startswith("Cargar"):
            # Extraer el nombre del nodo correctamente
            if " en " in paso:
                contenido = paso.split(" en ")[1]
                if " desde" in contenido:
                    nodo = contenido.split(" desde")[0].strip()
                elif " hasta" in contenido:
                    nodo = contenido.split(" hasta")[0].strip()
                else:
                    nodo = contenido.strip()
            else:
                nodo = camino[i + 1] if i + 1 < len(camino) else "Desconocido"

            if "(" in paso and "h)" in paso:
                try:
                    tiempo_str = paso.split("(")[-1].replace("h)", "").strip()
                    tiempo_carga = float(tiempo_str)
                except:
                    tiempo_carga = 0
            else:
                tiempo_carga = 0

            tiempos_carga_por_nodo[nodo] += tiempo_carga
            total_carga_mapa += tiempo_carga
        else:
            if indice_bateria < len(historial_bateria):
                indice_bateria += 1

    # Mostrar los tiempos de carga como etiquetas adicionales
    for nodo, tiempo in tiempos_carga_por_nodo.items():
        if nodo not in pos:
            print(f"[DEBUG] Nodo no encontrado en posiciones: {nodo}")
        x, y = pos[nodo]
        horas = int(tiempo)
        minutos = max(0, int(round((tiempo - horas) * 60)))
        texto = f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"
        ax.text(x, y + 0.2, texto, fontsize=8, color="black", ha='center')

    horas = int(total_carga_mapa)
    minutos = int((total_carga_mapa - horas) * 60)
    print(f"  Tiempo de carga total mostrado en el mapa: {horas:02}:{minutos:02} h")

plt.title("Ruta calculada")
plt.show()