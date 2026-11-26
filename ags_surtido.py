"""
Algoritmo Genético Simple (AGS)
Apoyo a la decisión de compra de una tienda de uniformes (problema de la mochila 0-1):
qué lotes comprar al proveedor con el presupuesto de cada surtido.

Uso:
    python3 ags_surtido.py           -> ejecuta el AGS con el ejemplo de 3 prendas
    python3 ags_surtido.py pruebas   -> ejecuta las pruebas de cada fase
    python3 ags_surtido.py grafica   -> ejecuta el ejemplo y guarda su gráfica
    python3 ags_surtido.py tienda    -> ejecuta el AGS con los datos del comerciante
    python3 ags_surtido.py validacion -> compara el AGS con otros métodos (datos del comerciante)
"""
import random
import sys
import itertools


# 1. DATOS DEL PROBLEMA Y PARÁMETROS

# Toda la mercancía se compra al proveedor a precio de mayoreo (costo C).
# Cada prenda tiene dos lotes según su canal de venta:
#   venta al público (por pieza) o pedido de mayoreo (escuelas, revendedores).
# (nombre, costo C, ganancia G)

# Ejemplo de prueba: 3 prendas (el de la traza a mano)
LOTES = [
    ("Camisa (venta al público)", 2700, 1800),
    ("Camisa (pedido de mayoreo)", 3600, 1200),
    ("Pantalón (venta al público)", 2800, 1800),
    ("Pantalón (pedido de mayoreo)", 2800, 1000),
    ("Sudadera (venta al público)", 900, 600),
    ("Sudadera (pedido de mayoreo)", 1800, 700),
]

P = 7000 # presupuesto
LAMBDA = 1 # factor de penalización

# Parámetros
N = 4          # tamaño población (par)
GEN = 10       # número de generaciones
L = len(LOTES) # longitud del cromosoma
PM = 1/L       # probabilidad de mutación por bit

# Datos del comerciante: lotes de 10 piezas, punto medio de cada rango
LOTES_TIENDA = [
    ("Suéter (venta al público)", 1650, 1200),
    ("Suéter (pedido de mayoreo)", 1650, 850),
    ("Camisa (venta al público)", 500, 650),
    ("Camisa (pedido de mayoreo)", 500, 350),
    ("Falda tipo 1 (venta al público)", 2000, 1050),
    ("Falda tipo 1 (pedido de mayoreo)", 2000, 800),
    ("Falda tipo 2 (venta al público)", 1700, 900),
    ("Falda tipo 2 (pedido de mayoreo)", 1700, 650),
    ("Falda tipo 3 (venta al público)", 1350, 700),
    ("Falda tipo 3 (pedido de mayoreo)", 1350, 250),
]
P_TIENDA = 4000      # presupuesto por surtido
LAMBDA_TIENDA = 100  # por encima del valor crítico (0.571); 100 deja margen
N_TIENDA = 20
GEN_TIENDA = 50


def usar_datos_tienda():
    """Cambia los datos y parámetros globales por los del comerciante."""
    global LOTES, P, LAMBDA, N, GEN, L, PM
    LOTES = LOTES_TIENDA
    P = P_TIENDA
    LAMBDA = LAMBDA_TIENDA
    N = N_TIENDA
    GEN = GEN_TIENDA
    L = len(LOTES)
    PM = 1/L



# 2. FUNCIONES DEL AGS

def costo_ganancia(x):
    """Suma el costo y la ganancia de los lotes cuyo bit vale 1."""
    costo = 0
    ganancia = 0
    for j in range(L):
        if x[j] == 1:
            costo = costo + LOTES[j][1]
            ganancia = ganancia + LOTES[j][2]
    return costo, ganancia

def aptitud(x):
    """f(x) = ganancia - LAMBDA * max(0, costo - P)"""
    costo, ganancia = costo_ganancia(x)
    exceso = max(0, costo - P)
    return ganancia - LAMBDA * exceso

def a_texto(x):
    """Convierte [1,0,1] en "101" para imprimir."""
    return "".join (str(b) for b in x)

def crear_poblacion():
    """Crear N cromosomas de L bits aleatorios."""
    poblacion = []
    for i in range(N):
        cromosoma = []
        for j in range(L):
            cromosoma.append(random.randint(0,1))
        poblacion.append(cromosoma)
    return poblacion

def emparejar(poblacion):
    """Baraja una copia de la población y forma parejas (1,2), (3,4), ..."""
    mezcla = poblacion[:]
    random.shuffle(mezcla)
    parejas = []
    for i in range(0, N, 2):
        parejas.append((mezcla[i], mezcla[i+1]))
    return parejas

def cruzar(a,b,k=None):
    """Cruce de un punto: k entre 1 y L-1.
    Si no se da k, se elige al azar (k solo se pasa en las pruebas)."""
    if k is None:
        k = random.randint(1, L -1)
    hijo1 = a[:k] + b[k:]
    hijo2 = b[:k] + a[k:]
    return hijo1,hijo2

def mutar(x):
    """Invierte cada bit con probabilidad PM. Regresa un cromosoma nuevo."""
    nuevo = []
    for bit in x:
        r = random.random()
        if r < PM:
            nuevo.append(1-bit)
        else:
            nuevo.append(bit)
    return nuevo

def eliminar(union):
    """Ordena de mayor a menor aptitud y se queda con los N mejores.
    sorted es estable: en un empate queda primero el que iba antes (los padres)."""
    ordenada = sorted(union, key=aptitud, reverse=True)
    return ordenada[:N]

def optimo_exacto():
    """Revisa todas las combinaciones y regresa la mejor que cabe en P."""
    mejor = None
    mejor_ganancia = -1
    for combinacion in itertools.product([0,1], repeat=L):
        x = list(combinacion)
        costo, ganancia = costo_ganancia(x)
        if costo <= P and ganancia > mejor_ganancia:
            mejor = x
            mejor_ganancia = ganancia
    return mejor, mejor_ganancia

def voraz():
    """Compra primero los lotes con mayor ganancia por peso invertido, mientras alcance P."""
    orden = sorted(range(L), key=lambda j: LOTES[j][2] / LOTES[j][1], reverse=True)
    x = [0] * L
    gastado = 0
    for j in orden:
        if gastado + LOTES[j][1] <= P:
            x[j] = 1
            gastado = gastado + LOTES[j][1]
    costo, ganancia = costo_ganancia(x)
    return x, ganancia



# 3. CICLO PRINCIPAL

def ags(semilla=None):
    if N % 2 != 0:
        sys.exit("Error: N debe ser par para formar parejas.")
    random.seed(semilla)
    poblacion = crear_poblacion()
    historial = []

    for g in range(1, GEN + 1):
        # 1. Emparejar, cruzar y mutar a los hijos
        hijos = []
        for a, b in emparejar(poblacion):
            h1, h2 = cruzar(a, b)
            hijos.append(mutar(h1))
            hijos.append(mutar(h2))

        # 2. Unir (padres primero) y eliminar a los peores
        union = poblacion + hijos
        poblacion = eliminar(union)

        # 3. Renumerar: la posición en la lista es el nuevo número
        aptitudes = [aptitud(x) for x in poblacion]
        promedio = sum(aptitudes) / N
        historial.append((g, aptitudes[0], promedio))
        print(f"Gen {g:3d} | mejor = {aptitudes[0]:5d} ({a_texto(poblacion[0])}) | promedio = {promedio:7.1f}")

    # Resultado
    mejor = poblacion[0]
    costo, ganancia = costo_ganancia(mejor)
    print("\nMejor surtido:", a_texto(mejor))
    for j in range(L):
        if mejor[j] == 1:
            print("  -", LOTES[j][0])
    print(f"Costo = {costo}  |  Ganancia = {ganancia}  |  Aptitud = {aptitud(mejor)}")
    print(f"Sobra del presupuesto: {P - costo}")

    return historial

def graficar(historial, archivo="convergencia.png"):
    """Guarda la gráfica de mejor aptitud y promedio por generación."""
    import matplotlib.pyplot as plt

    generaciones = [h[0] for h in historial]
    mejores = [h[1] for h in historial]
    promedios = [h[2] for h in historial]

    plt.figure(figsize=(8, 5))
    plt.plot(generaciones, mejores, marker="o", label="Mejor aptitud")
    plt.plot(generaciones, promedios, marker="o", label="Promedio")
    plt.xlabel("Generación")
    plt.ylabel("Aptitud")
    plt.title(f"Convergencia del AGS (N = {N}, {GEN} generaciones)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    if min(promedios) < 0:
        plt.ylim(0, max(mejores) * 1.15)
        plt.figtext(0.5, 0.01,
                "Promedios negativos de las primeras generaciones fuera de escala (penalización por exceder el presupuesto)",
                ha="center", fontsize=8)
    plt.savefig(archivo, dpi=150)
    print(f"\nGráfica guardada en {archivo}")



# 4. PRUEBAS DE CADA FASE
# Se ejecutan con: python3 ags_surtido.py pruebas

def prueba_1_datos():
    print("Lotes:", L, "| pm =", round(PM,3))

def prueba_2_aptitud():
    # Prueba con los individuos de la traza
    for c in ["110100","001011","100110","011001"]:
        x = [int(b) for b in c]
        print (c, "-->", costo_ganancia(x), "aptitud =", aptitud(x))

def prueba_3_poblacion():
    random.seed(1)
    poblacion = crear_poblacion()
    for i in range(N):
        x = poblacion[i]
        print(f"I{i +1} = {a_texto(x)} aptitud = {aptitud(x)}")

def prueba_4_emparejar():
    random.seed(1)
    poblacion = crear_poblacion()
    for i in range(N):
        print(f"I{i+1} = {a_texto(poblacion[i])} aptitud = {aptitud(poblacion[i])}")
    print("\nParejas:")
    for a,b in emparejar(poblacion):
        print(a_texto(a), "x", a_texto(b))

def prueba_5_cruce():
    random.seed(1)
    poblacion = crear_poblacion()
    print("Cruce:")
    for a, b in emparejar(poblacion):
        k = random.randint(1, L -1)
        h1, h2 = cruzar(a, b, k)
        print(f"Padres: {a_texto(a)} x {a_texto(b)}  |  k = {k}")
        print(f"  {a_texto(a[:k])} | {a_texto(a[k:])}")
        print(f"  {a_texto(b[:k])} | {a_texto(b[k:])}")
        print(f"Hijos:  {a_texto(h1)}  y  {a_texto(h2)}\n")

def prueba_6_mutacion():
    random.seed(1)
    poblacion = crear_poblacion()
    print("Mutación:")
    for a, b in emparejar(poblacion):
        h1, h2 = cruzar(a, b)
        for h in (h1, h2):
            m = mutar(h)
            marcas = "".join("^" if h[j] != m[j] else " " for j in range(L))
            print(f"Antes:   {a_texto(h)}")
            print(f"Después: {a_texto(m)}")
            print(f"         {marcas}\n")

def prueba_7_generacion():
    # Una generación completa: unir, eliminar y renumerar
    random.seed(1)
    poblacion = crear_poblacion()
    print("Padres:")
    for i in range(N):
        print(f"  I{i + 1} = {a_texto(poblacion[i])}  f = {aptitud(poblacion[i])}")

    hijos = []
    for a, b in emparejar(poblacion):
        h1, h2 = cruzar(a, b)
        hijos.append(mutar(h1))
        hijos.append(mutar(h2))

    print("Hijos:")
    for i in range(N):
        print(f"  H{i + 1} = {a_texto(hijos[i])}  f = {aptitud(hijos[i])}")

    union = poblacion + hijos
    poblacion = eliminar(union)

    print("Nueva población (renumerada):")
    for i in range(N):
        print(f"  I{i + 1} = {a_texto(poblacion[i])}  f = {aptitud(poblacion[i])}")

def pruebas():
    fases = [
        ("Fase 1: datos y parámetros", prueba_1_datos),
        ("Fase 2: aptitud", prueba_2_aptitud),
        ("Fase 3: población inicial", prueba_3_poblacion),
        ("Fase 4: emparejamiento", prueba_4_emparejar),
        ("Fase 5: cruce de un punto", prueba_5_cruce),
        ("Fase 6: mutación", prueba_6_mutacion),
        ("Fase 7: unir, eliminar y renumerar", prueba_7_generacion),
    ]
    for titulo, prueba in fases:
        print("=" * 50)
        print(titulo)
        print("=" * 50)
        prueba()
        print()



# 5. EJECUCIÓN

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "pruebas":
        pruebas()
    elif len(sys.argv) > 1 and sys.argv[1] == "grafica":
        historial = ags(semilla=1)
        graficar(historial)
    elif len(sys.argv) > 1 and sys.argv[1] == "tienda":
        usar_datos_tienda()
        historial = ags(semilla=1)
        graficar(historial, "convergencia_tienda.png")
    elif len(sys.argv) > 1 and sys.argv[1] == "validacion":
        usar_datos_tienda()
        x, g = optimo_exacto()
        print("Óptimo exacto:", a_texto(x), "| ganancia =", g)
        xv, gv = voraz()
        print("Voraz:        ", a_texto(xv), "| ganancia =", gv, f"| {100 * gv / g:.1f} % del óptimo")
    else:
        ags(semilla=1)