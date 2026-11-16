# Explicación del código del proyecto e instrucciones de uso

Este documento explica, archivo por archivo y función por función, el código de la carpeta [`entrega/`](entrega/). También explica cómo ejecutarlo y probarlo.

La teoría de cada algoritmo está en la [guía teórica](Guia_teorica_proyecto.md). Aquí se explica **cómo** se tradujo esa teoría a Python.

> **Convención.** Cuando se dice "línea N" se refiere al número de línea del archivo. Los enlaces del tipo [`ll1.py#L91`](entrega/parsing/ll1.py#L91) abren el archivo en esa línea cuando se ve en GitHub.

---

## Índice

1. [Instrucciones de uso](#1-instrucciones-de-uso)
2. [Mapa del código: qué hace cada archivo y cómo se conectan](#2-mapa-del-código)
3. [Conceptos de Python que aparecen en el código](#3-conceptos-de-python-que-aparecen-en-el-código)
4. [`parsing/grammar.py`: leer la gramática](#4-parsinggrammarpy-leer-la-gramática)
5. [`parsing/first_follow.py`: FIRST y FOLLOW (ítem 1)](#5-parsingfirst_followpy-first-y-follow-ítem-1)
6. [`parsing/parse_tree.py`: el árbol de análisis](#6-parsingparse_treepy-el-árbol-de-análisis)
7. [`parsing/ll1.py`: prueba, tabla y parser LL(1) (ítem 2)](#7-parsingll1py-prueba-tabla-y-parser-ll1-ítem-2)
8. [`parsing/slr1.py`: autómata LR(0), tabla y parser SLR(1) (ítem 2)](#8-parsingslr1py-autómata-lr0-tabla-y-parser-slr1-ítem-2)
9. [`main.py`: el programa de los ítems 1 y 2](#9-mainpy-el-programa-de-los-ítems-1-y-2)
10. [`sdd/evaluator.py`: el evaluador general de SDD (ítem 3)](#10-sddevaluatorpy-el-evaluador-general-de-sdd-ítem-3)
11. [`sdd/nested_list_sdd.py`: nuestra SDD](#11-sddnested_list_sddpy-nuestra-sdd)
12. [`sdd_main.py`: el programa del ítem 3](#12-sdd_mainpy-el-programa-del-ítem-3)
13. [`tests/test_project.py`: las pruebas](#13-teststest_projectpy-las-pruebas)
14. [Cómo modificar el código (preparación para la sustentación)](#14-cómo-modificar-el-código)
15. [Qué falta para la entrega](#15-qué-falta-para-la-entrega)

---

## 1. Instrucciones de uso

### 1.1 Requisitos

- **Python 3.8 o más reciente**, en macOS, Windows o Linux. Se probó con Python 3.9, 3.11, 3.12, 3.14 y 3.15.
- No hay que instalar nada más: solo se usa la biblioteca estándar de Python.
- **Todos los comandos se ejecutan dentro de la carpeta `entrega` del repositorio** (cambia la ruta por la de tu computador):

```bash
cd ruta/al/repositorio/entrega
```

**El nombre del comando de Python depende del sistema:**

| Sistema | Comando | Cómo comprobar la versión |
|---|---|---|
| macOS / Linux | `python3` | `python3 --version` |
| Windows | `py` (o `python`) | `py --version` |

En Windows, en todos los comandos de este documento, cambia `python3` por `py`. Si `py` no existe, instala Python desde [python.org](https://www.python.org/downloads/) y marca la casilla **"Add python.exe to PATH"**.

**Redirección de archivos en Windows.** Los comandos con `<` (por ejemplo `python3 main.py < tests/inputs/example1.txt`) funcionan en **macOS, Linux y en el "Símbolo del sistema" (cmd)** de Windows. **PowerShell no admite `<`**. En PowerShell, usa una de estas dos formas:

```powershell
Get-Content tests\inputs\example1.txt | py main.py
```

```powershell
cmd /c "py main.py < tests\inputs\example1.txt"
```

Si escribes la entrada a mano (`py main.py` y luego escribes), funciona igual en cualquier terminal.

### 1.2 Ítems 1 y 2: `main.py`

El programa lee **de la entrada estándar** (el teclado), primero la gramática y luego las cadenas. Hay dos formas de usarlo.

**a) Escribiendo a mano:**

```bash
python3 main.py
```

Luego escribes:

```
3
S -> AB
A -> aA d
B -> bBc e
```

Como esta gramática es LL(1) y SLR(1), el programa pregunta:

```
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```

1. Escribe `T` y Enter.
2. Escribe las cadenas, una por línea: `adbc` + Enter responde `yes`, y `a` + Enter responde `no`.
3. Para la cadena vacía escribe `e`.
4. Una **línea vacía** (Enter sin escribir nada) termina las cadenas y el programa vuelve a preguntar.
5. `Q` termina el programa.

**b) Con un archivo de entrada (redirección `<`):**

```bash
python3 main.py < tests/inputs/example1.txt
```

El archivo contiene todo lo que escribirías a mano: la gramática, las cadenas y la línea vacía final. En `tests/inputs/` hay ejemplos listos:

| Archivo | Qué contiene | Resultado esperado |
|---|---|---|
| `example1.txt` | Ejemplo 1 del enunciado | `Grammar is SLR(1).` y `yes yes no` |
| `example2.txt` | Ejemplo 2 (elige T, luego Q) | menú, `yes yes no`, menú |
| `example3.txt` | Ejemplo 3 | `Grammar is neither LL(1) nor SLR(1).` |
| `ll1_not_slr1.txt` | `S -> AaAb BbBa`, `A -> e`, `B -> e` | `Grammar is LL(1).` y `yes yes no` |
| `neither_lr.txt` | `S -> L=R R`, ... (Ejemplo 4.48 del libro) | `Grammar is neither LL(1) nor SLR(1).` |

**Opciones** (se pueden combinar):

| Opción | Qué hace | ¿La pide el enunciado? |
|---|---|---|
| `--sets` | Imprime FIRST y FOLLOW antes de seguir | **Sí** |
| `--table` | Imprime la tabla LL(1) y, si no es LL(1), qué condición falla | No (sirve para el informe) |
| `--automaton` | Imprime la gramática aumentada, los estados LR(0) con sus GOTO, la tabla SLR(1) y los conflictos | No (sirve para el informe) |
| `--trace` | Imprime cada análisis paso a paso (como las Figs. 4.21 y 4.38 del libro) | No (sirve para el informe: "one string parsed step by step") |

Ejemplo con todo:

```bash
python3 main.py --sets --table --automaton --trace < tests/inputs/example2.txt
```

> **Para el informe:** la sección 4.1 del enunciado pide una gramática propia con sus FIRST/FOLLOW, su tabla LL(1) o su autómata LR(0) con la tabla SLR(1) "computed by your program", y una cadena analizada paso a paso. Las opciones `--sets --table --automaton --trace` generan exactamente eso. Basta con copiar la salida.

### 1.3 Ítem 3: `sdd_main.py`

La gramática y la SDD ya están dentro del código. El programa solo lee cadenas, hasta una línea vacía:

```bash
python3 sdd_main.py < tests/inputs/sdd_strings.txt
```

O a mano: `python3 sdd_main.py`, escribes `[1,[2,3]]` + Enter y terminas con una línea vacía.

| Opción | Qué hace |
|---|---|
| `--parser LL` / `--parser SLR` | Elige el parser del ítem 2 que construye el árbol. Por defecto es `LL`. |
| `--rules` | Imprime la gramática, la **tabla de atributos**, las **reglas semánticas** y la **clasificación S/L-atribuida** (pasos 2 y 4 del enunciado). |
| `--graph` | Imprime también los vértices y las aristas del **grafo de dependencias** (paso 3). |
| `--circular` | Usa la variante **circular** de la SDD para mostrar que se detecta el ciclo (paso 6). |

Ejemplos:

```bash
python3 sdd_main.py --rules --graph < tests/inputs/sdd_strings.txt
```

```bash
python3 sdd_main.py --circular < tests/inputs/sdd_circular.txt
```

Salida para `[1,[2,3]]`, recortada:

```
Input: [1,[2,3]]
Annotated parse tree:
  S#1  (S -> L)  v=11
    L#2  (L -> [E])  d=0, s=11
      [#3  lexval='['
      E#4  (E -> IR)  d=1, s=11
        I#5  (I -> 1)  d=1, s=1
          1#6  lexval='1'
  ...
Evaluation order (topological order of the dependency graph):
  1. L#2.d = 0
  2. R#22.s = 0
  ...
  25. S#1.v = 11
Result: S.v = 11
```

Cómo leer la salida:
- `L#2` significa "el nodo número 2 (en preorden), etiquetado con L".
- `(L -> [E])` es la producción aplicada en ese nodo.
- Después vienen sus atributos.

### 1.4 Pruebas automáticas

```bash
python3 -m unittest discover -s tests -v
```

Deben salir **21 pruebas con `OK`**. Antes de entregar, borra las carpetas `__pycache__` que crea Python, porque el enunciado pide no incluir archivos compilados. Al repositorio de GitHub no se suben, porque el archivo `.gitignore` las excluye.

En macOS / Linux:

```bash
find . -name __pycache__ -exec rm -rf {} +
```

En Windows (PowerShell):

```powershell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

---

## 2. Mapa del código

```
entrega/
├── main.py                 ← programa de los ítems 1 y 2 (lee la entrada, decide el caso, imprime)
├── sdd_main.py             ← programa del ítem 3
├── parsing/                ← todo lo de los ítems 1 y 2
│   ├── grammar.py          ← Production, Grammar, read_grammar        (formato §2.2 del enunciado)
│   ├── first_follow.py     ← compute_first, compute_follow, format_set (§4.4.2 del libro)
│   ├── parse_tree.py       ← Node (nodo del árbol) y su impresión
│   ├── ll1.py              ← ll1_violations, build_ll1_table, LL1Parser (§4.4.3–4.4.4)
│   └── slr1.py             ← SLR1Parser: closure, goto, colección, tabla, parse (§4.6)
├── sdd/                    ← todo lo del ítem 3
│   ├── evaluator.py        ← Rule, SDD, validación, clasificación, grafo, Kahn, evaluate (§5.1–5.2)
│   └── nested_list_sdd.py  ← nuestra SDD, SOLO datos
├── tests/
│   ├── test_project.py     ← 21 pruebas
│   └── inputs/             ← archivos de entrada de ejemplo
└── README.md               ← en inglés, exigido por el enunciado
```

**Flujo de `main.py`:**

```
entrada estándar
   │  read_grammar()                      grammar.py
   ▼
Grammar ──► compute_first() ──► compute_follow()      first_follow.py
   │                 │                │
   │                 └──────┬─────────┘
   ▼                        ▼
LL1Parser(grammar, first, follow)     SLR1Parser(grammar, first, follow)
   │  .is_ll1                            │  .is_slr1
   └──────────────┬──────────────────────┘
                  ▼
     main() elige uno de los 4 casos del enunciado
                  │
                  ▼
     parse_strings(): para cada cadena → parser.parse(tokens) → "yes"/"no"
```

**Flujo de `sdd_main.py`:**

```
GRAMMAR_TEXT ──► Grammar ──► FIRST/FOLLOW ──► LL1Parser o SLR1Parser
build_sdd() ──► validate_sdd() (¿la SDD está bien definida?)
para cada cadena:
    parser.parse(tokens) ──► árbol (Node)        (o "no")
    evaluate(árbol, sdd):
        number_nodes ──► build_dependency_graph ──► topological_order (Kahn) ──► aplicar reglas
    imprimir árbol anotado, orden de evaluación y S.v
```

**Decisión de diseño importante:** los dos parsers reciben **los mismos** `first` y `follow`, calculados una sola vez. FIRST y FOLLOW se usan en la tabla LL(1) (Algoritmo 4.31) y en la tabla SLR(1), regla (b) del Algoritmo 4.46.

---

## 3. Conceptos de Python que aparecen en el código

Si ya los conoces, salta a la [sección 4](#4-parsinggrammarpy-leer-la-gramática).

| Concepto | Ejemplo en el código | Qué significa |
|---|---|---|
| **Tupla** | `("a", "A")`, `()` | Secuencia inmutable. `()` es la tupla vacía: así representamos el cuerpo de `A -> ε`. |
| **Conjunto (`set`)** | `{"a", "d"}` | Colección sin repetidos y sin orden. `|=` agrega elementos, `-` es diferencia, `&` es intersección, `<=` es "es subconjunto de". |
| **`frozenset`** | `frozenset({(0, 0)})` | Conjunto inmutable. Se puede usar como clave de diccionario, por eso así representamos un estado LR(0). |
| **Diccionario (`dict`)** | `table[("S", "a")]` | Asocia claves con valores. Las claves pueden ser tuplas, por ejemplo `(no_terminal, terminal)`. |
| **`dict.setdefault(k, [])`** | `table.setdefault((A, a), [])` | Devuelve el valor de `k`; si no existe, lo crea con `[]` y lo devuelve. |
| **`dict.get(k)`** | `self.action.get((s, a))` | Devuelve el valor de `k` o `None` si no existe (no da error). |
| **Comprensión de listas/conjuntos/diccionarios** | `{A: set() for A in nonterminals}` | Construye una colección en una línea. |
| **`@dataclass`** | `class Production` | Python genera automáticamente `__init__`, `__eq__`, etc. Con `frozen=True` el objeto es inmutable y se puede usar en conjuntos y como clave. |
| **`lambda`** | `lambda d: d + 1` | Función anónima de una línea. Equivale a `def f(d): return d + 1`. |
| **Generador (`yield`)** | `preorder(node)` | Función que entrega valores uno por uno. `yield from` entrega todos los de otro generador. |
| **f-string** | `f"First({A}) = {...}"` | Cadena con expresiones entre `{}`. `{x!r}` muestra `repr(x)`, por ejemplo con comillas. |
| **`enumerate(lista, start=1)`** | | Recorre dando `(índice, elemento)`. |
| **`zip(a, b)`** | | Recorre dos listas en paralelo. |
| **`reversed(lista)`** | | Recorre al revés. |
| **`del lista[i:]`** | `del states[len(states) - r:]` | Borra los elementos desde `i` hasta el final. |
| **`deque`** | `ready = deque(...)` | Cola eficiente: `popleft()` saca el primero. |
| **`Counter`** | `defined = Counter()` | Diccionario que cuenta. Las claves nuevas empiezan en 0. |
| **Excepciones** | `raise GrammarError(...)`, `try/except` | Señalan errores y permiten atraparlos. |
| **`if __name__ == "__main__":`** | al final de `main.py` | El código de abajo solo corre si el archivo se ejecuta directamente, no si se importa. |
| **`argparse`** | `--sets` | Biblioteca estándar para leer las opciones de la línea de comandos. |

---

## 4. `parsing/grammar.py`: leer la gramática

[Abrir archivo](entrega/parsing/grammar.py). Se encarga de la **sección 2.2 del enunciado**: el formato de entrada y sus suposiciones.

### 4.1 Constantes (líneas 19–22)

```python
EPSILON = "ε"           # cadena vacía (en la entrada y en la salida se escribe 'e')
END = "$"               # marcador de fin de entrada (§4.4.2)
START = "S"             # símbolo inicial de toda gramática del proyecto
AUGMENTED_START = "S'"  # símbolo inicial de la gramática aumentada (§4.6.2)
```

- **¿Por qué ε y no `e` internamente?** En la entrada `e` significa "vacío", pero internamente queremos un marcador que **nunca** pueda confundirse con un terminal. ε no se puede escribir como terminal en la entrada. Al **imprimir** se vuelve a escribir `e` (ver `format_set`).
- **`$`** es el marcador de fin. El enunciado prohíbe usarlo como terminal, así que no hay conflicto.
- **`S'` es una cadena de dos caracteres.** Ningún símbolo de la entrada puede ser igual a `"S'"`, porque todos los símbolos de la entrada tienen un solo carácter. Así el símbolo aumentado nunca choca con un no terminal ni con un terminal. Esto responde a "remember to augment the grammar with a new start symbol" del enunciado.

### 4.2 `GrammarError` (línea 25)

Es una excepción propia para los errores de formato de la entrada. `main.py` la atrapa e imprime un mensaje.

### 4.3 `is_nonterminal(symbol)` (línea 29)

```python
return symbol == AUGMENTED_START or (len(symbol) == 1 and "A" <= symbol <= "Z")
```

Implementa la convención del enunciado, "Nonterminals are capital letters", más el caso de `S'`. Usamos `"A" <= symbol <= "Z"` en lugar de `symbol.isupper()` porque `isupper()` también acepta mayúsculas de otros alfabetos (como `Ñ` o `Σ`). Todo lo que **no** es no terminal es terminal.

### 4.4 `Production` (líneas 34–45)

```python
@dataclass(frozen=True)
class Production:
    head: str
    body: tuple
```

- Representa `head -> body`. El cuerpo es una **tupla de símbolos**: `B -> bBc` es `Production("B", ("b", "B", "c"))`, y `B -> ε` es `Production("B", ())`.
- `frozen=True` la vuelve inmutable y comparable, así que dos producciones con la misma cabeza y el mismo cuerpo son iguales.
- `body_text()` devuelve el cuerpo como texto, con `e` si es vacío.
- `__str__` define cómo se imprime: `"B -> bBc"` o `"B -> e"`. **Este texto también sirve de clave para buscar las reglas de la SDD** (sección 10).

### 4.5 `Grammar` (líneas 48–78)

Guarda G = (N, T, P, S):

| Atributo | Contenido | Para qué se usa |
|---|---|---|
| `productions` | lista de `Production`; **el índice es el número de la producción** | tablas LL y SLR |
| `nonterminals` | no terminales en el orden de la entrada | recorrerlos; numerar estados |
| `start` | `"S"` | FOLLOW (regla 1), parsers |
| `terminals_in_order` | terminales en orden de **primera aparición** | numerar los estados LR(0) como el libro |
| `terminals` | terminales en **orden ASCII** (`sorted`) | columnas de las tablas impresas |
| `by_head` | `{A: [índices de las producciones de A]}` | prueba LL(1), CLOSURE |

Líneas 61–66: se recorren todos los cuerpos y cada símbolo que no es no terminal y no se ha visto se agrega a `seen`. Así se obtienen los terminales en orden de aparición, y `sorted(seen)` da el orden ASCII.

### 4.6 `parse_production_line(line)` (líneas 81–103)

Convierte una línea como `"B -> bBc e"` en `("B", [("b","B","c"), ()])`:

1. Si no hay `->`, es un error.
2. `line.split("->", 1)` parte **solo en la primera** flecha.
3. La cabeza debe ser **una** letra mayúscula.
4. `right_side.split()` separa por espacios, como pide el enunciado: "alternatives separated by blank spaces".
5. Para cada alternativa:
   - Si es exactamente `"e"`, el cuerpo es `()` (ε).
   - Si no, se comprueba que no contenga `e` ni `$`, que el enunciado prohíbe como terminales.
   - `tuple(alternative)` separa la alternativa en caracteres, porque **cada carácter es un símbolo**: `"bBc"` se vuelve `("b","B","c")`.

### 4.7 `read_grammar(read_line)` (líneas 106–143)

Recibe una **función** `read_line` que devuelve la siguiente línea o `None` al final. Así la misma función sirve para leer del teclado (`main.py`) y para leer de un texto (`grammar_from_text`).

1. Lee la primera línea, saltando líneas vacías iniciales, y la convierte a entero `n`.
2. Lee exactamente `n` líneas de producciones. Para cada una:
   - Si el no terminal ya apareció, es un error. El enunciado dice "Every nonterminal appears on the left side of exactly one input line".
   - Se agrega a `nonterminals`, en orden de aparición.
   - `productions.extend(...)` agrega una `Production` por cada alternativa.
3. Validaciones finales:
   - Debe existir `S`.
   - Todo no terminal usado en un cuerpo debe tener su propia línea.
4. Devuelve `Grammar(productions, nonterminals)`.

> **Nota:** el enunciado dice "The first line is not necessarily the one of S". El código no supone que S está primero: usa `START = "S"` directamente.

### 4.8 `grammar_from_text(text)` (línea 146)

```python
lines = iter(text.strip("\n").splitlines())
return read_grammar(lambda: next(lines, None))
```

Convierte un texto en un iterador de líneas, y `next(lines, None)` devuelve la siguiente o `None` al final. Lo usan `sdd_main.py`, donde la gramática está escrita en el código, y las pruebas.

---

## 5. `parsing/first_follow.py`: FIRST y FOLLOW (ítem 1)

[Abrir archivo](entrega/parsing/first_follow.py). Implementa **§4.4.2** del libro.

### 5.1 `first_of_symbol(symbol, first)` (línea 11)

```python
if is_nonterminal(symbol):
    return first[symbol]
return {symbol}
```

- Para un no terminal, devuelve su conjunto actual.
- **Para un terminal, FIRST(X) = {X}** (regla 1 del libro).

### 5.2 `first_of_string(symbols, first)` (líneas 18–34): FIRST de una cadena

```python
result = set()
for symbol in symbols:
    first_x = first_of_symbol(symbol, first)
    result |= first_x - {EPSILON}       # (1)
    if EPSILON not in first_x:
        return result                   # (2)
result.add(EPSILON)                     # (3)
return result
```

Es la regla del libro para FIRST(X₁X₂…Xₙ):

- **(1)** Agrega los símbolos de FIRST(Xᵢ) que no son ε.
- **(2)** Si Xᵢ **no** deriva ε, los símbolos siguientes no pueden "asomarse" al principio, así que se termina.
- **(3)** Solo se llega aquí si **todos** los Xᵢ derivan ε, y entonces ε ∈ FIRST(X₁…Xₙ).

**Caso especial:** si `symbols` está vacío (el cuerpo de `A -> ε`), el `for` no se ejecuta y se devuelve `{ε}`. Es decir, FIRST(ε) = {ε}. Por eso la **regla 3 del libro** (si `X -> ε`, agregar ε a FIRST(X)) no necesita código aparte.

Esta función se usa en tres lugares: `compute_first`, `compute_follow` (FIRST(β)) y la tabla LL(1) (FIRST(α)).

### 5.3 `compute_first(grammar)` (líneas 37–52)

```python
first = {A: set() for A in grammar.nonterminals}   # todos empiezan vacíos
changed = True
while changed:                                     # hasta un punto fijo
    changed = False
    for production in grammar.productions:
        new_symbols = first_of_string(production.body, first)
        if not new_symbols <= first[production.head]:
            first[production.head] |= new_symbols
            changed = True
return first
```

- **Regla 2 del libro:** para cada `A -> Y1…Yk`, todo FIRST(Y1…Yk) va a FIRST(A).
- **¿Por qué el `while changed`?** El libro dice "apply the following rules until no more terminals or ε can be added". FIRST(A) puede depender de FIRST(B), y este de FIRST(A); por ejemplo, con recursión. Se repasan todas las producciones una y otra vez hasta que una pasada completa no cambie nada. Eso es un **punto fijo**.
- **¿Por qué termina?** Los conjuntos solo crecen y están acotados (no pueden tener más que todos los terminales y ε). Tarde o temprano dejan de crecer.
- `new_symbols <= first[...]` pregunta "¿ya estaban todos?". Si no, se agregan y se marca `changed`.

### 5.4 `compute_follow(grammar, first)` (líneas 55–81)

```python
follow = {A: set() for A in grammar.nonterminals}
follow[grammar.start].add(END)                     # regla 1
changed = True
while changed:
    changed = False
    for production in grammar.productions:
        A = production.head
        for i, B in enumerate(production.body):    # cada aparición de B
            if not is_nonterminal(B):
                continue
            beta = production.body[i + 1:]         # lo que sigue a B
            first_beta = first_of_string(beta, first)
            new_symbols = first_beta - {EPSILON}             # regla 2
            if EPSILON in first_beta:                        # regla 3
                new_symbols |= follow[A]
            if not new_symbols <= follow[B]:
                follow[B] |= new_symbols
                changed = True
return follow
```

- **Regla 1:** `$ ∈ FOLLOW(S)`.
- Para **cada aparición** de un no terminal B en cada cuerpo (`enumerate` da la posición `i`), `beta` es lo que queda a su derecha.
- **Regla 2:** FIRST(β) − {ε} va a FOLLOW(B).
- **Regla 3:** si β puede desaparecer (ε ∈ FIRST(β)), todo FOLLOW(A) va a FOLLOW(B). **Esto incluye el caso `A -> αB`:** si B está al final, `beta` es `()` y `first_of_string(())` = {ε}. Un solo `if` cubre las dos formas de la regla 3 del libro.
- FOLLOW **nunca** recibe ε, porque siempre se resta `- {EPSILON}` y FOLLOW(A) tampoco lo tiene.
- Se itera hasta un punto fijo igual que en FIRST.

### 5.5 `format_set(symbols)` (líneas 84–94)

```python
terminals = sorted(s for s in symbols if s not in (EPSILON, END))
if EPSILON in symbols: terminals.append("e")
if END in symbols:     terminals.append("$")
return "{" + ", ".join(terminals) + "}"
```

Implementa el formato exacto del enunciado: "write the terminals in ASCII order, followed by `e` (for ε, if it belongs to the set) and then by `$`".
- `sorted` sobre caracteres ordena por código ASCII.
- Al final se agregan `e` y `$`, en ese orden.

### 5.6 `sets_report(...)` (líneas 97–101)

Genera las líneas de `--sets`: primero `First(A) = …` para todos los no terminales en **orden alfabético** (`sorted(grammar.nonterminals)`), luego `Follow(A) = …`.

> Recuerda que el enunciado no deja claro si se intercalan. Si el profesor dice que van intercalados (`First(A)`, `Follow(A)`, `First(B)`, …), solo hay que cambiar estas dos líneas por un único `for` que agregue las dos.

---

## 6. `parsing/parse_tree.py`: el árbol de análisis

[Abrir archivo](entrega/parsing/parse_tree.py). El enunciado (paso 5.2 del ítem 3) dice: "Each node stores its symbol, the production used (if it is a nonterminal), its children and its attribute values". Eso es exactamente `Node`:

```python
class Node:
    def __init__(self, symbol, production=None):
        self.symbol = symbol
        self.production = production   # Production, o None si es hoja
        self.children = []
        self.attrs = {}                # atributo -> valor
        self.id = None                 # número en preorden
```

| Función | Qué hace |
|---|---|
| `is_leaf()` | Un nodo sin producción es una hoja (terminal o ε). |
| `is_epsilon()` | ¿Es la hoja ε? |
| `terminal_leaf(symbol)` | Crea la hoja de un terminal **con `attrs["lexval"] = symbol`**. El enunciado dice "the attribute lexval of a terminal is the character itself". |
| `epsilon_leaf()` | Hoja ε, hija única de un nodo cuya producción es `A -> ε`. Así el árbol se dibuja como en el libro (Fig. 5.5). |
| `preorder(node)` | Generador: el nodo y luego, recursivamente, sus hijos de izquierda a derecha. |
| `number_nodes(root)` | Numera los nodos en preorden (1, 2, 3…) para poder nombrarlos (`L#2`). |
| `node_label(node)` | `"L#2"`, o `"ε"` para la hoja vacía. |
| `format_tree(root)` | Una línea por nodo, con **2 espacios de sangría por nivel**, la producción y los atributos. Es el formato que pide el enunciado: "one node per line, indented by depth, with its attributes". |

`format_tree` usa una función interna recursiva `visit(node, depth)`: escribe la línea del nodo y llama a `visit` con cada hijo y `depth + 1`.

---

## 7. `parsing/ll1.py`: prueba, tabla y parser LL(1) (ítem 2)

[Abrir archivo](entrega/parsing/ll1.py). Implementa **§4.4.3 y §4.4.4**.

### 7.1 `ll1_violations(grammar, first, follow)` (líneas 17–49): la prueba LL(1)

El enunciado dice: "The condition for a grammar to be LL(1) is given at the beginning of the section; implement that test in your solution". Esta función es esa prueba, escrita casi literalmente:

```python
for A in grammar.nonterminals:
    indices = grammar.by_head[A]
    for x in range(len(indices)):
        for y in range(x + 1, len(indices)):        # cada par distinto α | β
            ...
            first_alpha = first_of_string(alpha.body, first)
            first_beta = first_of_string(beta.body, first)

            common = (first_alpha & first_beta) - {EPSILON}
            if common:                                       # condición 1
                ...
            if EPSILON in first_alpha and EPSILON in first_beta:   # condición 2
                ...
            if EPSILON in first_beta and (first_alpha - {EPSILON}) & follow[A]:   # condición 3
                ...
            if EPSILON in first_alpha and (first_beta - {EPSILON}) & follow[A]:   # condición 3 (simétrica)
                ...
```

- Los dos `for` anidados con `y` desde `x + 1` recorren **cada par de producciones distintas** de A una sola vez.
- **Condición 1:** α y β no pueden empezar con el mismo terminal, así que FIRST(α) ∩ FIRST(β) sin ε debe ser vacío.
- **Condición 2:** a lo sumo una deriva ε.
- **Condición 3:** si β ⇒* ε, α no puede empezar con un terminal de FOLLOW(A). Y lo simétrico.
- No se devuelve solo `True`/`False`, sino la **lista de violaciones**. Si la lista está vacía, la gramática es LL(1). La lista se imprime con `--table` para explicar **por qué** no es LL(1).

> **La gramática no se transforma.** No hay ningún código que elimine la recursión izquierda o factorice: la prueba se hace sobre la gramática tal como llega, como exige el enunciado.

### 7.2 `build_ll1_table(grammar, first, follow)` (líneas 52–75): Algoritmo 4.31

```python
table = {}

def add(A, a, index):
    cell = table.setdefault((A, a), [])
    if index not in cell:
        cell.append(index)

for index, production in enumerate(grammar.productions):
    first_alpha = first_of_string(production.body, first)
    for a in first_alpha - {EPSILON}:            # paso 1
        add(production.head, a, index)
    if EPSILON in first_alpha:                   # paso 2
        for b in follow[production.head]:
            add(production.head, b, index)
return table
```

- La tabla M es un diccionario: la clave es `(no_terminal, terminal_o_$)` y el valor es una **lista** de números de producción. Debería tener a lo sumo un elemento; si tiene más, hay conflicto.
- **Paso 1:** `A -> α` va en M[A, a] para cada `a ∈ FIRST(α)`.
- **Paso 2:** si α ⇒* ε, `A -> α` va en M[A, b] para cada `b ∈ FOLLOW(A)`. Como FOLLOW(A) ya contiene `$` cuando corresponde, M[A, $] queda cubierto sin código aparte.
- **¿Por qué `if index not in cell`?** Si α es anulable y un terminal está a la vez en FIRST(α) y en FOLLOW(A), la misma producción se agregaría dos veces a la misma celda. Eso parecería un conflicto falso.
- Las celdas que no existen en el diccionario son **error**.

### 7.3 `LL1Parser.__init__` (líneas 81–85)

```python
self.violations = ll1_violations(grammar, first, follow)
self.is_ll1 = not self.violations          # lista vacía ⇒ es LL(1)
self.table = build_ll1_table(grammar, first, follow)
```

`table_conflicts()` (línea 87) devuelve las celdas con más de una producción. Según el libro, existen **si y solo si** la gramática no es LL(1). Es la misma prueba vista desde la tabla, y las pruebas automáticas comprueban que las dos coinciden.

### 7.4 `LL1Parser.parse(tokens, trace)` (líneas 91–141): Algoritmo 4.34

Es la traducción de la **Fig. 4.20** del libro, más la construcción del árbol. Compáralo línea por línea:

| Fig. 4.20 del libro | Código |
|---|---|
| `let a be the first symbol of w;` | `symbols = list(tokens) + [END]`; `a = symbols[position]` |
| (pila inicial: S encima de $) | `stack = [(END, None), (self.grammar.start, root)]` |
| `let X be the top stack symbol;` | `X, node = stack[-1]` |
| `while (X ≠ $) {` | `while X != END:` |
| `if (X = a) pop the stack and let a be the next symbol of w;` | `if X == a: stack.pop(); position += 1; a = symbols[position]` |
| `else if (X is a terminal) error();` | `elif not is_nonterminal(X): return None` |
| `else if (M[X, a] is an error entry) error();` | `elif (X, a) not in self.table: return None` |
| `else if (M[X, a] = X → Y1…Yk) {` | `else: production = ...self.table[(X, a)][0]` |
| `output the production; pop the stack;` | `stack.pop()` (y se anota en `trace`) |
| `push Yk, …, Y1 onto the stack, with Y1 on top;` | `for Y, child in reversed(list(zip(production.body, children))): stack.append((Y, child))` |

Detalles importantes:

1. **La pila es una lista de Python con la cima al final.** `stack[-1]` es la cima, `append` apila y `pop()` desapila.
2. **La pila guarda pares `(símbolo, nodo)`**, no solo símbolos. Así, al expandir un no terminal, sabemos **qué nodo del árbol** le corresponde y le colgamos los hijos. El libro lo sugiere: "Additional code could be executed here, for example, code to construct a node in a parse tree".
3. **Construcción del árbol al expandir `X -> Y1…Yk`:**
   ```python
   node.production = production
   children = [Node(Y) if is_nonterminal(Y) else terminal_leaf(Y) for Y in production.body]
   node.children = children if children else [epsilon_leaf()]
   ```
   Se crea un hijo por símbolo del cuerpo: los terminales con su `lexval` y los no terminales vacíos, que se completarán al expandirlos. Si el cuerpo es vacío (`X -> ε`), el único hijo es la hoja ε.
4. **Apilar en orden inverso:** `zip` empareja cada símbolo con su nodo hijo, y `reversed` los recorre del último al primero, de modo que **Y1 queda en la cima**. Si el cuerpo es vacío, no se apila nada.
5. **Aceptación (líneas 138–141):** al salir del `while`, la pila llegó a `$`. Se acepta **solo si** la entrada también está en `$` (`accepted = a == END`). Si sobra entrada, es error. El libro lo deja implícito, pero hay que comprobarlo.
6. Si la cadena tiene un carácter que no es terminal de la gramática, la celda `(X, a)` no existe o `X == a` nunca se cumple, así que la respuesta es `no`. No hace falta validarlo aparte.
7. La primera línea de `parse` (`if not self.is_ll1: raise ...`) impide usar el parser sobre una tabla con conflictos. Con una gramática recursiva por la izquierda, el parser podría expandir `S -> S+T` para siempre.
8. **`trace`:** si se pasa una lista, `_record` agrega una fila **antes** de cada acción, con las columnas de la Fig. 4.21 (MATCHED, STACK con la cima a la izquierda, INPUT, ACTION). Si es `None`, no se hace nada.

### 7.5 Impresión: `table_lines()` y `format_grid(rows)` (líneas 152–169)

- `table_lines` arma una matriz de textos: una fila por no terminal, una columna por terminal más `$`. Las celdas con conflicto muestran las producciones separadas por `|`.
- `format_grid` alinea las columnas calculando el ancho máximo de cada una. `slr1.py` y los programas también la usan.

---

## 8. `parsing/slr1.py`: autómata LR(0), tabla y parser SLR(1) (ítem 2)

[Abrir archivo](entrega/parsing/slr1.py). Implementa **§4.6.2, §4.6.3 y §4.6.4**.

### 8.1 Representación (líneas 16–20)

- **Ítem LR(0)** = par `(número_de_producción, posición_del_punto)`. Es lo que sugiere el libro en el recuadro "Representing Item Sets". Ejemplo: `(4, 1)` con la producción 4 = `B -> bBc` es `B -> b·Bc`.
- **Estado** = `frozenset` de ítems. Como es inmutable se puede usar como clave de diccionario (`number_of[estado]`), y dos estados con los mismos ítems son iguales.
- **Acciones:** tuplas `("shift", j)`, `("reduce", p)` y `("accept",)`.

### 8.2 `__init__` (líneas 25–45): gramática aumentada

```python
self.productions = [Production(AUGMENTED_START, (grammar.start,))] + grammar.productions
```

- **Gramática aumentada G':** la producción 0 es `S' -> S` y la producción `i ≥ 1` es la producción `i-1` original. Así los `r1`, `r2`… de la tabla coinciden con la numeración del libro (Fig. 4.37: (1) E → E+T, (2) E → T…).
- `by_head` es como en `Grammar`, pero para G'.
- **`self.symbols`** define el orden en que se prueban los símbolos en GOTO: primero los no terminales y luego los terminales en orden de aparición. Esto solo afecta **la numeración** de los estados. Con este orden, la gramática del Ejemplo 1 da **exactamente** los estados I0–I11 y la tabla de las Figs. 4.31 y 4.37 del libro, lo que comprueba una de las pruebas automáticas.
- Luego se construyen la colección canónica, la tabla y los conflictos. **`is_slr1` es `True` si y solo si no hay conflictos** (Algoritmo 4.46).

### 8.3 `closure(items)` (líneas 49–68): Fig. 4.32

```python
J = set(items)
changed = True
while changed:                                   # repeat ... until
    changed = False
    for production_index, dot in list(J):
        body = self.productions[production_index].body
        if dot < len(body) and is_nonterminal(body[dot]):   # A -> α·Bβ
            B = body[dot]
            for b_index in self.by_head[B]:                  # cada B -> γ
                if (b_index, 0) not in J:
                    J.add((b_index, 0))                      # agregar B -> ·γ
                    changed = True
return frozenset(J)
```

- `dot < len(body)` significa que el punto no está al final; `body[dot]` es el símbolo justo después del punto.
- Si ese símbolo es un no terminal B, se agregan los ítems `B -> ·γ` (punto al inicio: `(b_index, 0)`) de **todas** las producciones de B.
- `list(J)` hace una copia para recorrer, porque no se puede modificar un conjunto mientras se recorre.
- El `while changed` es el `repeat … until no more items are added` del libro. Hace falta porque un ítem nuevo puede tener otro no terminal después del punto. Así funciona `E' -> ·E` ⇒ `E -> ·T` ⇒ `T -> ·F` ⇒ `F -> ·(E)` en el Ejemplo 4.40.
- **Caso ε:** `B -> ε` tiene cuerpo vacío, así que su ítem es `(b, 0)` con `0 == len(body)`. Es a la vez **inicial y completo** (`B -> ·`). Más adelante genera una reducción.

### 8.4 `goto(items, X)` (líneas 70–80)

```python
moved = set()
for production_index, dot in items:
    body = self.productions[production_index].body
    if dot < len(body) and body[dot] == X:
        moved.add((production_index, dot + 1))      # mover el punto sobre X
return self.closure(moved) if moved else frozenset()
```

Es la definición del libro: se toman los ítems con X justo después del punto, se avanza el punto y se toma la clausura. Si ninguno tiene X después del punto, GOTO es vacío, es decir, no hay transición.

### 8.5 `canonical_collection()` (líneas 82–111): Fig. 4.33

```python
states = [self.closure({(0, 0)})]   # I0 = CLOSURE({[S' -> ·S]})
number_of = {states[0]: 0}
transitions = {}
i = 0
while i < len(states):
    for X in self.symbols:
        target = self.goto(states[i], X)
        if not target:
            continue
        if target not in number_of:              # estado nuevo
            number_of[target] = len(states)
            states.append(target)
        transitions[(i, X)] = number_of[target]  # arista i --X--> target
    i += 1
return states, transitions
```

- `states` es la colección C: una lista donde la posición es el número de estado.
- `number_of` permite preguntar en O(1) "¿este conjunto ya está en C? ¿con qué número?".
- **Equivalencia con el libro:** el libro repite rondas "hasta que no se agreguen conjuntos nuevos". Aquí se recorre la lista con un índice `i` **mientras la lista crece**: cada estado nuevo se agrega al final y se procesará cuando `i` llegue a él. Cuando `i` alcanza el final, todos los estados tienen calculados sus GOTO y ninguna ronda más podría agregar nada. Es la misma colección, calculada en una sola pasada (un recorrido en anchura).
- `transitions[(i, X)]` guarda las aristas del autómata. Se usan para los `shift` (X terminal) y para la tabla GOTO (X no terminal).

### 8.6 `build_table(follow)` (líneas 115–149): Algoritmo 4.46

```python
for i, items in enumerate(self.states):
    for production_index, dot in sorted(items):
        production = self.productions[production_index]
        if dot < len(production.body):
            a = production.body[dot]
            if not is_nonterminal(a):                          # regla (a)
                add(i, a, (SHIFT, self.transitions[(i, a)]))
        elif production_index == 0:                            # regla (c)
            add(i, END, (ACCEPT,))
        else:                                                  # regla (b)
            for a in follow[production.head]:
                add(i, a, (REDUCE, production_index))
```

Para cada ítem de cada estado:
- **Regla (a):** el punto está antes de un **terminal** `a`, así que la acción es `shift` al estado `GOTO(Ii, a)`. Si el punto está antes de un no terminal, no se genera acción; eso va en la tabla GOTO.
- **Regla (c):** el ítem es completo y es `S' -> S·` (producción 0), así que se pone `accept` con `$`.
- **Regla (b):** el ítem es completo `A -> α·`, así que se pone `reduce A -> α` en **cada terminal de FOLLOW(A)**. Esto es lo que hace "Simple" al SLR.
- `add` guarda una **lista** de acciones por celda y evita duplicados exactos. Varios ítems de un mismo estado pueden pedir el mismo `shift j`, por ejemplo `B -> ·bBc` y `B -> b·Bc` en I6, y eso no es un conflicto.
- La tabla GOTO se saca de `transitions` filtrando los símbolos no terminales.
- En `__init__`: `self.conflicts` son las celdas con más de una acción. Si hay alguna, **no es SLR(1)**, y eso detecta tanto desplazar/reducir como reducir/reducir.

### 8.7 `parse(tokens, trace)` (líneas 155–203): Algoritmo 4.44

Traducción de la **Fig. 4.36**:

| Fig. 4.36 del libro | Código |
|---|---|
| `let a be the first symbol of w$;` | `symbols = list(tokens) + [END]`; `a = symbols[0]` |
| (pila con s0) | `states = [0]` |
| `while (1) {` | `while True:` |
| `let s be the state on top of the stack;` | `s = states[-1]` |
| `if (ACTION[s, a] = shift t) { push t; let a be the next input symbol; }` | rama `SHIFT`: `states.append(t)`, avanzar `position` |
| `else if (ACTION[s, a] = reduce A → β) {` | rama `REDUCE` |
| `pop |β| symbols off the stack;` | `del states[len(states) - r:]` |
| `let state t now be on top of the stack;` | `t = states[-1]` |
| `push GOTO[t, A] onto the stack;` | `states.append(self.goto_table[(t, production.head)])` |
| `output the production A → β;` | (se anota en `trace`; se crea el nodo A) |
| `} else if (ACTION[s, a] = accept) break;` | rama `ACCEPT`: `return nodes[-1]` |
| `else call error-recovery routine;` | celda vacía: `return None`, es decir, `no` |

Detalles importantes:

1. **Pila paralela de nodos `nodes`:** el libro dice que la pila solo necesita estados, pero para el ítem 3 necesitamos el árbol. `nodes[k]` es el nodo del árbol del símbolo representado por `states[k+1]` (s0 no representa ningún símbolo).
   - Al hacer **shift**, se apila una hoja con su `lexval`.
   - Al hacer **reduce** por `A -> β`, se toman los últimos `r = |β|` nodos, que son exactamente los de β en orden, y se crea un nodo `A` con ellos como hijos. Es el "parsing ascendente construye el árbol desde las hojas" de §4.5.
2. **Reducción por ε (r = 0).** Por eso el código usa `nodes[len(nodes) - r:]` y `del states[len(states) - r:]` en lugar de `nodes[-r:]`. **En Python, `lista[-0:]` es la lista entera**, mientras que `lista[len(lista) - 0:]` es la lista vacía. Con r = 0 no se desapila nada y el nodo A tiene la hoja ε como único hijo.
3. **Aceptación:** al llegar a `accept`, la pila de nodos tiene un solo nodo, `S`, que es la raíz del árbol.
4. **Errores:** si la celda `ACTION[s, a]` no existe, la cadena se rechaza. Esto incluye caracteres que no son terminales de la gramática.
5. `act = cell[0]`: como `parse` solo se usa si la gramática es SLR(1), cada celda tiene una única acción.

### 8.8 Impresión (líneas 218–257)

- `item_text` escribe un ítem con `·`. Se usa `·` y no `.` porque `.` podría ser un terminal de la gramática.
- `action_text` escribe `s5`, `r2` o `acc`, como la Fig. 4.37.
- `automaton_lines` lista la gramática aumentada numerada y, por cada estado, sus ítems y sus transiciones `GOTO(Ii, X) = Ij`. Con esto se puede **dibujar el autómata** para el informe.
- `table_lines` imprime ACTION y GOTO. Un conflicto se ve como `r5/s8`.

---

## 9. `main.py`: el programa de los ítems 1 y 2

[Abrir archivo](entrega/main.py).

### 9.0 `use_utf8_output()` (línea 29)

```python
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")
```

En Windows, cuando la salida se redirige (a un archivo con `>`, o a otro programa), Python usa por defecto la codificación `cp1252`. Esa codificación no tiene el carácter `ε`, así que el programa fallaría con `UnicodeEncodeError` al imprimir el árbol del ítem 3. Esta función obliga a escribir siempre en UTF-8. La llaman `main()` en `main.py` y en `sdd_main.py`. En macOS y Linux no cambia nada, porque ya usan UTF-8.

### 9.1 `make_line_reader(stream)` (línea 40)

```python
def read_line():
    line = stream.readline()
    if line == "":
        return None                 # fin de la entrada (EOF)
    return line.rstrip("\r\n")
```

- `readline()` devuelve `""` **solo** al final del archivo. Una línea vacía de verdad llega como `"\n"`, que después de `rstrip` queda `""`. Así se distinguen "se acabó la entrada" (`None`) y "línea vacía" (`""`), que en el enunciado significa "fin de las cadenas".
- Se lee **línea por línea**, no todo de una vez. Así el programa funciona de forma interactiva: puede mostrar el menú y esperar la respuesta.

### 9.2 `string_to_tokens(line)` (línea 50)

`"e"` es la cadena vacía (`[]`) y cualquier otra se separa en caracteres. El enunciado dice "the empty string is given as a line containing only e". El `$` lo agrega cada parser, porque "The strings that your program receives do not include it: your program must append it".

### 9.3 `parse_strings(parser, read_line, show_trace)` (línea 55)

Bucle: lee una línea; si es `None` (EOF) o vacía, termina. Si no, la analiza e imprime `yes` si `parse` devolvió un árbol y `no` si devolvió `None`. Con `--trace`, imprime antes la tabla de pasos.

### 9.4 `main()` (líneas 103–155)

1. **Opciones** con `argparse`: `--sets`, `--table`, `--automaton` y `--trace`. Son `store_true`, es decir, `True` si aparecen. Luego se llama a `use_utf8_output()`.
2. **Lectura de la gramática.** Si hay un error de formato, se imprime en `stderr` y se termina con código 1.
3. **Ítem 1:** `compute_first` y `compute_follow`. Con `--sets` se imprimen.
4. **Ítem 2:** se construyen **los dos** parsers, porque hay que saber si la gramática es LL(1) **y** si es SLR(1).
5. **Los 4 casos del enunciado (§2.2.2):**
   ```python
   if ll1.is_ll1 and slr1.is_slr1:      # caso 1: menú T/B/Q
   elif ll1.is_ll1:                     # caso 2: "Grammar is LL(1)."
   elif slr1.is_slr1:                   # caso 3: "Grammar is SLR(1)."
   else:                                # caso 4: "Grammar is neither LL(1) nor SLR(1)."
   ```
   - **Caso 1:** se imprime el `PROMPT` exacto del enunciado y se lee una letra. `T` usa LL(1), `B` usa SLR(1) y `Q` termina. Después de cada bloque de cadenas se vuelve a preguntar. Si la letra no es válida, se vuelve a preguntar. `.upper()` acepta también minúsculas. Si se acaba la entrada (`None`), el programa termina.
   - `flush=True` fuerza a que el texto se muestre de inmediato, importante en modo interactivo.
6. `return 0` y `sys.exit(main())` devuelven el código de salida al sistema.

> **Salida exacta:** sin las opciones extra, el programa imprime **solo** lo que pide el enunciado. Las pruebas comparan carácter por carácter con los ejemplos de la sección 5.

---

## 10. `sdd/evaluator.py`: el evaluador general de SDD (ítem 3)

[Abrir archivo](entrega/sdd/evaluator.py). Implementa **§5.1 y §5.2**. **Este archivo no sabe nada de nuestra SDD concreta**, tal como pide el enunciado: "The evaluator must not know anything about your particular SDD: changing the SDD must only require changing this data".

### 10.1 Convención de posiciones

En una producción `A -> X1 X2 … Xn`, la **posición 0** es la cabeza A y la **posición i** es el símbolo Xᵢ del cuerpo.

Así una regla se puede guardar sin depender de nombres repetidos. Por ejemplo, en `R -> ,IR` hay dos R (la cabeza y el R1 del cuerpo), pero en posiciones distintas: R = 0, `,` = 1, I = 2, R1 = 3. Esto resuelve el problema de los subíndices que el libro menciona en la nota al pie 2 de §5.2.1.

### 10.2 Las estructuras de datos (líneas 28–76)

```python
@dataclass(frozen=True)
class Attribute:
    kind: str      # SYN o INH
    type: str      # "int", ...
    meaning: str   # significado
```

`Attribute` es una fila de la **tabla de atributos** del paso 2.1 del enunciado.

```python
@dataclass(frozen=True)
class Rule:
    target: tuple   # (posición, atributo) que DEFINE
    deps: tuple     # ((posición, atributo), ...) que USA
    fn: object      # la función que calcula el valor
    text: str       # la regla escrita como en el libro
```

`Rule` es **exactamente** lo que pide el paso 5.1: "for each rule the attribute it defines, the attributes it uses, and the function that computes it". Por ejemplo, `E.d = L.d + 1` en `L -> [E]` es `Rule(target=(2,"d"), deps=((0,"d"),), fn=lambda d: d + 1, text="E.d = L.d + 1")`.

`SDD` agrupa:
- `attributes`: `{símbolo: {nombre: Attribute}}`.
- `rules`: `{"A -> cuerpo": [Rule, …]}`, con la clave en el mismo formato que `str(Production)`.
- `main_attribute`: el atributo principal de S que se imprime al final.

Además:
- `rules_for(production)` devuelve las reglas de una producción, o `[]`.
- `kind(symbol, name)` devuelve `SYN`, `INH` o `None`. **Los terminales solo tienen `lexval`, que es sintetizado**, como dice §5.1.1: "Terminals can have synthesized attributes, but not inherited attributes".

Hay dos excepciones: `SDDError` (la SDD está mal definida) y `CircularSDDError` (hay un ciclo; guarda las etiquetas del ciclo para mostrarlo).

### 10.3 `validate_sdd(grammar, sdd)` (líneas 87–142)

Comprueba lo que el enunciado pide revisar ("Check each of the following for every production, as described in Section 5.1.1"):

1. **S no tiene heredados** (líneas 97–99).
2. No hay reglas para producciones que no existen (líneas 101–104). Así se detecta, por ejemplo, un error al escribir la clave.
3. Para cada producción y cada regla:
   - la posición existe;
   - **no se define un atributo de un terminal** ("Terminals only have synthesized attributes provided by the scanner");
   - **en la posición 0 solo se definen sintetizados de la cabeza**;
   - **en las posiciones ≥ 1 solo se definen heredados de no terminales del cuerpo**;
   - los atributos usados existen ("using only attributes of the symbols of that same production").
4. **Cada sintetizado de la cabeza y cada heredado de cada no terminal del cuerpo se define exactamente una vez** (final de la función). Se arma la lista `required` y se cuenta con un `Counter` cuántas veces se define cada uno: 0 es "never defined" y más de 1 es "defined more than once".

Devuelve la lista de problemas. `sdd_main.py` no evalúa nada si la lista no está vacía.

### 10.4 `classify_sdd(grammar, sdd)` (líneas 145–183)

Aplica las definiciones del libro:
- **S-atribuida (§5.2.3):** todos los atributos declarados son sintetizados (línea 154).
- **L-atribuida (§5.2.4):** para cada regla que define un **heredado** `Xi.a` (posición `i ≥ 1`), revisa cada atributo que usa, en la posición `j`:
  - `j == 0` y es heredado de la cabeza: permitido por la condición **(a)**.
  - `1 ≤ j < i`, es decir, un símbolo a la izquierda: permitido por la condición **(b)**.
  - `j == i`, el mismo símbolo: permitido solo si no forma ciclos, condición **(c)**. El código no puede asegurarlo en general, así que responde "only if condition (c) holds" (`None`).
  - Cualquier otro caso (un símbolo a la derecha, o un **sintetizado** de la cabeza) **no es L-atribuida** (Ejemplo 5.9 del libro).

  Las reglas que definen sintetizados (posición 0) siempre están permitidas.

Nuestra SDD da **S-attributed: no, L-attributed: yes** (`--rules`).

### 10.5 `DependencyGraph` y `build_dependency_graph` (líneas 186–237): §5.2.1

```python
class DependencyGraph:
    vertices   # vértice k -> (nodo, atributo)
    number     # (id del nodo, atributo) -> k
    edges      # k -> lista de sucesores
    rule_of    # k -> (Rule, nodo donde se aplica)  (quién lo define)
```

- `vertex(node, name)` crea el vértice de `node.name` la primera vez y después devuelve el mismo número. Así cada atributo de cada nodo tiene **un único vértice** ("one vertex for each attribute of each node").

```python
for node in preorder(root):
    if node.is_leaf():
        if not node.is_epsilon():
            graph.vertex(node, LEXVAL)            # las hojas aportan su lexval
        continue
    for rule in sdd.rules_for(node.production):   # instanciar las reglas
        target = graph.vertex(node_at(node, rule.target[0]), rule.target[1])
        if target in graph.rule_of:
            raise SDDError(...)                   # definido dos veces
        graph.rule_of[target] = (rule, node)
        for position, name in rule.deps:
            source = graph.vertex(node_at(node, position), name)
            graph.edges[source].append(target)    # arista USADO -> DEFINIDO
```

Es exactamente el paso 5.3 del enunciado: "For each internal node, instantiate the rules of its production: for each rule, add one edge from each attribute it depends on to the attribute it defines. The leaves provide their lexval."

- **`node_at(node, position)`** (línea 207) traduce una posición de la regla a un nodo concreto del árbol: la posición 0 es el propio nodo y la posición i es su hijo `i-1` (las listas de Python empiezan en 0).
- **Instanciar** significa que la regla `E.d = L.d + 1` de `L -> [E]` se convierte, en el nodo L#2, en la arista `L#2.d -> E#4.d`; y en el nodo L#10, en `L#10.d -> E#12.d`. La regla es una sola, pero aparece una vez por cada nodo donde se usa la producción.
- **Dirección de las aristas:** `edges[source].append(target)`, del atributo **usado** al **definido**. El enunciado advierte que dibujarlas al revés es un error común.
- `rule_of[target]` recuerda **qué regla y en qué nodo** define cada vértice, para poder evaluarlo después.

### 10.6 `topological_order(graph)` (líneas 240–261): §5.2.2

```python
indegree = [0] * len(graph.vertices)
for v in graph.edges:
    for w in graph.edges[v]:
        indegree[w] += 1                 # aristas que ENTRAN a w
ready = deque(v for v in range(len(graph.vertices)) if indegree[v] == 0)
order = []
while ready:
    v = ready.popleft()                  # un vértice sin aristas de entrada
    order.append(v)
    for w in graph.edges[v]:             # "eliminar" v del grafo
        indegree[w] -= 1
        if indegree[w] == 0:
            ready.append(w)
if len(order) < len(graph.vertices):
    raise CircularSDDError(find_cycle(graph, indegree))
return order
```

Es el **algoritmo de Kahn**, que es literalmente la demostración del libro en §5.2.2: "we can surely find a node with no edge entering. […] Make this node the first in the topological order, remove it from the dependency graph, and repeat the process on the remaining nodes".

- `indegree[w]` cuenta cuántas aristas entran a `w`, es decir, de cuántos atributos depende aún.
- `ready` contiene los vértices que ya no dependen de nada pendiente.
- "Eliminar" `v` del grafo equivale a restar 1 al grado de entrada de sus sucesores.
- **Si al final no se ordenaron todos los vértices, hay un ciclo.** Si quedan vértices, todos tienen aristas de entrada desde vértices que tampoco se pudieron ordenar. El libro dice que en ese caso no hay ningún orden topológico.

### 10.7 `find_cycle(graph, indegree)` (líneas 264–281)

Para mostrar **cuál** es el ciclo, se usa la otra mitad del argumento del libro: "we could proceed from predecessor to predecessor until we came back to some node we had already seen, yielding a cycle".

- Se construyen los predecesores.
- Se parte de un vértice que quedó con `indegree > 0`.
- Se retrocede siempre a un predecesor que también quedó sin ordenar, hasta repetir un vértice.
- El tramo entre las dos apariciones es el ciclo. Se invierte para mostrarlo en el sentido de las aristas.

### 10.8 `evaluate(root, sdd)` (líneas 284–307)

```python
number_nodes(root)                               # nombres L#2, E#4, ...
graph = build_dependency_graph(root, sdd)
order = topological_order(graph)                 # o CircularSDDError
computed = []
for v in order:                                  # se evalúa EN ESE ORDEN
    node, name = graph.vertices[v]
    if v in graph.rule_of:
        rule, owner = graph.rule_of[v]
        arguments = [node_at(owner, position).attrs[dep] for position, dep in rule.deps]
        node.attrs[name] = rule.fn(*arguments)   # aplicar la regla
        computed.append(v)
    elif name != LEXVAL:
        raise SDDError(...)                      # usado pero nunca definido
```

- Para cada vértice, en orden topológico:
  - Si una regla lo define, se buscan los valores de sus dependencias (que **ya están calculados**, porque el orden lo garantiza) y se llama a la función de la regla. `rule.fn(*arguments)` pasa la lista como argumentos separados: `fn(a, b)`.
  - Si es un `lexval`, ya tiene valor desde que se creó la hoja.
- Al final se reordenan los atributos de cada nodo según la tabla de atributos, solo para que el árbol impreso se lea mejor.
- **Esto es lo que el enunciado pide en vez de "Evaluating the tree recursively in a fixed order":** el orden lo decide el grafo, no un recorrido fijo del árbol. Por eso funciona para **cualquier** SDD no circular, sea S-atribuida, L-atribuida o ninguna de las dos.

---

## 11. `sdd/nested_list_sdd.py`: nuestra SDD

[Abrir archivo](entrega/sdd/nested_list_sdd.py). Este archivo **solo contiene datos**: la gramática, la tabla de atributos y las reglas. No tiene ningún algoritmo.

### 11.1 La gramática (paso 1 del enunciado)

```
5
S -> L
L -> [E]
E -> IR e
R -> ,IR e
I -> L 0 1 2 3 4 5 6 7 8 9
```

- **Lenguaje:** listas anidadas de dígitos, por ejemplo `[]`, `[5]`, `[1,[2,3]]` o `[[],[4]]`.
- **G1:** sigue el formato de §2.2 y es **LL(1) y SLR(1)**. Lo comprueba la prueba `test_grammar_is_ll1_and_slr1`, y puedes verlo con:
  ```bash
  printf '5\nS -> L\nL -> [E]\nE -> IR e\nR -> ,IR e\nI -> L 0 1 2 3 4 5 6 7 8 9\n' | python3 main.py --table --automaton
  ```
- **G2:** tiene **5 no terminales** (S, L, E, R, I) y **17 producciones**. **L es recursivo**, porque L ⇒ [E] ⇒ [IR] ⇒ [LR]; R también lo es, por `R -> ,IR`.
- **G3:** no es una gramática ni una SDD del libro ni del enunciado.

¿Por qué `E -> IR | ε` y `R -> ,IR | ε` en lugar de `E -> E,I | I`? Porque la versión recursiva por la izquierda **no sería LL(1)**. Con esta forma, después de leer un elemento, el siguiente símbolo decide: `,` significa que hay otro elemento y `]` que se terminó la lista. Es la misma idea que E' en la gramática 4.28 del libro.

### 11.2 La traducción

Se calcula la **suma ponderada por profundidad**: cada dígito se multiplica por la profundidad de la lista que lo contiene, y la lista exterior tiene profundidad 1.

| Cadena | Cálculo | S.v |
|---|---|---|
| `[]` | (nada) | 0 |
| `[5]` | 5·1 | 5 |
| `[1,[2,3]]` | 1·1 + 2·2 + 3·2 | 11 |
| `[[[[5]]]]` | 5·4 | 20 |
| `[7,0,[1,[2]],9]` | 7·1 + 0·1 + 1·2 + 2·3 + 9·1 | 24 |

### 11.3 Tabla de atributos (paso 2.1)

| Símbolo | Atributo | Tipo de atributo | Tipo de dato | Significado |
|---|---|---|---|---|
| S | v | sintetizado | int | suma ponderada de toda la lista (**atributo principal**) |
| L | d | heredado | int | profundidad del nivel donde aparece esta lista (0 para la exterior) |
| L | s | sintetizado | int | suma ponderada de los dígitos dentro de esta lista |
| E | d | heredado | int | profundidad de los elementos de esta lista |
| E | s | sintetizado | int | suma ponderada de esos elementos |
| R | d | heredado | int | profundidad de los elementos restantes |
| R | s | sintetizado | int | suma ponderada de los elementos restantes |
| I | d | heredado | int | profundidad de este elemento |
| I | s | sintetizado | int | aporte de este elemento a la suma |
| terminales | lexval | sintetizado (léxico) | char | el propio carácter |

### 11.4 Reglas semánticas (paso 2.2)

| Producción | Reglas semánticas |
|---|---|
| S → L | L.d = 0;  S.v = L.s |
| L → [ E ] | E.d = L.d + 1;  L.s = E.s |
| E → I R | I.d = E.d;  R.d = E.d;  E.s = I.s + R.s |
| E → ε | E.s = 0 |
| R → , I R₁ | I.d = R.d;  R₁.d = R.d;  R.s = I.s + R₁.s |
| R → ε | R.s = 0 |
| I → L | L.d = I.d;  I.s = L.s |
| I → dígito (0…9) | I.s = I.d × int(dígito.lexval) |

**Idea:**
- La **profundidad baja** por el árbol con el heredado `d`, y aumenta en 1 al entrar en cada `[…]`.
- La **suma sube** con el sintetizado `s`.
- En cada dígito, la profundidad (que viene de arriba) y el valor (`lexval`, que viene de la hoja) se encuentran en `I.s = I.d × lexval`.

**Así se escribe en el código**, por ejemplo para `L -> [E]` (posiciones: 0 = L, 1 = `[`, 2 = E, 3 = `]`):

```python
"L -> [E]": [
    Rule(target=(2, "d"), deps=((0, "d"),), fn=lambda d: d + 1, text="E.d = L.d + 1"),
    Rule(target=(0, "s"), deps=((2, "s"),), fn=lambda s: s, text="L.s = E.s"),
],
```

- `target=(2, "d")`: se define el atributo `d` del símbolo en la posición 2 (E).
- `deps=((0, "d"),)`: se usa `d` de la posición 0 (L). La coma final hace que sea una tupla de un elemento.
- `fn=lambda d: d + 1`: recibe el valor de L.d y devuelve L.d + 1.

Las 10 producciones `I -> 0` … `I -> 9` se generan con un `for` (líneas 77–83), porque todas tienen la misma regla. `deps=((0, "d"), (1, "lexval"))` usa el `d` del propio I y el `lexval` de la hoja del dígito. `int(lexval)` convierte el carácter `'7'` en el número 7.

### 11.5 Revisión (pasos 2 y 4)

- **Cada regla define un sintetizado de la cabeza o un heredado del cuerpo**, y cada uno se define **exactamente una vez**. `validate_sdd` lo verifica y devuelve `[]`.
- **S no tiene heredados.** Hay al menos un sintetizado (`s`, `v`) y un heredado (`d`).
- **Clasificación:**
  - **No es S-atribuida**, porque `d` es heredado.
  - **Es L-atribuida**, porque todos los heredados se calculan **solo con el heredado de la cabeza**: `E.d = L.d + 1`, `I.d = E.d`, `R.d = E.d`, `I.d = R.d`, `R₁.d = R.d` y `L.d = I.d` cumplen la condición (a) de §5.2.4. `L.d = 0` es una constante. Todo lo demás es sintetizado.

### 11.6 `build_circular_sdd()` (paso 6)

Copia las reglas y cambia, en `S -> L`, `L.d = 0` por **`L.d = L.s`**. Ahora:

```
L.d → E.d → I.d → I.s → E.s → L.s → L.d     (ciclo)
```

**Detalle interesante para la sustentación:** con `[]` **no** hay ciclo. `E -> ε` calcula `E.s = 0` sin usar `E.d`, así que L.s no depende de L.d. Con `[1]` sí hay ciclo. **La circularidad depende del árbol**, por eso el evaluador la busca en el grafo de cada cadena (ver la nota al pie 1 de §5.1.2 del libro). El programa lo muestra:

```
Input: []
...
Result: S.v = 0

Input '[1]': the SDD is circular, so it cannot be evaluated.
Cycle found in the dependency graph: E#4.d -> I#5.d -> I#5.s -> E#4.s -> L#2.s -> L#2.d -> E#4.d
```

---

## 12. `sdd_main.py`: el programa del ítem 3

[Abrir archivo](entrega/sdd_main.py).

1. **Opciones:** `--parser`, `--rules`, `--graph` y `--circular`.
2. **Gramática:** se lee de `GRAMMAR_TEXT` con `grammar_from_text`. El enunciado lo permite: "The grammar may be read in the format of Section 2.2; the SDD may be written in your source code".
3. **SDD:** `build_sdd()` o `build_circular_sdd()`.
4. **`validate_sdd`:** si la SDD tiene problemas, se imprimen y el programa termina.
5. **`--rules`:** `print_rules` imprime la gramática, la tabla de atributos, la tabla Producción | Reglas y la clasificación. Es material directo para los pasos 2 y 4 del informe.
6. **Parser:** se construye el del ítem 2 elegido y se verifica que la gramática sea LL(1) o SLR(1) según el caso. Así se cumple "you must parse the strings with your own parser from Item 2".
7. **Bucle de cadenas** (hasta una línea vacía):
   - `parser.parse(...)`: si devuelve `None`, se imprime `no`.
   - `evaluate(tree, sdd)`: si lanza `CircularSDDError`, se imprime el ciclo y **el programa se detiene**, porque el enunciado dice "report that the SDD is circular and stop".
   - Si no, se imprime:
     - el **árbol anotado** con `format_tree`;
     - con `--graph`, los vértices y aristas;
     - el **orden de evaluación**: los atributos calculados por reglas, numerados en el orden topológico, con su valor;
     - el **valor del atributo principal**: `Result: S.v = …`.

> `from main import make_line_reader, string_to_tokens` reutiliza las funciones de lectura de `main.py`, así que la forma de leer cadenas es la misma en los dos programas.

---

## 13. `tests/test_project.py`: las pruebas

[Abrir archivo](entrega/tests/test_project.py). Hay 21 pruebas con `unittest`, la biblioteca estándar.

| Clase | Qué comprueba |
|---|---|
| `TestStatementExamples` | La **salida exacta** de los 3 ejemplos del enunciado, ejecutando `main.py` como lo haría el profesor (`subprocess` con el archivo como entrada). También `--sets`, el caso "solo LL(1)" y el caso "ninguno". |
| `TestFirstFollow` | FIRST y FOLLOW del **Ejemplo 4.30 del libro**, y una cadena de no terminales anulables. |
| `TestParsers` | Que la tabla SLR coincide celda a celda con la **Fig. 4.37 del libro**. Que **los dos parsers aceptan exactamente el lenguaje** a^n d b^m c^m en **todas** las cadenas de longitud ≤ 6 sobre {a, b, c, d} (5461 cadenas), y que construyen **el mismo árbol**. La cadena vacía, los símbolos desconocidos, la recursión izquierda, un conflicto reducir/reducir y las gramáticas mal escritas. |
| `TestSDD` | Los valores de la SDD con los dos parsers, las cadenas fuera del lenguaje, la validación, la clasificación, la variante circular, la salida del programa y que **el evaluador es general**: con la SDD de paréntesis del enunciado (escrita como datos dentro de la prueba), el mismo evaluador da S.m = 2 para `(())()` sin cambiar una línea de `evaluator.py`. |

---

## 14. Cómo modificar el código

El enunciado dice que en la sustentación pueden pedirles "modify your code on the spot". Estos son los cambios más probables y dónde hacerlos.

| Te piden… | Dónde y cómo |
|---|---|
| Cambiar una regla de la SDD (por ejemplo, sumar en vez de multiplicar) | En `sdd/nested_list_sdd.py`, cambiar la `fn` (y el `text`) de esa `Rule`. **No se toca el evaluador.** |
| Agregar un atributo a la SDD (por ejemplo, contar los dígitos) | Agregar el atributo a `ATTRIBUTES` y una `Rule` que lo defina **en cada producción** donde corresponde. `validate_sdd` avisa si falta alguna. |
| Hacer la SDD circular | `python3 sdd_main.py --circular`, o cambiar una regla para que un atributo dependa de sí mismo a través del árbol. |
| Imprimir los conjuntos intercalados | En `sets_report` (`first_follow.py`), un solo `for` que agregue `First(A)` y `Follow(A)`. |
| Cambiar el formato de salida del árbol | `format_tree` en `parse_tree.py`. |
| Mostrar el análisis paso a paso | Ya existe: `--trace`. |
| Explicar por qué una gramática no es LL(1) / SLR(1) | `--table` muestra las condiciones violadas y `--automaton` los conflictos (`ACTION[2, =] = r5, s8`). |
| Que el menú acepte otra letra | `main()` en `main.py`, el bloque `if choice == ...`. |

**Ejercicio recomendado antes de sustentar:** cada integrante debería tomar una gramática nueva, calcular a mano FIRST/FOLLOW, la tabla LL(1) y el autómata con la tabla SLR(1), y luego comparar con:

```bash
python3 main.py --sets --table --automaton --trace
```

Ojo: la numeración de los estados puede variar si se recorren los símbolos en otro orden. El programa usa primero los no terminales y luego los terminales en orden de aparición.

---

## 15. Qué falta para la entrega

El código está completo. **Lo que todavía no está hecho:**

1. **`README.md`:** escribir los **nombres completos** de los integrantes, en lugar de `<Full name 1>`, etc. Revisar también el párrafo sobre el uso de IA.
2. **El informe en PDF** (preferiblemente en LaTeX), en la raíz de la entrega. Debe contener:
   - Las secciones del libro seguidas y las estructuras de datos. Pueden usar la [sección 2](#2-mapa-del-código) y la tabla de la guía teórica.
   - **Ítems 1 y 2:** una gramática propia que no esté en el enunciado, con su salida de `--sets`, `--table` o `--automaton`, y una cadena con `--trace`.
   - **Ítem 3:** la gramática, la tabla de atributos y las reglas (`--rules`); el ejemplo a mano con una cadena de al menos 4 terminales, con el árbol anotado, el grafo de dependencias y un orden topológico (pueden apoyarse en `--graph`); la clasificación; y las pruebas del paso 6 (al menos 5 cadenas y la prueba circular). `tests/inputs/sdd_strings.txt` tiene 5 cadenas: la más corta (`[]`), una con anidamiento profundo, dos normales y una que no pertenece al lenguaje.
   - Los problemas que encontraron y cómo los resolvieron.
3. **Borrar `__pycache__`** antes de comprimir (ver la sección 1.4).
4. **Confirmar con el profesor** el orden de las líneas de `--sets`.
5. **Revisar que la SDD les convenza** o cambiarla por una propia. El enunciado sugiere consultar si hay dudas sobre G3, así que pueden mostrársela al profesor antes.
