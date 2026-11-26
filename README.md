# AGS para el surtido de una tienda de uniformes

Algoritmo Genético Simple (AGS) que apoya la decisión de compra de una tienda
de uniformes: indica qué lotes comprar al proveedor con el presupuesto de cada
surtido, maximizando la ganancia esperada de su venta. El problema se modela
como una mochila 0-1.

Proyecto de la materia Inteligencia Artificial (SCC-1012), grupo 9SA,
Instituto Tecnológico de Oaxaca.

**Integrantes:** Cruz Ruiz Hector Fernando y García Gallegos Eric
**Docente:** Matadamas Ortiz Idarh Claudio

## Planteamiento

La tienda compra toda su mercancía al proveedor a precio de mayoreo y la vende
por dos canales:

- **Venta al público:** por pieza.
- **Pedidos de mayoreo:** a escuelas y revendedores, a partir de 6 piezas,
  con el precio más bajo desde 10.

Con el presupuesto de cada surtido ($1,500 a $4,000), el algoritmo decide qué
lotes comprar. Cada prenda tiene dos lotes posibles, uno por canal de venta.

## Modelo

- **Cromosoma:** 2 bits por prenda. El primero indica si se compra el lote
  para venta al público y el segundo, el lote para pedidos de mayoreo
  (1 = se compra, 0 = no).
- **Lote:** Q piezas. Costo C = c · Q y ganancia G = (p − c) · Q, donde c es
  el costo unitario de compra y p el precio de venta del canal.
- **Aptitud:** f(x) = Σ Gⱼ xⱼ − λ · máx(0, Σ Cⱼ xⱼ − P)
  - G: ganancia esperada del lote
  - C: costo del lote
  - P: presupuesto del surtido
  - λ: factor de penalización por exceder el presupuesto

Con los datos de la tienda, el valor crítico de λ es 0.571: por debajo, un
surtido que se pasa del presupuesto puede superar al óptimo. Se usa λ = 100
como margen de seguridad.

## Esquema del algoritmo

1. Crear N cromosomas al azar.
2. Emparejar al azar a toda la población (todos se cruzan).
3. Cruzar cada pareja con un punto aleatorio (2 hijos por pareja).
4. Mutar a los hijos bit por bit con probabilidad pm = 1/L.
5. Unir padres e hijos (2N individuos).
6. Ordenar por aptitud y eliminar a los N peores.
7. Renumerar a los sobrevivientes y repetir hasta completar las generaciones.

En un empate de aptitud sobrevive el padre, porque los padres van primero
en la unión y el ordenamiento es estable. Este esquema de supervivencia
corresponde a la selección elitista entre generaciones del algoritmo CHC
(Eshelman, 1991).

## Requisitos

- Python 3.8 o superior.
- Los modos normal, `pruebas` y `validacion` solo usan la biblioteca estándar.
- Los modos `grafica`, `tienda` y `barrido` guardan gráficas y requieren
  Matplotlib:

```
python -m pip install matplotlib
```

## Ejecución

```
python3 ags_surtido.py              # AGS con el ejemplo de 3 prendas
python3 ags_surtido.py pruebas      # pruebas de cada fase
python3 ags_surtido.py grafica      # ejemplo de 3 prendas y su gráfica de convergencia
python3 ags_surtido.py tienda       # AGS con los datos del comerciante y su gráfica
python3 ags_surtido.py validacion   # comparación con otros métodos en 30 ejecuciones
python3 ags_surtido.py barrido      # comparación en presupuestos de $1,500 a $4,000
```

Todas las corridas usan semillas fijas, así que los resultados se pueden
repetir.

## Pruebas por fase

Usan el ejemplo de 3 prendas, el mismo de la traza a mano.

| Fase | Qué comprueba |
|---|---|
| 1 | Datos y parámetros |
| 2 | Aptitud de los individuos de la traza a mano |
| 3 | Población inicial |
| 4 | Emparejamiento aleatorio |
| 5 | Cruce de un punto |
| 6 | Mutación por bit |
| 7 | Unión, eliminación y renumeración |

## Datos

### Ejemplo de prueba (3 prendas)

6 lotes con presupuesto de $7,000. El óptimo es 101010: camisa, pantalón y
sudadera para venta al público, con costo de $6,400 y ganancia de $4,200.
Con N = 4 y semilla 1, el AGS lo encuentra en la generación 7.

### Datos del comerciante (Uniformes JAEL, Central de Abastos, Oaxaca)

Suéter, camisa y tres tipos de falda: 10 lotes y 1,024 combinaciones.
Presupuesto de $4,000, N = 20, 50 generaciones y λ = 100.

El óptimo es 1011000010: suéter y falda tipo 3 para venta al público, y
camisa para venta al público y para pedido de mayoreo. Costo de $4,000 y
ganancia de $2,900. Con semilla 1, el AGS lo encuentra en la generación 28.

**Supuestos:** precios y costos tomados del punto medio de los rangos que
indicó el dueño, lotes de 10 piezas y venta completa de cada lote.

## Resultados de la validación

### Modo `validacion` (P = $4,000, 30 ejecuciones, 1,020 evaluaciones cada una)

| Método | Media | Desv. | Peor | % del óptimo | Óptimos |
|---|---|---|---|---|---|
| Voraz | 2,900 | 0 | 2,900 | 100.0 % | 30/30 |
| AGS | 2,890 | 37.4 | 2,750 | 99.7 % | 28/30 |
| Búsqueda aleatoria | 2,840 | 91.7 | 2,550 | 97.9 % | 20/30 |

El óptimo exacto se obtiene revisando las 1,024 combinaciones.

### Modo `barrido` (51 presupuestos de $1,500 a $4,000)

| Método | Llega al óptimo | % del óptimo en promedio | Peor |
|---|---|---|---|
| Voraz | 31 de 51 presupuestos | 92.5 % | 74.1 % |
| AGS | 93.0 % de 1,530 ejecuciones | 99.2 % | 97.2 % (promedio de un presupuesto) |
| Búsqueda aleatoria | 61.2 % de 1,530 ejecuciones | 94.6 % | 86.2 % (promedio de un presupuesto) |

Con $4,000 el voraz acierta por coincidencia; en 20 de los 51 presupuestos
reales no llega al óptimo. El AGS alcanza más del 95 % del óptimo en todo el
rango.

## Interfaz gráfica

La rama `prototipo-interfaz` incluye `interfaz.py`, una interfaz en tkinter
que usa las mismas funciones del algoritmo. Permite editar los lotes, cargar
el ejemplo o los datos de la tienda, y ver la tabla por generación, la gráfica
de convergencia y el mejor surtido.

```
git checkout prototipo-interfaz
python3 interfaz.py
```

## Limitaciones

- En la realidad, la tienda no separa su mercancía por canal de venta; los
  dos lotes por prenda son una simplificación del modelo.
- Solo 5 prendas tienen datos completos; faltan los costos de las demás y la
  demanda por temporada.
- Con 10 bits el problema es pequeño y puede resolverse revisando todas las
  combinaciones; el AGS se justifica al crecer el número de prendas y al
  agregar condiciones que vuelven el modelo no lineal.

## Referencias

- Eshelman, L. J. (1991). The CHC adaptive search algorithm: How to have safe
  search when engaging in nontraditional genetic recombination. En G. J. E.
  Rawlins (Ed.), *Foundations of genetic algorithms* (pp. 265-283). Morgan
  Kaufmann.
- Goldberg, D. E. (1989). *Genetic algorithms in search, optimization, and
  machine learning*. Addison-Wesley.