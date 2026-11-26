"""
Visualización dinámica del Algoritmo Genético Simple (AGS).

Muestra paso a paso cada generación de ags_surtido.py con los individuos como
nodos. No modifica el algoritmo: usa sus funciones y variables globales, y
consume el azar en el mismo orden que ags(semilla=...).

Uso:
    python visualizacion.py
"""
import random
import tkinter as tk

import ags_surtido as ags


# 1. DATOS DE CONFIGURACIÓN

# Valores del ejemplo, guardados al importar para poder volver a ellos
# después de usar_datos_tienda().
EJEMPLO = {nombre: getattr(ags, nombre)
           for nombre in ("LOTES", "P", "LAMBDA", "N", "GEN", "L", "PM")}

ETAPAS = ["Población", "Emparejamiento", "Cruce", "Mutación",
          "Unión y orden", "Eliminación", "Renumeración"]

# Colores
VERDE, VERDE_BORDE = "#c9efc9", "#2e8b2e"
ROJO, ROJO_BORDE = "#f6c9c9", "#b03030"
GRIS, GRIS_BORDE, GRIS_TEXTO = "#ececec", "#aaaaaa", "#888888"
COLOR_A = "#9ec5f8"      # bits que vienen del primer padre
COLOR_B = "#f8c78e"      # bits que vienen del segundo padre
MUTADO = "#ff6fa0"
PUNTO_CRUCE = "#d00000"
PALETA = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b",
          "#e377c2", "#17becf", "#bcbd22", "#d62728", "#7f7f7f"]


def usar_ejemplo():
    """Restaura los datos y parámetros del ejemplo de 3 prendas."""
    for nombre, valor in EJEMPLO.items():
        setattr(ags, nombre, valor)


# 2. MOTOR: reproduce la corrida de ags() y guarda cada etapa

class Simulacion:
    """Avanza una corrida del AGS etapa por etapa."""

    def __init__(self, semilla):
        random.seed(semilla)
        self.poblacion = ags.crear_poblacion()
        self.gen = 1
        self.etapa = 1
        self.historial = []      # (generación, mejor, promedio, mejor cromosoma)
        # Linaje: una columna por generación (la 0 es la población inicial).
        # Cada nodo: (cromosoma, origen); origen = None, ("padre", i) o ("hijo", i, j).
        self.linaje = [[(x, None) for x in self.poblacion]]
        self.terminada = False
        self.datos = None
        self.preparar_generacion()

    def preparar_generacion(self):
        """Calcula toda la generación con el mismo orden de azar que ags()."""
        padres = self.poblacion
        indice = {id(x): i for i, x in enumerate(padres)}
        parejas = []
        hijos = []
        for a, b in ags.emparejar(padres):
            k = random.randint(1, ags.L - 1)
            h1, h2 = ags.cruzar(a, b, k)
            m1 = ags.mutar(h1)
            m2 = ags.mutar(h2)
            parejas.append({
                "a": indice[id(a)], "b": indice[id(b)], "k": k,
                "antes": (h1, h2), "despues": (m1, m2),
                "cambios": ([j for j in range(ags.L) if h1[j] != m1[j]],
                            [j for j in range(ags.L) if h2[j] != m2[j]]),
            })
            hijos.append(m1)
            hijos.append(m2)

        union = padres + hijos
        sobrevivientes = ags.eliminar(union)
        # Orden completo de los 2N (mismo criterio y estabilidad que eliminar).
        orden = sorted(range(len(union)), key=lambda i: ags.aptitud(union[i]), reverse=True)
        if any(union[orden[i]] is not sobrevivientes[i] for i in range(ags.N)):
            raise RuntimeError("El orden mostrado no coincide con eliminar().")
        self.datos = {"padres": padres, "parejas": parejas, "hijos": hijos,
                      "union": union, "orden": orden, "sobrevivientes": sobrevivientes}

    def cerrar_generacion(self):
        """Etapa 7: la nueva población queda renumerada y se registra el historial."""
        columna = []
        for i in self.datos["orden"][:ags.N]:
            if i < ags.N:
                columna.append((self.datos["union"][i], ("padre", i)))
            else:
                pareja = self.datos["parejas"][(i - ags.N) // 2]
                columna.append((self.datos["union"][i], ("hijo", pareja["a"], pareja["b"])))
        self.linaje.append(columna)
        self.poblacion = self.datos["sobrevivientes"]
        aptitudes = [ags.aptitud(x) for x in self.poblacion]
        promedio = sum(aptitudes) / ags.N
        self.historial.append((self.gen, aptitudes[0], promedio, self.poblacion[0]))
        if self.gen == ags.GEN:
            self.terminada = True

    def siguiente(self):
        """Avanza una etapa. Regresa False si la corrida ya terminó."""
        if self.terminada:
            return False
        if self.etapa < 7:
            self.etapa += 1
            if self.etapa == 7:
                self.cerrar_generacion()
        else:
            self.gen += 1
            self.etapa = 1
            self.preparar_generacion()
        return True


# 3. INTERFAZ

class App:
    ANCHO_PANEL = 360
    GRAF_ANCHO, GRAF_ALTO = 330, 190
    GRAFO_ALTO = 130

    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Visualización del AGS - Surtido de uniformes")
        raiz.geometry("1320x800")
        self.modo = "Ejemplo (3 prendas)"
        self.reproduciendo = False
        self.trabajo = None
        self.ampliadas = {}      # nombre -> (ventana, lienzo)
        usar_ejemplo()
        self.construir_interfaz()
        self.reiniciar()

    # Construcción de la ventana

    def construir_interfaz(self):
        barra = tk.Frame(self.raiz, padx=8, pady=6)
        barra.pack(side="top", fill="x")

        tk.Label(barra, text="Datos:").pack(side="left")
        tk.Button(barra, text="Ejemplo (3 prendas)",
                  command=lambda: self.cambiar_modo("ejemplo")).pack(side="left", padx=4)
        tk.Button(barra, text="Datos de la tienda",
                  command=lambda: self.cambiar_modo("tienda")).pack(side="left", padx=4)
        tk.Label(barra, text="Semilla:").pack(side="left", padx=(16, 2))
        self.var_semilla = tk.StringVar(value="1")
        tk.Entry(barra, textvariable=self.var_semilla, width=7).pack(side="left")
        self.var_parametros = tk.StringVar()
        tk.Label(barra, textvariable=self.var_parametros, fg="#333").pack(side="left", padx=16)
        self.var_aviso = tk.StringVar()
        tk.Label(barra, textvariable=self.var_aviso, fg=ROJO_BORDE).pack(side="left")

        controles = tk.Frame(self.raiz, padx=8, pady=2)
        controles.pack(side="top", fill="x")
        self.boton_siguiente = tk.Button(controles, text="Siguiente paso", width=14, command=self.siguiente)
        self.boton_siguiente.pack(side="left", padx=4)
        self.boton_reproducir = tk.Button(controles, text="Reproducir", width=14, command=self.alternar_reproduccion)
        self.boton_reproducir.pack(side="left", padx=4)
        tk.Button(controles, text="Reiniciar", width=10, command=self.reiniciar).pack(side="left", padx=4)
        tk.Label(controles, text="Velocidad:").pack(side="left", padx=(16, 2))
        self.velocidad = tk.Scale(controles, from_=1, to=10, orient="horizontal", length=160, showvalue=False)
        self.velocidad.set(5)
        self.velocidad.pack(side="left")
        tk.Label(controles, text="lenta  <->  rápida", fg="#666").pack(side="left", padx=6)

        # Panel lateral
        panel = tk.Frame(self.raiz, width=self.ANCHO_PANEL, padx=8, pady=6)
        panel.pack(side="right", fill="y")
        panel.pack_propagate(False)

        estado = tk.LabelFrame(panel, text="Estado", padx=8, pady=4)
        estado.pack(fill="x")
        self.var_gen = tk.StringVar()
        self.var_etapa = tk.StringVar()
        self.var_mejor = tk.StringVar()
        self.var_cromosoma = tk.StringVar()
        self.var_promedio = tk.StringVar()
        for variable in (self.var_gen, self.var_etapa, self.var_mejor, self.var_cromosoma, self.var_promedio):
            tk.Label(estado, textvariable=variable, anchor="w", justify="left",
                     wraplength=self.ANCHO_PANEL - 40).pack(fill="x")

        grafica = tk.LabelFrame(panel, text="Convergencia", padx=4, pady=4)
        grafica.pack(fill="x", pady=8)
        self.grafica = tk.Canvas(grafica, width=self.GRAF_ANCHO, height=self.GRAF_ALTO,
                                 bg="white", highlightthickness=0)
        self.grafica.pack()
        tk.Button(grafica, text="Ampliar", command=lambda: self.ampliar("grafica")).pack(anchor="e")
        self.var_nota_grafica = tk.StringVar()
        tk.Label(grafica, textvariable=self.var_nota_grafica, fg="#666", font=("Segoe UI", 8),
                 wraplength=self.ANCHO_PANEL - 40, justify="left").pack(fill="x")

        linaje = tk.LabelFrame(panel, text="Linaje de las generaciones", padx=4, pady=4)
        linaje.pack(fill="x", pady=(0, 8))
        self.grafo = tk.Canvas(linaje, width=self.GRAF_ANCHO, height=self.GRAFO_ALTO,
                               bg="white", highlightthickness=0)
        self.grafo.pack()
        tk.Button(linaje, text="Ampliar", command=lambda: self.ampliar("grafo")).pack(anchor="e")
        tk.Label(linaje, text="Columna = generación; nodo = sobreviviente (arriba el mejor). "
                              "Gris: pasó como padre. Naranja: hijo y sus padres.",
                 fg="#666", font=("Segoe UI", 8), wraplength=self.ANCHO_PANEL - 40,
                 justify="left").pack(fill="x")

        resultado = tk.LabelFrame(panel, text="Mejor surtido", padx=8, pady=4)
        resultado.pack(fill="both", expand=True)
        self.var_resultado = tk.StringVar()
        tk.Label(resultado, textvariable=self.var_resultado, anchor="nw", justify="left",
                 wraplength=self.ANCHO_PANEL - 40).pack(fill="both", expand=True)

        # Lienzo principal con barras de desplazamiento
        zona = tk.Frame(self.raiz)
        zona.pack(side="left", fill="both", expand=True)
        zona.rowconfigure(0, weight=1)
        zona.columnconfigure(0, weight=1)
        self.lienzo = tk.Canvas(zona, bg="#fbfbfb", highlightthickness=0)
        barra_y = tk.Scrollbar(zona, orient="vertical", command=self.lienzo.yview)
        barra_x = tk.Scrollbar(zona, orient="horizontal", command=self.lienzo.xview)
        self.lienzo.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        self.lienzo.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        self.lienzo.bind("<MouseWheel>", lambda e: self.lienzo.yview_scroll(int(-e.delta / 120), "units"))
        self.lienzo.bind("<Shift-MouseWheel>", lambda e: self.lienzo.xview_scroll(int(-e.delta / 120), "units"))

    # Control

    def cambiar_modo(self, modo):
        if modo == "tienda":
            ags.usar_datos_tienda()
            self.modo = "Datos de la tienda"
        else:
            usar_ejemplo()
            self.modo = "Ejemplo (3 prendas)"
        self.reiniciar()

    def leer_semilla(self):
        try:
            semilla = int(self.var_semilla.get())
            self.var_aviso.set("")
        except ValueError:
            semilla = 1
            self.var_semilla.set("1")
            self.var_aviso.set("Semilla no válida: se usó 1")
        return semilla

    def reiniciar(self):
        self.pausar()
        semilla = self.leer_semilla()
        self.var_parametros.set(
            f"{self.modo}  |  N = {ags.N}  |  {ags.GEN} generaciones  |  P = {ags.P}  |  λ = {ags.LAMBDA}")
        self.celda = 22 if ags.L <= 6 else 16
        self.ancho_nodo = max(150, ags.L * self.celda + 16)
        self.alto_nodo = self.celda + 46
        self.sim = Simulacion(semilla)
        self.refrescar()

    def siguiente(self):
        if self.sim.siguiente():
            self.refrescar()
        if self.sim.terminada:
            self.pausar()

    def retraso(self):
        return int(2400 / self.velocidad.get())

    def alternar_reproduccion(self):
        if self.reproduciendo:
            self.pausar()
        elif not self.sim.terminada:
            self.reproduciendo = True
            self.boton_reproducir.config(text="Pausa")
            self.paso_automatico()

    def paso_automatico(self):
        if not self.reproduciendo:
            return
        self.siguiente()
        if self.reproduciendo:
            self.trabajo = self.raiz.after(self.retraso(), self.paso_automatico)

    def pausar(self):
        self.reproduciendo = False
        if self.trabajo is not None:
            self.raiz.after_cancel(self.trabajo)
            self.trabajo = None
        self.boton_reproducir.config(text="Reproducir")

    def refrescar(self):
        self.dibujar()
        self.actualizar_panel()
        estado = "disabled" if self.sim.terminada else "normal"
        self.boton_siguiente.config(state=estado)
        self.boton_reproducir.config(state=estado)

    # Panel lateral

    def actualizar_panel(self):
        sim = self.sim
        self.var_gen.set(f"Generación: {sim.gen} de {ags.GEN}")
        self.var_etapa.set(f"Etapa {sim.etapa} de 7: {ETAPAS[sim.etapa - 1]}")
        if sim.historial:
            g, mejor, promedio, cromosoma = sim.historial[-1]
            self.var_mejor.set(f"Mejor aptitud (gen. {g}): {mejor}")
            self.var_cromosoma.set(f"Mejor cromosoma: {ags.a_texto(cromosoma)}")
            self.var_promedio.set(f"Promedio (gen. {g}): {promedio:.1f}")
        else:
            self.var_mejor.set("Mejor aptitud: -")
            self.var_cromosoma.set("Mejor cromosoma: -")
            self.var_promedio.set("Promedio: -")
        self.dibujar_grafica()
        self.dibujar_grafo()
        self.redibujar_ampliadas()
        self.actualizar_resultado()

    # Ventanas ampliadas (convergencia y linaje)

    def ampliar(self, nombre):
        """Abre (o trae al frente) una ventana grande con la gráfica o el grafo."""
        if nombre in self.ampliadas:
            self.ampliadas[nombre][0].lift()
            return
        titulos = {"grafica": "Convergencia", "grafo": "Linaje de las generaciones"}
        ventana = tk.Toplevel(self.raiz)
        ventana.title(titulos[nombre])
        ventana.geometry("980x600")
        lienzo = tk.Canvas(ventana, bg="white", highlightthickness=0)
        lienzo.pack(fill="both", expand=True)
        self.ampliadas[nombre] = (ventana, lienzo)
        lienzo.bind("<Configure>", lambda e: self.redibujar_ampliadas())
        ventana.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ampliada(nombre))

    def cerrar_ampliada(self, nombre):
        ventana, _ = self.ampliadas.pop(nombre)
        ventana.destroy()

    def redibujar_ampliadas(self):
        for nombre, (_, lienzo) in self.ampliadas.items():
            ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
            if ancho < 50 or alto < 50:
                continue
            if nombre == "grafica":
                self.dibujar_grafica(lienzo, ancho, alto)
            else:
                self.dibujar_grafo(lienzo, ancho, alto)

    def actualizar_resultado(self):
        if not self.sim.terminada:
            self.var_resultado.set("Se muestra al terminar las generaciones.")
            return
        mejor = self.sim.poblacion[0]
        costo, ganancia = ags.costo_ganancia(mejor)
        lineas = [f"Cromosoma: {ags.a_texto(mejor)}", "Lotes comprados:"]
        lineas += [f"  - {ags.LOTES[j][0]}" for j in range(ags.L) if mejor[j] == 1]
        lineas += [f"Costo: {costo}", f"Ganancia: {ganancia}",
                   f"Sobrante del presupuesto: {ags.P - costo}"]
        if costo > ags.P:
            lineas.append("Aviso: el surtido excede el presupuesto.")
        self.var_resultado.set("\n".join(lineas))

    def dibujar_grafica(self, g=None, ancho_total=None, alto_total=None):
        g = g or self.grafica
        ancho_total = ancho_total or self.GRAF_ANCHO
        alto_total = alto_total or self.GRAF_ALTO
        g.delete("all")
        ml, mr, mt, mb = 52, 12, 24, 26
        ancho = ancho_total - ml - mr
        alto = alto_total - mt - mb
        g.create_rectangle(ml, mt, ml + ancho, mt + alto, outline="#999")
        g.create_text(ml, 4, text="Mejor", fill="#1f77b4", anchor="nw", font=("Segoe UI", 9, "bold"))
        g.create_text(ml + 60, 4, text="Promedio", fill="#ff7f0e", anchor="nw", font=("Segoe UI", 9, "bold"))
        historial = self.sim.historial
        if not historial:
            g.create_text(ml + ancho / 2, mt + alto / 2, text="Sin datos", fill="#999")
            self.var_nota_grafica.set("")
            return

        mejores = [h[1] for h in historial]
        promedios = [h[2] for h in historial]
        if min(promedios) < 0:
            ymin, ymax = 0, max(mejores) * 1.15
            self.var_nota_grafica.set("Promedios negativos fuera de escala (el eje empieza en 0).")
        else:
            ymin, ymax = min(promedios + mejores), max(promedios + mejores)
            margen = (ymax - ymin) * 0.08 or 1
            ymin, ymax = ymin - margen, ymax + margen
            self.var_nota_grafica.set("")
        if ymax <= ymin:
            ymax = ymin + 1

        def px(gen):
            return ml + (gen - 1) / max(ags.GEN - 1, 1) * ancho

        def py(valor):
            valor = max(valor, ymin)
            return mt + (ymax - valor) / (ymax - ymin) * alto

        for i in range(4):
            valor = ymin + (ymax - ymin) * i / 3
            y = py(valor)
            g.create_line(ml, y, ml + ancho, y, fill="#eee")
            g.create_text(ml - 4, y, text=f"{valor:.0f}", anchor="e", font=("Segoe UI", 8))
        for gen in sorted({1, (ags.GEN + 1) // 2, ags.GEN}):
            g.create_text(px(gen), mt + alto + 4, text=str(gen), anchor="n", font=("Segoe UI", 8))

        for serie, color in ((mejores, "#1f77b4"), (promedios, "#ff7f0e")):
            puntos = [(px(h[0]), py(v)) for h, v in zip(historial, serie)]
            if len(puntos) > 1:
                g.create_line(*[c for p in puntos for c in p], fill=color, width=2)
            for x, y in puntos:
                g.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)

    def dibujar_grafo(self, g=None, ancho_total=None, alto_total=None):
        """Grafo de linaje: columnas = generaciones, nodos = sobrevivientes."""
        g = g or self.grafo
        ancho_total = ancho_total or self.GRAF_ANCHO
        alto_total = alto_total or self.GRAFO_ALTO
        g.delete("all")
        ml, mr, mt, mb = 12, 12, 10, 18
        ancho = ancho_total - ml - mr
        alto = alto_total - mt - mb
        tope = 5 if ancho_total <= 400 else 9

        def posicion(col, fila):
            x = ml + col / max(ags.GEN, 1) * ancho
            y = mt + fila / max(ags.N - 1, 1) * alto
            return x, y

        radio = max(2, min(tope, alto / max(ags.N - 1, 1) / 2 - 0.5, ancho / max(ags.GEN, 1) / 2 - 0.5))
        linaje = self.sim.linaje
        # Aristas primero, para que los nodos queden encima
        for col in range(1, len(linaje)):
            for fila, (_, origen) in enumerate(linaje[col]):
                x2, y2 = posicion(col, fila)
                if origen[0] == "padre":
                    x1, y1 = posicion(col - 1, origen[1])
                    g.create_line(x1, y1, x2, y2, fill="#aaaaaa")
                else:
                    for i in origen[1:]:
                        x1, y1 = posicion(col - 1, i)
                        g.create_line(x1, y1, x2, y2, fill="#f0a030")
        for col, nodos in enumerate(linaje):
            for fila, (cromosoma, _) in enumerate(nodos):
                x, y = posicion(col, fila)
                cabe = ags.costo_ganancia(cromosoma)[0] <= ags.P
                mejor = fila == 0
                g.create_oval(x - radio, y - radio, x + radio, y + radio,
                              fill=VERDE_BORDE if cabe else ROJO_BORDE,
                              outline="#1f77b4" if mejor else "white", width=2 if mejor else 1)
        for col in sorted({0, ags.GEN // 2, ags.GEN}):
            x, _ = posicion(col, 0)
            g.create_text(x, alto_total - 3, text=str(col), anchor="s", font=("Segoe UI", 8))

    # Dibujo de elementos básicos

    def texto(self, x, y, contenido, **opciones):
        opciones.setdefault("anchor", "nw")
        opciones.setdefault("font", ("Segoe UI", 10))
        return self.lienzo.create_text(x, y, text=contenido, **opciones)

    def rect_redondeado(self, x1, y1, x2, y2, r=10, **opciones):
        puntos = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
                  x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.lienzo.create_polygon(puntos, smooth=True, **opciones)

    def bits(self, x, y, cromosoma, colores=None, resaltar=(), tenue=False):
        """Dibuja un cromosoma como celdas de un bit cada una."""
        c = self.celda
        fuente = ("Consolas", 10 if c > 16 else 9, "bold")
        for j, bit in enumerate(cromosoma):
            relleno = colores[j] if colores else "#ffffff"
            borde = "#555555"
            grosor = 1
            if j in resaltar:
                borde, grosor = PUNTO_CRUCE, 3
            if tenue:
                relleno, borde = "#f4f4f4", GRIS_BORDE
            self.lienzo.create_rectangle(x + j * c, y, x + (j + 1) * c, y + c,
                                         fill=relleno, outline=borde, width=grosor)
            self.texto(x + j * c + c / 2, y + c / 2, str(bit), anchor="center", font=fuente,
                       fill=GRIS_TEXTO if tenue else "black")

    def nodo(self, x, y, etiqueta, cromosoma, nota=""):
        """Nodo de un individuo: verde si su costo cabe en P, rojo si se pasa."""
        costo, _ = ags.costo_ganancia(cromosoma)
        cabe = costo <= ags.P
        w, h = self.ancho_nodo, self.alto_nodo
        self.rect_redondeado(x, y, x + w, y + h, fill=VERDE if cabe else ROJO,
                             outline=VERDE_BORDE if cabe else ROJO_BORDE, width=2)
        self.texto(x + 8, y + 5, etiqueta, font=("Segoe UI", 10, "bold"))
        if nota:
            self.texto(x + w - 8, y + 6, nota, anchor="ne", font=("Segoe UI", 8), fill="#555")
        self.bits(x + (w - ags.L * self.celda) / 2, y + 24, cromosoma)
        self.texto(x + w / 2, y + self.celda + 28, f"f = {ags.aptitud(cromosoma)}   costo = {costo}",
                   anchor="n", font=("Segoe UI", 9))

    def fila_bits(self, x, y, etiqueta, cromosoma, colores, resaltar=()):
        self.texto(x, y + self.celda / 2, etiqueta, anchor="w", font=("Segoe UI", 9, "bold"))
        self.bits(x + 46, y, cromosoma, colores, resaltar)

    def leyenda(self, y, elementos):
        x = 14
        for color, texto in elementos:
            self.lienzo.create_rectangle(x, y + 2, x + 14, y + 16, fill=color, outline="#555")
            self.texto(x + 20, y, texto, font=("Segoe UI", 9))
            x += 40 + len(texto) * 6

    def posicion(self, i, columnas, y0):
        x = 14 + (i % columnas) * (self.ancho_nodo + 22)
        y = y0 + (i // columnas) * (self.alto_nodo + 18)
        return x, y

    def colores_hijos(self, k):
        """Colores por origen: cabeza y cola de cada hijo según el padre."""
        n = ags.L
        return ([COLOR_A] * k + [COLOR_B] * (n - k), [COLOR_B] * k + [COLOR_A] * (n - k))

    # Dibujo de cada etapa

    def dibujar(self):
        self.lienzo.delete("all")
        sim = self.sim
        self.texto(14, 8, f"Generación {sim.gen}  -  Etapa {sim.etapa}: {ETAPAS[sim.etapa - 1]}",
                   font=("Segoe UI", 13, "bold"))
        if sim.terminada:
            self.texto(420, 10, "Corrida terminada", font=("Segoe UI", 10, "bold"), fill=VERDE_BORDE)
        dibujar_etapa = [self.etapa_poblacion, self.etapa_emparejamiento, self.etapa_cruce,
                         self.etapa_mutacion, self.etapa_union, self.etapa_eliminacion,
                         self.etapa_renumeracion][sim.etapa - 1]
        dibujar_etapa(44)
        region = self.lienzo.bbox("all")
        self.lienzo.configure(scrollregion=(0, 0, region[2] + 20, region[3] + 20))
        self.lienzo.xview_moveto(0)
        self.lienzo.yview_moveto(0)

    def etapa_poblacion(self, y0):
        self.leyenda(y0, [(VERDE, "costo <= P"), (ROJO, "costo > P")])
        columnas = ags.N if ags.N <= 6 else 5
        for i, x in enumerate(self.sim.datos["padres"]):
            px, py = self.posicion(i, columnas, y0 + 30)
            self.nodo(px, py, f"I{i + 1}", x)

    def etapa_emparejamiento(self, y0):
        datos = self.sim.datos
        parejas = datos["parejas"]
        columnas = min(len(parejas), 2)
        enlace = 80
        ancho_bloque = 2 * self.ancho_nodo + enlace
        for p, pareja in enumerate(parejas):
            bx = 14 + (p % columnas) * (ancho_bloque + 30)
            by = y0 + (p // columnas) * (self.alto_nodo + 26)
            color = PALETA[p % len(PALETA)]
            medio = by + self.alto_nodo / 2
            self.lienzo.create_line(bx + self.ancho_nodo, medio, bx + self.ancho_nodo + enlace, medio,
                                    width=4, fill=color)
            self.texto(bx + self.ancho_nodo + enlace / 2, medio - 6, f"Pareja {p + 1}", anchor="s",
                       font=("Segoe UI", 9, "bold"), fill=color)
            self.nodo(bx, by, f"I{pareja['a'] + 1}", datos["padres"][pareja["a"]])
            self.nodo(bx + self.ancho_nodo + enlace, by, f"I{pareja['b'] + 1}", datos["padres"][pareja["b"]])

    def bloques(self, y0, alto_bloque, ancho_bloque):
        """Posiciones (x, y) de un bloque por pareja en una cuadrícula."""
        n = len(self.sim.datos["parejas"])
        columnas = min(n, 3)
        return [(14 + (p % columnas) * (ancho_bloque + 24), y0 + (p // columnas) * (alto_bloque + 14))
                for p in range(n)]

    def etapa_cruce(self, y0):
        self.leyenda(y0, [(COLOR_A, "primer padre"), (COLOR_B, "segundo padre"),
                          (PUNTO_CRUCE, "punto de cruce k")])
        datos = self.sim.datos
        c = self.celda
        rh = c + 6
        ancho_bloque = 46 + ags.L * c + 30
        alto_bloque = 20 + 4 * rh + 8 + 8
        posiciones = self.bloques(y0 + 30, alto_bloque, ancho_bloque)
        for p, (pareja, (bx, by)) in enumerate(zip(datos["parejas"], posiciones)):
            k = pareja["k"]
            a, b = datos["padres"][pareja["a"]], datos["padres"][pareja["b"]]
            self.texto(bx, by, f"Pareja {p + 1}:  I{pareja['a'] + 1} x I{pareja['b'] + 1}   (k = {k})",
                       font=("Segoe UI", 9, "bold"))
            ry = by + 20
            col_h1, col_h2 = self.colores_hijos(k)
            self.fila_bits(bx, ry, f"I{pareja['a'] + 1}", a, [COLOR_A] * ags.L)
            self.fila_bits(bx, ry + rh, f"I{pareja['b'] + 1}", b, [COLOR_B] * ags.L)
            self.fila_bits(bx, ry + 2 * rh + 8, f"H{2 * p + 1}", pareja["antes"][0], col_h1)
            self.fila_bits(bx, ry + 3 * rh + 8, f"H{2 * p + 2}", pareja["antes"][1], col_h2)
            xk = bx + 46 + k * c
            self.lienzo.create_line(xk, ry - 3, xk, ry + 4 * rh + 8 + 1, fill=PUNTO_CRUCE, width=3)

    def etapa_mutacion(self, y0):
        datos = self.sim.datos
        total = sum(len(cs) for pareja in datos["parejas"] for cs in pareja["cambios"])
        self.leyenda(y0, [(MUTADO, "bit mutado")])
        resumen = (f"Bits mutados en esta generación: {total}" if total
                   else "Ningún bit mutó en esta generación")
        self.texto(190, y0, resumen, font=("Segoe UI", 9))
        c = self.celda
        rh = c + 6
        ancho_bloque = 46 + ags.L * c + 30
        alto_bloque = 20 + 2 * (rh + 18) + 4
        posiciones = self.bloques(y0 + 30, alto_bloque, ancho_bloque)
        for p, (pareja, (bx, by)) in enumerate(zip(datos["parejas"], posiciones)):
            self.texto(bx, by, f"Pareja {p + 1}", font=("Segoe UI", 9, "bold"))
            origen = self.colores_hijos(pareja["k"])
            for n in range(2):
                antes, despues = pareja["antes"][n], pareja["despues"][n]
                cambios = pareja["cambios"][n]
                colores = list(origen[n])
                for j in cambios:
                    colores[j] = MUTADO
                ry = by + 20 + n * (rh + 18)
                self.fila_bits(bx, ry, f"H{2 * p + n + 1}", despues, colores, resaltar=cambios)
                if cambios:
                    nota = "muta " + ", ".join(f"bit {j + 1} ({antes[j]}→{despues[j]})" for j in cambios)
                else:
                    nota = "sin mutación"
                self.texto(bx + 46, ry + c + 1, f"{nota}  |  f = {ags.aptitud(despues)}",
                           font=("Segoe UI", 8), fill="#444")

    def columna(self, y0, eliminando):
        """Los 2N individuos ordenados de mayor a menor aptitud."""
        datos = self.sim.datos
        c = self.celda
        rh = c + 8
        ancho_tabla = 90 + ags.L * c + 230
        if eliminando:
            self.texto(14, y0, f"Se eliminan los {ags.N} peores; se conservan los {ags.N} mejores.",
                       font=("Segoe UI", 9))
        else:
            self.texto(14, y0, "Mayor a menor aptitud. En un empate, los padres van antes que los hijos.",
                       font=("Segoe UI", 9))
        y0 += 26
        for pos, i in enumerate(datos["orden"]):
            x = 14
            y = y0 + pos * rh
            cromosoma = datos["union"][i]
            costo, _ = ags.costo_ganancia(cromosoma)
            descartado = eliminando and pos >= ags.N
            if descartado:
                relleno, borde, tinta = GRIS, GRIS_BORDE, GRIS_TEXTO
            elif costo <= ags.P:
                relleno, borde, tinta = VERDE, VERDE_BORDE, "black"
            else:
                relleno, borde, tinta = ROJO, ROJO_BORDE, "black"
            self.lienzo.create_rectangle(x, y, x + ancho_tabla, y + rh - 3, fill=relleno, outline=borde)
            self.texto(x + 34, y + (rh - 3) / 2, f"#{pos + 1}", anchor="e", fill=tinta, font=("Segoe UI", 9))
            es_padre = i < ags.N
            etiqueta = f"I{i + 1}" if es_padre else f"H{i - ags.N + 1}"
            self.texto(x + 42, y + (rh - 3) / 2, etiqueta, anchor="w", fill=tinta, font=("Segoe UI", 9, "bold"))
            self.bits(x + 80, y + 2, cromosoma, tenue=descartado)
            xf = x + 80 + ags.L * c + 12
            self.texto(xf, y + (rh - 3) / 2, f"f = {ags.aptitud(cromosoma)}", anchor="w", fill=tinta,
                       font=("Segoe UI", 9))
            rol = "padre" if es_padre else "hijo"
            if eliminando:
                rol += "  -  se elimina" if descartado else "  -  se queda"
            self.texto(xf + 90, y + (rh - 3) / 2, rol, anchor="w", fill=tinta, font=("Segoe UI", 9))
            if descartado:
                self.lienzo.create_line(x + 4, y + (rh - 3) / 2, x + ancho_tabla - 4, y + (rh - 3) / 2,
                                        fill="#777", width=2)
        if eliminando:
            ycorte = y0 + ags.N * rh - 2
            self.lienzo.create_line(8, ycorte, ancho_tabla + 20, ycorte, fill=PUNTO_CRUCE, width=3, dash=(8, 4))

    def etapa_union(self, y0):
        self.columna(y0, eliminando=False)

    def etapa_eliminacion(self, y0):
        self.columna(y0, eliminando=True)

    def etapa_renumeracion(self, y0):
        datos = self.sim.datos
        self.texto(14, y0, "Los sobrevivientes son I1..IN de la siguiente generación (se indica su origen).",
                   font=("Segoe UI", 9))
        columnas = ags.N if ags.N <= 6 else 5
        for pos, i in enumerate(datos["orden"][:ags.N]):
            origen = f"I{i + 1}" if i < ags.N else f"H{i - ags.N + 1}"
            px, py = self.posicion(pos, columnas, y0 + 28)
            self.nodo(px, py, f"I{pos + 1}", datos["union"][i], nota=f"antes: {origen}")


# 4. EJECUCIÓN

def main():
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
