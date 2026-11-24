import random
import sys

# 1. DATOS DEL PROBLEMA Y PARÁMETROS

# Datos del problema: un lote por bit 
# (nombre, costo C, ganancia G)

LOTES = [
    ("Camisa menudeo", 2700, 1800),
    ("Camisa mayoreo", 3600, 1200),
    ("Pantalon menudeo", 2800, 1800),
    ("Pantalon mayoreo", 2800, 1000),
    ("Sudadera menudeo", 900, 600),
    ("Sudadera mayoreo", 1800, 700),
]

P = 7000 # presupuesto
LAMBDA = 1 # factor de penalización

# Parámetros
N = 4          # tamaño población  
GEN = 10       # número de generaciones  
L = len(LOTES) # longitud del cromosoma
PM = 1/L       # probabilidad de mutación por bit



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



# 3. CICLO PRINCIPAL
def ags(semilla=None):
    random.seed(semilla)
    poblacion = crear_poblacion()

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



# 4. PRUEBAS DE CADA FASE
# Se ejecutan con: python3 ags_surtido.py prueba

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
    else:
        ags(semilla=1)
