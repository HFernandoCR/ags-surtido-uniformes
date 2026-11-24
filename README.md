# AGS para el surtido de una tienda de uniformes

Algoritmo Genético Simple (AGS) que propone qué lotes de mercancía comprar
antes de una temporada, maximizando la ganancia esperada sin exceder el
presupuesto. El problema se modela como una mochila 0-1.

Proyecto de la materia Inteligencia Artificial (SCC-1012), grupo 9SA,
Instituto Tecnológico de Oaxaca.

**Integrantes:** Cruz Ruiz Hector Fernando y García Gallegos Eric
**Docente:** Matadamas Ortiz Idarh Claudio

## Modelo

- **Cromosoma:** 2 bits por prenda. El primero indica si se compra el lote
  de menudeo y el segundo, el de mayoreo (1 = se compra, 0 = no).
- **Aptitud:** f(x) = Σ Gⱼ xⱼ − λ · máx(0, Σ Cⱼ xⱼ − P)
  - G: ganancia esperada del lote
  - C: costo del lote
  - P: presupuesto
  - λ: factor de penalización por exceder el presupuesto

## Esquema del algoritmo

1. Crear N cromosomas al azar.
2. Emparejar al azar a toda la población (todos se cruzan).
3. Cruzar cada pareja con un punto aleatorio (2 hijos por pareja).
4. Mutar a los hijos bit por bit con probabilidad pm.
5. Unir padres e hijos (2N individuos).
6. Ordenar por aptitud y eliminar a los N peores.
7. Renumerar a los sobrevivientes y repetir hasta completar las generaciones.

En un empate de aptitud sobrevive el padre, porque los padres van primero
en la unión y el ordenamiento es estable.

## Requisitos

Python 3.8 o superior. No usa bibliotecas externas.

## Ejecución

```
python3 ags_surtido.py           # ejecuta el AGS
python3 ags_surtido.py pruebas   # ejecuta las pruebas de cada fase
```

## Pruebas por fase

| Fase | Qué comprueba |
|---|---|
| 1 | Datos y parámetros |
| 2 | Aptitud de los individuos de la traza a mano |
| 3 | Población inicial |
| 4 | Emparejamiento aleatorio |
| 5 | Cruce de un punto |
| 6 | Mutación por bit |
| 7 | Unión, eliminación y renumeración |

## Ejemplo de prueba

3 prendas (6 lotes) con presupuesto de 7,000. El óptimo es 101010:
camisa, pantalón y sudadera a menudeo, con costo de 6,400 y ganancia
de 4,200. Con N = 4 y semilla 1, el AGS lo encuentra en la generación 7.
