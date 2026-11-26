import random
import math
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# Se importa el módulo completo para poder asignar sus variables globales
import ags_surtido as ags

# Colores de la gráfica y del texto de advertencia
COLOR_MEJOR = "#1f6feb"
COLOR_PROMEDIO = "#e8590c"
COLOR_ERROR = "#c92a2a"

# Conjuntos de datos que se pueden cargar. Se leen de ags_surtido al importar,
# antes de que configurar_modelo cambie sus variables globales.
EJEMPLO = {"lotes": list(ags.LOTES), "P": ags.P, "lambda": ags.LAMBDA,
           "N": ags.N, "GEN": ags.GEN, "semilla": 1}
TIENDA = {"lotes": list(ags.LOTES_TIENDA), "P": ags.P_TIENDA, "lambda": ags.LAMBDA_TIENDA,
          "N": ags.N_TIENDA, "GEN": ags.GEN_TIENDA, "semilla": 1}


# 1. LECTURA Y VALIDACIÓN DE DATOS

def leer_entero(texto, nombre, minimo=None):
    """Convierte el texto a entero o lanza ValueError con un mensaje claro."""
    try:
        valor = int(texto.strip())
    except ValueError:
        raise ValueError(f"{nombre} debe ser un número entero.")
    if minimo is not None and valor < minimo:
        raise ValueError(f"{nombre} debe ser mayor o igual a {minimo}.")
    return valor


def leer_lotes(filas):
    """Convierte las filas de la tabla en una lista de (nombre, costo, ganancia)."""
    lotes = []
    for i, (nombre, costo, ganancia) in enumerate(filas, start=1):
        if not nombre.strip():
            raise ValueError(f"El lote {i} no tiene nombre.")
        c = leer_entero(costo, f"El costo del lote {i}", 0)
        g = leer_entero(ganancia, f"La ganancia del lote {i}", 0)
        lotes.append((nombre.strip(), c, g))
    if len(lotes) < 2:
        raise ValueError("Se necesitan al menos 2 lotes para poder cruzar.")
    return lotes


def leer_parametros(campos):
    """Valida los campos de parámetros y los regresa en un diccionario."""
    try:
        lam = float(campos["lambda"].strip())
    except ValueError:
        raise ValueError("Lambda debe ser un número.")
    if lam < 0:
        raise ValueError("Lambda debe ser mayor o igual a 0.")
    if lam == int(lam):
        lam = int(lam)

    n = leer_entero(campos["N"], "N")
    if n <= 0 or n % 2 != 0:
        raise ValueError("N debe ser par y mayor que 0 (se forman parejas).")

    texto_semilla = campos["semilla"].strip()
    semilla = leer_entero(texto_semilla, "La semilla") if texto_semilla else None

    return {
        "P": leer_entero(campos["P"], "El presupuesto P", 0),
        "LAMBDA": lam,
        "N": n,
        "GEN": leer_entero(campos["GEN"], "Las generaciones", 1),
        "semilla": semilla,
    }


# 2. CONEXIÓN CON ags_surtido.py

def configurar_modelo(lotes, parametros):
    """Asigna los globales del módulo y recalcula L y PM."""
    ags.LOTES = lotes
    ags.L = len(lotes)
    ags.PM = 1 / ags.L
    ags.P = parametros["P"]
    ags.LAMBDA = parametros["LAMBDA"]
    ags.N = parametros["N"]
    ags.GEN = parametros["GEN"]


def ejecutar_ags(semilla):
    """Mismo ciclo de ags(), pero guarda el historial en lugar de imprimir."""
    random.seed(semilla)
    poblacion = ags.crear_poblacion()
    historial = []

    for g in range(1, ags.GEN + 1):
        # Emparejar, cruzar y mutar a los hijos
        hijos = []
        for a, b in ags.emparejar(poblacion):
            h1, h2 = ags.cruzar(a, b)
            hijos.append(ags.mutar(h1))
            hijos.append(ags.mutar(h2))

        # Unir (padres primero) y eliminar a los peores
        union = poblacion + hijos
        poblacion = ags.eliminar(union)

        # Renumerar y guardar los datos de la generación
        aptitudes = [ags.aptitud(x) for x in poblacion]
        historial.append({
            "gen": g,
            "mejor": aptitudes[0],
            "promedio": sum(aptitudes) / ags.N,
            "cromosoma": poblacion[0],
        })
    return historial


# 3. AUXILIARES DE LA GRÁFICA

PASOS_VERTICAL = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
PASOS_HORIZONTAL = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000]


def marcas_verticales(minimo, maximo):
    """Regresa las marcas redondas del eje vertical, con un paso de margen arriba y abajo."""
    paso = PASOS_VERTICAL[-1]
    for candidato in PASOS_VERTICAL:
        if (maximo - minimo) / candidato <= 6:
            paso = candidato
            break
    inferior = math.floor(minimo / paso) * paso
    superior = math.ceil(maximo / paso) * paso
    # Margen: si los datos tocan un borde, se agrega un paso más
    if minimo - inferior < paso * 0.15:
        inferior -= paso
    if superior - maximo < paso * 0.15:
        superior += paso
    return list(range(inferior, superior + 1, paso))


def paso_horizontal(total, ancho):
    """Elige cada cuántas generaciones se escribe una etiqueta sin que se encimen."""
    maximo_etiquetas = max(2, ancho // 45)
    for paso in PASOS_HORIZONTAL:
        if total / paso <= maximo_etiquetas:
            return paso
    return PASOS_HORIZONTAL[-1]


# 4. INTERFAZ

class Interfaz:
    def __init__(self, raiz):
        self.raiz = raiz
        self.historial = []
        raiz.title("AGS - Surtido de tienda de uniformes")
        raiz.geometry("1280x800")
        raiz.minsize(1000, 650)
        self.crear_panel_izquierdo()
        self.crear_panel_derecho()
        self.cargar_lotes_iniciales()

    # Construcción de la ventana

    def crear_panel_izquierdo(self):
        """Tabla de lotes, parámetros y botón Ejecutar."""
        marco = ttk.Frame(self.raiz, padding=8)
        marco.pack(side="left", fill="y")

        ttk.Label(marco, text="Lotes de mercancía (doble clic para editar)").pack(anchor="w")
        cuadro_lotes = ttk.Frame(marco)
        cuadro_lotes.pack(fill="x", pady=4)
        self.tabla_lotes = ttk.Treeview(
            cuadro_lotes, columns=("nombre", "costo", "ganancia"), show="headings", height=9)
        for col, texto, ancho in (("nombre", "Nombre", 150),
                                  ("costo", "Costo", 70),
                                  ("ganancia", "Ganancia", 70)):
            self.tabla_lotes.heading(col, text=texto)
            self.tabla_lotes.column(col, width=ancho, stretch=False,
                                    anchor="w" if col == "nombre" else "e")
        # Si la tabla no cabe en el panel, la barra horizontal evita recortar los nombres
        barra_lotes = ttk.Scrollbar(cuadro_lotes, orient="horizontal",
                                    command=self.tabla_lotes.xview)
        self.tabla_lotes.configure(xscrollcommand=barra_lotes.set)
        cuadro_lotes.columnconfigure(0, weight=1)
        self.tabla_lotes.grid(row=0, column=0, sticky="ew")
        barra_lotes.grid(row=1, column=0, sticky="ew")
        # Este espaciador le pide al panel el ancho de las tres columnas (el Treeview no lo hace)
        self.espaciador = tk.Frame(cuadro_lotes, height=0)
        self.espaciador.grid(row=2, column=0, sticky="w")
        self.tabla_lotes.bind("<Double-1>", self.editar_celda)

        botones = ttk.Frame(marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Agregar lote", command=self.agregar_lote).pack(side="left")
        ttk.Button(botones, text="Quitar lote", command=self.quitar_lote).pack(side="left", padx=6)
        ttk.Button(marco, text="Cargar ejemplo (3 prendas)",
                   command=lambda: self.cargar_datos(EJEMPLO)).pack(fill="x", pady=(6, 0))
        ttk.Button(marco, text="Cargar datos de la tienda",
                   command=lambda: self.cargar_datos(TIENDA)).pack(fill="x", pady=(4, 0))

        self.crear_campos_parametros(marco)

        ttk.Button(marco, text="Ejecutar", command=self.ejecutar).pack(fill="x", pady=(12, 4))
        self.mensaje = tk.Label(marco, text="", fg=COLOR_ERROR, wraplength=300, justify="left")
        self.mensaje.pack(fill="x")

        self.crear_panel_mejor(marco)

    def crear_panel_mejor(self, marco):
        """Panel de texto con el mejor surtido, con una sola familia de letra."""
        ttk.Label(marco, text="Mejor surtido").pack(anchor="w", pady=(8, 0))
        normal = tkfont.nametofont("TkDefaultFont")
        negrita = normal.copy()
        negrita.configure(weight="bold")
        self.fuente_negrita = negrita  # se guarda para que no se libere
        self.panel_mejor = tk.Text(marco, width=34, height=6, state="disabled", wrap="word",
                                   font=normal, relief="solid", bd=1)
        self.panel_mejor.tag_configure("rojo", foreground=COLOR_ERROR)
        self.panel_mejor.tag_configure("negrita", font=negrita)
        self.panel_mejor.pack(fill="both", expand=True, pady=4)

    def crear_campos_parametros(self, marco):
        """Campos de texto para P, lambda, N, generaciones y semilla."""
        cuadro = ttk.LabelFrame(marco, text="Parámetros", padding=8)
        cuadro.pack(fill="x", pady=(12, 0))
        valores = (("P", "Presupuesto P", ags.P),
                   ("lambda", "Lambda", ags.LAMBDA),
                   ("N", "Tamaño de población N", ags.N),
                   ("GEN", "Generaciones", ags.GEN),
                   ("semilla", "Semilla (vacía = aleatoria)", 1))
        self.campos = {}
        for fila, (clave, texto, inicial) in enumerate(valores):
            ttk.Label(cuadro, text=texto).grid(row=fila, column=0, sticky="w", pady=2)
            variable = tk.StringVar(value=str(inicial))
            ttk.Entry(cuadro, textvariable=variable, width=10).grid(
                row=fila, column=1, padx=(8, 0), pady=2)
            self.campos[clave] = variable

    def crear_panel_derecho(self):
        """Tabla de resultados (40 % de la altura) y gráfica (60 %)."""
        marco = ttk.Frame(self.raiz, padding=8)
        marco.pack(side="left", fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=4, uniform="alto")
        marco.rowconfigure(1, weight=6, uniform="alto")

        arriba = ttk.Frame(marco)
        arriba.grid(row=0, column=0, sticky="nsew")
        ttk.Label(arriba, text="Resultados por generación").pack(anchor="w")
        cuadro = ttk.Frame(arriba)
        cuadro.pack(fill="both", expand=True, pady=4)
        self.tabla_resultados = ttk.Treeview(
            cuadro, columns=("gen", "mejor", "cromosoma", "promedio"),
            show="headings", height=3)
        for col, texto in (("gen", "Generación"), ("mejor", "Mejor aptitud"),
                           ("cromosoma", "Mejor cromosoma"), ("promedio", "Promedio")):
            self.tabla_resultados.heading(col, text=texto)
            self.tabla_resultados.column(col, anchor="center", stretch=True)
        self.ajustar_columnas()
        # La tabla se estira con la ventana; las barras aparecen cuando hace falta
        barra_v = ttk.Scrollbar(cuadro, orient="vertical", command=self.tabla_resultados.yview)
        barra_h = ttk.Scrollbar(cuadro, orient="horizontal", command=self.tabla_resultados.xview)
        self.tabla_resultados.configure(yscrollcommand=barra_v.set,
                                        xscrollcommand=barra_h.set)
        cuadro.columnconfigure(0, weight=1)
        cuadro.rowconfigure(0, weight=1)
        self.tabla_resultados.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")

        abajo = ttk.Frame(marco)
        abajo.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        ttk.Label(abajo, text="Convergencia").pack(anchor="w")
        self.lienzo = tk.Canvas(abajo, bg="white", height=100, highlightthickness=1,
                                highlightbackground="#bbbbbb")
        self.lienzo.pack(fill="both", expand=True, pady=4)
        self.lienzo.bind("<Configure>", lambda e: self.dibujar_grafica())

    def ajustar_columnas(self):
        """Fija el ancho mínimo de cada columna al de su encabezado y su contenido."""
        fuente = tkfont.nametofont("TkDefaultFont")
        for i, col in enumerate(self.tabla_resultados["columns"]):
            textos = [self.tabla_resultados.heading(col, "text")]
            textos += [str(self.tabla_resultados.item(f, "values")[i])
                       for f in self.tabla_resultados.get_children()]
            ancho = max(fuente.measure(t) for t in textos) + 24
            self.tabla_resultados.column(col, width=ancho, minwidth=ancho)

    # Tabla de lotes

    def cargar_lotes_iniciales(self):
        """Precarga los lotes definidos en ags_surtido.py."""
        for lote in ags.LOTES:
            self.tabla_lotes.insert("", "end", values=lote)
        self.ajustar_columna_nombre()

    def ajustar_columna_nombre(self):
        """Ensancha la columna Nombre al nombre más largo de la tabla."""
        fuente = tkfont.nametofont("TkDefaultFont")
        textos = [self.tabla_lotes.heading("nombre", "text")]
        textos += [str(self.tabla_lotes.item(f, "values")[0])
                   for f in self.tabla_lotes.get_children()]
        ancho = max(fuente.measure(t) for t in textos) + 24
        self.tabla_lotes.column("nombre", width=ancho, minwidth=ancho)
        total = sum(self.tabla_lotes.column(col, "width") for col in self.tabla_lotes["columns"])
        self.espaciador.config(width=total + 4)

    def cargar_datos(self, datos):
        """Reemplaza lotes y parámetros por un conjunto de datos y limpia los resultados."""
        self.tabla_lotes.delete(*self.tabla_lotes.get_children())
        for lote in datos["lotes"]:
            self.tabla_lotes.insert("", "end", values=lote)
        self.ajustar_columna_nombre()
        for clave, variable in self.campos.items():
            variable.set(str(datos[clave]))
        self.mensaje.config(text="")
        self.limpiar_resultados()

    def limpiar_resultados(self):
        """Vacía la tabla de resultados, la gráfica y el panel del mejor surtido."""
        self.historial = []
        self.tabla_resultados.delete(*self.tabla_resultados.get_children())
        self.ajustar_columnas()
        self.dibujar_grafica()
        self.panel_mejor.config(state="normal")
        self.panel_mejor.delete("1.0", "end")
        self.panel_mejor.config(state="disabled")

    def agregar_lote(self):
        """Agrega una fila nueva con valores por defecto."""
        fila = self.tabla_lotes.insert("", "end", values=("Lote nuevo", 0, 0))
        self.tabla_lotes.selection_set(fila)
        self.tabla_lotes.see(fila)
        self.ajustar_columna_nombre()

    def quitar_lote(self):
        """Quita las filas seleccionadas (o la última si no hay selección)."""
        seleccion = self.tabla_lotes.selection()
        if not seleccion:
            filas = self.tabla_lotes.get_children()
            seleccion = filas[-1:]
        for fila in seleccion:
            self.tabla_lotes.delete(fila)
        self.ajustar_columna_nombre()

    def editar_celda(self, evento):
        """Coloca un campo de texto sobre la celda para editarla."""
        fila = self.tabla_lotes.identify_row(evento.y)
        columna = self.tabla_lotes.identify_column(evento.x)
        if not fila or self.tabla_lotes.identify_region(evento.x, evento.y) != "cell":
            return
        indice = int(columna[1:]) - 1
        x, y, ancho, alto = self.tabla_lotes.bbox(fila, columna)
        valores = list(self.tabla_lotes.item(fila, "values"))

        campo = ttk.Entry(self.tabla_lotes)
        campo.insert(0, valores[indice])
        campo.select_range(0, "end")
        campo.place(x=x, y=y, width=ancho, height=alto)
        campo.focus_set()

        def guardar(_=None):
            valores[indice] = campo.get()
            self.tabla_lotes.item(fila, values=valores)
            campo.destroy()
            self.ajustar_columna_nombre()

        campo.bind("<Return>", guardar)
        campo.bind("<FocusOut>", guardar)
        campo.bind("<Escape>", lambda e: campo.destroy())

    def filas_de_lotes(self):
        """Regresa el contenido de la tabla de lotes como lista de tuplas de texto."""
        return [tuple(str(v) for v in self.tabla_lotes.item(f, "values"))
                for f in self.tabla_lotes.get_children()]

    # Ejecución

    def ejecutar(self):
        """Valida los datos, corre el AGS y muestra los resultados."""
        try:
            lotes = leer_lotes(self.filas_de_lotes())
            parametros = leer_parametros({k: v.get() for k, v in self.campos.items()})
        except ValueError as error:
            self.mensaje.config(text=str(error))
            return
        self.mensaje.config(text="")

        configurar_modelo(lotes, parametros)
        self.historial = ejecutar_ags(parametros["semilla"])
        self.mostrar_tabla()
        self.dibujar_grafica()
        self.mostrar_mejor()

    # Presentación de resultados

    def mostrar_tabla(self):
        """Llena la tabla con una fila por generación."""
        self.tabla_resultados.delete(*self.tabla_resultados.get_children())
        for h in self.historial:
            self.tabla_resultados.insert("", "end", values=(
                h["gen"], h["mejor"], ags.a_texto(h["cromosoma"]), f"{h['promedio']:.1f}"))
        self.ajustar_columnas()

    def dibujar_grafica(self):
        """Dibuja ejes, las dos líneas y la leyenda en el Canvas."""
        c = self.lienzo
        c.delete("all")
        if not self.historial:
            return
        ancho, alto = c.winfo_width(), c.winfo_height()
        gens = [h["gen"] for h in self.historial]
        mejores = [h["mejor"] for h in self.historial]
        promedios = [h["promedio"] for h in self.historial]

        # Si algún promedio es negativo, el eje empieza en 0 y se avisa con una nota
        fuera_de_escala = min(promedios) < 0
        izq, der, arriba, abajo = 70, 20, 15, (56 if fuera_de_escala else 40)

        # Rango vertical con marcas redondas y margen
        if fuera_de_escala:
            marcas = [m for m in marcas_verticales(0, max(max(mejores), 0)) if m >= 0]
        else:
            marcas = marcas_verticales(min(mejores + promedios), max(mejores + promedios))
        minimo, maximo = marcas[0], marcas[-1]

        def px(g):
            if len(gens) == 1:
                return (izq + ancho - der) / 2
            return izq + (g - gens[0]) / (gens[-1] - gens[0]) * (ancho - izq - der)

        def py(v):
            return alto - abajo - (v - minimo) / (maximo - minimo) * (alto - arriba - abajo)

        # Ejes, cuadrícula y marcas del eje vertical
        c.create_line(izq, arriba, izq, alto - abajo, fill="#444444")
        c.create_line(izq, alto - abajo, ancho - der, alto - abajo, fill="#444444")
        for valor in marcas:
            c.create_line(izq, py(valor), ancho - der, py(valor), fill="#eeeeee")
            c.create_text(izq - 6, py(valor), text=str(valor), anchor="e", font=("TkDefaultFont", 8))
        c.create_text(14, (arriba + alto - abajo) / 2, text="Aptitud", angle=90,
                      font=("TkDefaultFont", 9))

        # Marcas del eje horizontal sin encimarse
        paso = paso_horizontal(len(gens), ancho - izq - der)
        for g in gens:
            if g % paso == 0:
                c.create_line(px(g), alto - abajo, px(g), alto - abajo + 4, fill="#444444")
                c.create_text(px(g), alto - abajo + 14, text=str(g), font=("TkDefaultFont", 8))
        if fuera_de_escala:
            c.create_text((izq + ancho - der) / 2, alto - 24, text="Generación", font=("TkDefaultFont", 9))
            c.create_text((izq + ancho - der) / 2, alto - 8, fill="#666666", font=("TkDefaultFont", 8),
                          text="Promedios negativos fuera de escala (penalización por exceder el presupuesto)")
        else:
            c.create_text((izq + ancho - der) / 2, alto - 8, text="Generación", font=("TkDefaultFont", 9))

        # Líneas de datos; con más de 50 generaciones se omiten los puntos
        con_puntos = len(gens) <= 50
        for serie, color in ((promedios, COLOR_PROMEDIO), (mejores, COLOR_MEJOR)):
            # Cada tramo se recorta en el borde inferior si la serie baja del mínimo
            for (g0, v0), (g1, v1) in zip(zip(gens, serie), zip(gens[1:], serie[1:])):
                if v0 < minimo and v1 < minimo:
                    continue
                if v0 < minimo:
                    g0, v0 = g0 + (minimo - v0) / (v1 - v0) * (g1 - g0), minimo
                elif v1 < minimo:
                    g1, v1 = g0 + (minimo - v0) / (v1 - v0) * (g1 - g0), minimo
                c.create_line(px(g0), py(v0), px(g1), py(v1), fill=color, width=2, capstyle="round")
            if con_puntos or len(gens) == 1:
                for g, v in zip(gens, serie):
                    if v >= minimo:
                        c.create_oval(px(g) - 3, py(v) - 3, px(g) + 3, py(v) + 3,
                                      fill=color, outline=color)

        self.dibujar_leyenda(izq + 8, arriba + 8, ancho - izq - der)

    def dibujar_leyenda(self, x, y, ancho_disponible):
        """Leyenda en la esquina superior izquierda del área de la gráfica.
        Si no cabe en una línea, los dos elementos van uno debajo del otro."""
        c = self.lienzo
        elementos = (("Mejor aptitud", COLOR_MEJOR), ("Promedio", COLOR_PROMEDIO))
        ancho_fila = 140
        en_columna = 2 * ancho_fila + 16 > ancho_disponible
        ancho_caja = ancho_fila + 8 if en_columna else 2 * ancho_fila + 8
        alto_caja = 44 if en_columna else 24
        c.create_rectangle(x - 4, y - 4, x - 4 + ancho_caja, y - 4 + alto_caja,
                           fill="white", outline="#cccccc")
        for i, (texto, color) in enumerate(elementos):
            xi = x if en_columna else x + i * ancho_fila
            yi = y + 8 + (i * 20 if en_columna else 0)
            c.create_line(xi, yi, xi + 24, yi, fill=color, width=3)
            c.create_text(xi + 30, yi, text=texto, anchor="w", font=("TkDefaultFont", 9))

    def mostrar_mejor(self):
        """Muestra el mejor surtido final con costo, ganancia, aptitud y sobrante."""
        mejor = self.historial[-1]["cromosoma"]
        costo, ganancia = ags.costo_ganancia(mejor)
        sobra = ags.P - costo

        t = self.panel_mejor
        t.config(state="normal")
        t.delete("1.0", "end")
        t.insert("end", f"Cromosoma: {ags.a_texto(mejor)}\n", "negrita")
        comprados = [ags.LOTES[j][0] for j in range(ags.L) if mejor[j] == 1]
        for nombre in comprados or ["(ningún lote)"]:
            t.insert("end", f"  - {nombre}\n")
        t.insert("end", f"Costo: {costo}\n")
        t.insert("end", f"Ganancia: {ganancia}\n")
        t.insert("end", f"Aptitud: {ags.aptitud(mejor)}\n")
        if sobra < 0:
            t.insert("end", f"Se pasa del presupuesto por {-sobra} (P = {ags.P})\n", "rojo")
        else:
            t.insert("end", f"Sobra del presupuesto: {sobra}\n")
        t.config(state="disabled")


def main():
    raiz = tk.Tk()
    Interfaz(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
