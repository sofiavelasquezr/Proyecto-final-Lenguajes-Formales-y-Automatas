# Guía teórica del proyecto: FIRST/FOLLOW, LL(1), SLR(1) y SDD

Basada en Aho, Lam, Sethi y Ullman, *Compilers: Principles, Techniques, and Tools* (2.ª ed., 2007), secciones **4.4, 4.5, 4.6, 5.1 y 5.2**, que son las que pide el enunciado (`sdt_revised.pdf`).

> **Cómo usar esta guía.** Cada sección explica un tema del libro y luego dice qué significa para el proyecto (los recuadros **"En el proyecto"**). Los números de figura, algoritmo y ejemplo son los del libro, para que puedan citarlos en el informe, como exige el enunciado.
>
> Todos los conjuntos, tablas, autómatas y trazas de los ejemplos propios (los que no son del libro) se verificaron con un programa. Los números de los estados LR(0) dependen del orden en que se construyen; si su programa los numera distinto, no está mal.

---

## Índice

0. [Conceptos previos (repaso)](#0-conceptos-previos-repaso)
1. [Mapa: qué pide el proyecto y dónde está en el libro](#1-mapa-qué-pide-el-proyecto-y-dónde-está-en-el-libro)
2. [§4.4 Análisis descendente (top-down)](#2-44-análisis-descendente-top-down)
   - 2.1 [§4.4.1 Descenso recursivo](#21-441-descenso-recursivo)
   - 2.2 [§4.4.2 FIRST y FOLLOW](#22-442-first-y-follow)
   - 2.3 [§4.4.3 Gramáticas LL(1) y tabla predictiva](#23-443-gramáticas-ll1-y-tabla-predictiva)
   - 2.4 [§4.4.4 Parser predictivo no recursivo](#24-444-parser-predictivo-no-recursivo)
3. [§4.5 Análisis ascendente (bottom-up)](#3-45-análisis-ascendente-bottom-up)
4. [§4.6 LR y SLR](#4-46-lr-y-slr)
   - 4.1 [Ítems LR(0), CLOSURE, GOTO y el autómata LR(0)](#41-462-ítems-lr0-closure-goto-y-el-autómata-lr0)
   - 4.2 [El algoritmo de análisis LR](#42-463-el-algoritmo-de-análisis-lr)
   - 4.3 [Construcción de la tabla SLR](#43-464-construcción-de-la-tabla-slr)
   - 4.4 [Prefijos viables](#44-465-prefijos-viables)
5. [Los ejemplos del enunciado, resueltos](#5-los-ejemplos-del-enunciado-resueltos)
6. [§5.1 Definiciones dirigidas por la sintaxis (SDD)](#6-51-definiciones-dirigidas-por-la-sintaxis-sdd)
7. [§5.2 Orden de evaluación: grafos de dependencias](#7-52-orden-de-evaluación-grafos-de-dependencias)
8. [El ítem 3 paso a paso, con un ejemplo completo](#8-el-ítem-3-paso-a-paso-con-un-ejemplo-completo)
9. [Del libro al código: decisiones de implementación](#9-del-libro-al-código-decisiones-de-implementación)
10. [Teoremas y propiedades para justificar](#10-teoremas-y-propiedades-para-justificar)
11. [Errores frecuentes](#11-errores-frecuentes)
12. [Preguntas probables en la sustentación](#12-preguntas-probables-en-la-sustentación)

---

## 0. Conceptos previos (repaso)

Estos conceptos vienen de §4.2 y el libro los usa todo el tiempo en las secciones del proyecto.

| Concepto | Definición |
|---|---|
| **Gramática libre de contexto (GLC)** | G = (N, T, P, S): no terminales, terminales, producciones `A → α` y símbolo inicial. |
| **Cabeza / cuerpo** | En `A → α`, la cabeza es `A` y el cuerpo es `α`. |
| **Notación** | `A, B, C` son no terminales; `a, b, c` son terminales; `X, Y, Z` son símbolos cualesquiera; `α, β, γ` son cadenas de símbolos (pueden ser vacías); `w, x, y, z` son cadenas de terminales. |
| **Derivación** `⇒` | Se reemplaza un no terminal por el cuerpo de una de sus producciones: `αAβ ⇒ αγβ` si `A → γ`. |
| `⇒*` y `⇒+` | Cero o más pasos, y uno o más pasos. |
| **Derivación por la izquierda** `⇒lm` | En cada paso se reemplaza el no terminal **más a la izquierda**. |
| **Derivación por la derecha** `⇒rm` | En cada paso se reemplaza el no terminal **más a la derecha**. También se llama derivación canónica. |
| **Forma sentencial** | Cualquier α tal que `S ⇒* α`. Si se obtiene por la derecha, es una **forma sentencial derecha**. |
| **Árbol de análisis (parse tree)** | La raíz es S, los nodos internos son no terminales con sus hijos (el cuerpo de la producción aplicada) y las hojas son terminales o ε. |
| **Ambigua** | Hay una cadena con dos árboles distintos (o, lo que es igual, con dos derivaciones por la izquierda distintas). |
| **Recursiva por la izquierda** | Existe `A ⇒+ Aα`. |
| **ε (épsilon)** | La cadena vacía. **En el proyecto se escribe `e`.** |
| **`$`** | Marcador de fin de entrada. No es un símbolo de la gramática. **El programa lo agrega a cada cadena.** |

**Relación con los parsers:**
- Un parser **descendente** (LL) construye una **derivación por la izquierda**, empezando por la raíz.
- Un parser **ascendente** (LR) construye una **derivación por la derecha al revés**, empezando por las hojas.

---

## 1. Mapa: qué pide el proyecto y dónde está en el libro

| Ítem del proyecto | Qué implementar | Sección / algoritmo / figura del libro |
|---|---|---|
| 1. FIRST y FOLLOW | Reglas iterativas de punto fijo; FIRST de cadenas | §4.4.2 (reglas de FIRST, FIRST(X₁…Xₙ) y FOLLOW; Ejemplo 4.30) |
| 2. Prueba LL(1) | Las condiciones de la definición de LL(1) | §4.4.3 (definición al inicio de la sección) |
| 2. Tabla LL(1) | Tabla predictiva M[A, a] | §4.4.3, **Algoritmo 4.31**; Ejemplo 4.32, Fig. 4.17 |
| 2. Parser LL(1) | Parser con pila y tabla, **no recursivo** | §4.4.4, **Algoritmo 4.34**, **Fig. 4.20**; Ejemplo 4.35, Fig. 4.21 |
| 2. Teoría de desplazamiento-reducción | Mangos (handles), conflictos | §4.5 (sobre todo §4.5.4) |
| 2. Autómata LR(0) | Gramática aumentada, CLOSURE, GOTO, colección canónica | §4.6.2, **Fig. 4.32** (CLOSURE), **Fig. 4.33** (items) |
| 2. Tabla SLR(1) | ACTION y GOTO usando FOLLOW | §4.6.4, **Algoritmo 4.46** |
| 2. Parser SLR(1) | Algoritmo de análisis LR | §4.6.3, **Algoritmo 4.44**, **Fig. 4.36** |
| 3. SDD | Atributos sintetizados y heredados, árbol anotado | §5.1.1, §5.1.2 (Figs. 5.1, 5.4) |
| 3. Grafo de dependencias | Una arista desde cada atributo usado hacia el atributo definido | §5.2.1 (Figs. 5.6, 5.7) |
| 3. Orden de evaluación | Ordenamiento topológico y detección de ciclos | §5.2.2 (Ejemplo 5.6) |
| 3. Clasificación | S-atribuida o L-atribuida | §5.2.3, §5.2.4 (Ejemplos 5.7, 5.8, 5.9) |

---

## 2. §4.4 Análisis descendente (top-down)

**Idea.** El análisis descendente construye el árbol **desde la raíz hacia las hojas, en preorden**. Es lo mismo que encontrar una **derivación por la izquierda** de la entrada. El problema central en cada paso es este:

> Si tengo un no terminal A por expandir, ¿qué producción de A aplico?

Un **parser predictivo** responde mirando solo el siguiente símbolo de la entrada (el *lookahead*). Las gramáticas en las que esto siempre funciona con **1** símbolo son las **LL(1)**:
- **L**: lee la entrada de izquierda a derecha (*Left-to-right*).
- **L**: produce una derivación por la izquierda (*Leftmost*).
- **1**: usa un símbolo de *lookahead*.

La gramática que usa el libro como ejemplo en esta sección es la de expresiones **sin recursión izquierda** (gramática 4.28):

```
E  → T E'
E' → + T E' | ε
T  → F T'
T' → * F T' | ε
F  → ( E ) | id
```

### 2.1 §4.4.1 Descenso recursivo

- Hay un procedimiento por cada no terminal (Fig. 4.13). Cada uno elige una producción y recorre su cuerpo: si encuentra un no terminal, llama a su procedimiento; si encuentra un terminal, lo compara con la entrada.
- En general puede necesitar **retroceso (backtracking)**: si una alternativa falla, se devuelve el puntero de la entrada y se prueba otra. El Ejemplo 4.29 usa `S → cAd`, `A → ab | a` con la entrada `cad`: primero prueba `A → ab`, falla y retrocede para probar `A → a`.
- **Una gramática recursiva por la izquierda hace que el descenso recursivo entre en un ciclo infinito.** Al expandir A, puede volver a expandir A sin haber consumido nada de la entrada.

> **En el proyecto:** **no** implementan descenso recursivo. El enunciado exige el parser **con tabla y no recursivo** de §4.4.4. Esta subsección sirve para entender la motivación.

### 2.2 §4.4.2 FIRST y FOLLOW

Son dos funciones de la gramática que se usan para construir **tanto** el parser LL(1) **como** el SLR(1).

#### Definiciones

**FIRST(α)**, donde α es cualquier cadena de símbolos, es el **conjunto de terminales con los que empiezan las cadenas que se derivan de α**. Si `α ⇒* ε`, entonces **ε también está en FIRST(α)**.

**FOLLOW(A)**, donde A es un no terminal, es el **conjunto de terminales `a` que pueden aparecer justo a la derecha de A en alguna forma sentencial**. Es decir, los `a` para los que existe una derivación `S ⇒* αAaβ`. Además, **si A puede ser el símbolo más a la derecha de una forma sentencial, entonces `$` ∈ FOLLOW(A)**.

> Puede que en algún momento de la derivación hubiera símbolos entre A y `a`. Si los había, derivaron ε y desaparecieron (Fig. 4.15).
>
> **FOLLOW nunca contiene ε.** FIRST sí puede contenerlo.

#### Algoritmo para FIRST(X) de cada símbolo X

Se aplican estas reglas **hasta que ningún conjunto FIRST cambie** (iteración de punto fijo):

1. Si X es **terminal**, FIRST(X) = {X}.
2. Si X es no terminal y `X → Y₁Y₂…Yₖ` (con k ≥ 1):
   - Se agrega `a` a FIRST(X) si `a` ∈ FIRST(Yᵢ) y ε está en FIRST(Y₁), …, FIRST(Yᵢ₋₁), es decir, si `Y₁…Yᵢ₋₁ ⇒* ε`.
   - Si ε está en FIRST(Yⱼ) para **todo** j = 1…k, se agrega ε a FIRST(X).
   - En la práctica: todo lo de FIRST(Y₁) (menos ε) entra. Si Y₁ no deriva ε, no se agrega nada más. Si sí lo deriva, se agrega FIRST(Y₂) (menos ε), y así sucesivamente.
3. Si `X → ε` es una producción, se agrega ε a FIRST(X).

#### FIRST de una cadena X₁X₂…Xₙ

Hace falta para la tabla LL(1), porque se aplica al **cuerpo completo** de una producción.

- Se agregan los símbolos de FIRST(X₁) que no son ε.
- Si ε ∈ FIRST(X₁), también los de FIRST(X₂) que no son ε.
- Si ε ∈ FIRST(X₁) y ε ∈ FIRST(X₂), también los de FIRST(X₃) que no son ε, y así sucesivamente.
- **Al final**, se agrega ε si ε ∈ FIRST(Xᵢ) para **todos** los i.
- Caso especial: **FIRST(ε) = {ε}**. Sirve para los cuerpos vacíos y para "lo que queda a la derecha" cuando no queda nada.

#### Algoritmo para FOLLOW(A) de cada no terminal

Se aplican estas reglas **hasta que ningún conjunto FOLLOW cambie**:

1. Se pone `$` en FOLLOW(S), donde S es el símbolo inicial.
2. Si hay una producción `A → αBβ`, todo FIRST(β) **excepto ε** está en FOLLOW(B).
3. Si hay una producción `A → αB`, o una `A → αBβ` con ε ∈ FIRST(β), entonces **todo FOLLOW(A) está en FOLLOW(B)**.

Intuición de la regla 3: si B está al final del cuerpo (o lo que viene después puede desaparecer), lo que sigue a A también puede seguir a B.

> **Detalle importante:** las reglas se aplican a **cada aparición** de B en **cada** cuerpo. Si B aparece dos veces en un mismo cuerpo, se procesan las dos.

#### Ejemplo 4.30 del libro (gramática 4.28)

| | FIRST | FOLLOW |
|---|---|---|
| E | { (, id } | { ), $ } |
| E' | { +, ε } | { ), $ } |
| T | { (, id } | { +, ), $ } |
| T' | { *, ε } | { +, ), $ } |
| F | { (, id } | { +, *, ), $ } |

Algunas justificaciones:
- FIRST(T) = FIRST(F) porque F no deriva ε.
- `)` ∈ FOLLOW(E) por el cuerpo `( E )`.
- FOLLOW(E') = FOLLOW(E) porque E' solo aparece al **final** de cuerpos de producciones de E.
- `+` ∈ FOLLOW(T) porque T va seguido de E' y `+` ∈ FIRST(E'). Como E' ⇒* ε, todo FOLLOW(E) también entra en FOLLOW(T).

#### Ejemplo resuelto paso a paso (Ejemplo 2 del enunciado)

```
S → AB
A → aA | d
B → bBc | ε
```

**FIRST:**
- FIRST(A) = {a, d}, porque los cuerpos empiezan con `a` o con `d`.
- FIRST(B) = {b, ε}, porque un cuerpo empieza con `b` y el otro es ε.
- FIRST(S) = FIRST(AB). FIRST(A) = {a, d} y A **no** deriva ε, así que no se mira B. Resultado: FIRST(S) = {a, d}.

**FOLLOW:**
- Regla 1: `$` ∈ FOLLOW(S).
- En `S → AB`:
  - A va seguido de B. Por la regla 2, FIRST(B) − {ε} = {b} ⊆ FOLLOW(A). Como ε ∈ FIRST(B), por la regla 3 FOLLOW(S) = {$} ⊆ FOLLOW(A).
  - B está al final del cuerpo. Por la regla 3, FOLLOW(S) ⊆ FOLLOW(B), así que `$` ∈ FOLLOW(B).
- En `A → aA`: A está al final, así que FOLLOW(A) ⊆ FOLLOW(A). Esto no aporta nada.
- En `B → bBc`: B va seguido de `c`, así que `c` ∈ FOLLOW(B).

Resultado: FOLLOW(S) = {$}, FOLLOW(A) = {b, $}, FOLLOW(B) = {c, $}.

> **En el proyecto (`--sets`):** para esta gramática, la salida exacta sería:
> ```
> First(A) = {a, d}
> First(B) = {b, e}
> First(S) = {a, d}
> Follow(A) = {b, $}
> Follow(B) = {c, $}
> Follow(S) = {$}
> ```
> Los no terminales van en orden alfabético. Dentro de cada conjunto, primero los terminales en orden ASCII, luego `e` y al final `$`. El orden ASCII pone primero los símbolos (`(`=40, `)`=41, `*`=42, `+`=43), luego los dígitos y luego las letras minúsculas. Así, `{+, *, (, ), $}` se imprime como `{(, ), *, +, $}`.
>
> El enunciado no dice si van todos los `First` y luego todos los `Follow`, o intercalados por no terminal. Aquí se muestran todos los `First` primero; confírmenlo con el profesor.

### 2.3 §4.4.3 Gramáticas LL(1) y tabla predictiva

#### Definición (el "test" que el enunciado les pide implementar)

> **Una gramática G es LL(1) si y solo si, para cada par de producciones distintas `A → α | β`, se cumple:**
> 1. No hay ningún terminal `a` tal que α y β deriven cadenas que empiecen con `a`.
> 2. A lo sumo uno de α y β puede derivar la cadena vacía.
> 3. Si `β ⇒* ε`, entonces α no deriva ninguna cadena que empiece con un terminal de FOLLOW(A). Lo mismo al revés: si `α ⇒* ε`, β no deriva ninguna cadena que empiece con un terminal de FOLLOW(A).

**Formulación con conjuntos**, que es la que se implementa:
- Las condiciones 1 y 2 equivalen a **FIRST(α) ∩ FIRST(β) = ∅**. Contando ε como elemento, la condición 2 es que ε no esté en ambos.
- La condición 3 equivale a: **si ε ∈ FIRST(β), entonces FIRST(α) ∩ FOLLOW(A) = ∅**, y lo mismo intercambiando α y β.

Consecuencia directa: **ninguna gramática recursiva por la izquierda ni ambigua puede ser LL(1).**
- Si `A → Aα | β`, todo lo de FIRST(β) también está en FIRST(Aα), así que se viola la condición 1.
- Si es ambigua, para alguna cadena hay dos producciones posibles en algún punto.

#### Algoritmo 4.31: construcción de la tabla predictiva M[A, a]

Para cada producción `A → α`:
1. Para cada terminal `a` ∈ FIRST(α), se agrega `A → α` a M[A, a].
2. Si ε ∈ FIRST(α), se agrega `A → α` a M[A, b] para cada `b` ∈ FOLLOW(A). Si además `$` ∈ FOLLOW(A), también se agrega a M[A, $].

Las celdas vacías son **error**.

**Teorema práctico** (el libro lo dice justo después del Ejemplo 4.32):
- Para toda gramática LL(1), **cada celda tiene a lo sumo una producción**.
- Si G es recursiva por la izquierda o ambigua, **habrá al menos una celda con más de una producción**.
- Por lo tanto, **G es LL(1) ⇔ la tabla no tiene celdas con más de una producción.** Revisar los conflictos de la tabla es la misma prueba que la definición de arriba.

#### Tabla del Ejemplo 4.32 (Fig. 4.17), para la gramática 4.28

| | id | + | * | ( | ) | $ |
|---|---|---|---|---|---|---|
| **E** | E → TE' | | | E → TE' | | |
| **E'** | | E' → +TE' | | | E' → ε | E' → ε |
| **T** | T → FT' | | | T → FT' | | |
| **T'** | | T' → ε | T' → *FT' | | T' → ε | T' → ε |
| **F** | F → id | | | F → (E) | | |

Por ejemplo, `E' → ε` va en las columnas `)` y `$` porque FOLLOW(E') = {), $}.

#### Ejemplo de gramática que no es LL(1): Ejemplo 4.33, el "dangling else"

```
S  → iEtSS' | a
S' → eS | ε
E  → b
```

La celda M[S', e] contiene **dos** producciones: `S' → eS` (porque `e` ∈ FIRST(eS)) y `S' → ε` (porque `e` ∈ FOLLOW(S')). La gramática es ambigua, así que no es LL(1). El libro aclara que **hay lenguajes que no tienen ninguna gramática LL(1)**, por mucho que se transforme la gramática.

#### Tabla LL(1) del Ejemplo 2 del enunciado

| | a | b | c | d | $ |
|---|---|---|---|---|---|
| **S** | S → AB | | | S → AB | |
| **A** | A → aA | | | A → d | |
| **B** | | B → bBc | B → ε | | B → ε |

Ninguna celda tiene más de una producción, así que la gramática **es LL(1)**.

> **En el proyecto:**
> - El enunciado dice **"Do not transform the input grammar (for example, do not remove left recursion) before checking whether it is LL(1)"**. Si la gramática es recursiva por la izquierda, el programa debe concluir simplemente que **no es LL(1)**.
> - Recuerden que en las gramáticas del proyecto **ε se escribe `e`**. Al leer `B -> bBc e`, la segunda alternativa es el cuerpo vacío.

### 2.4 §4.4.4 Parser predictivo no recursivo

**Modelo (Fig. 4.19).** Tiene cuatro partes:
- Un búfer de entrada con `w$`.
- Una **pila** de símbolos gramaticales, que al inicio contiene `S` encima de `$`.
- La tabla M.
- Una salida.

El parser **imita una derivación por la izquierda**: si `w` es lo que ya se reconoció de la entrada, la pila contiene un α tal que `S ⇒*lm wα`.

#### Algoritmo 4.34 (programa de la Fig. 4.20)

```
let a be the first symbol of w$;
let X be the top stack symbol;
while (X ≠ $) {                       /* stack is not empty */
    if (X == a) pop the stack and let a be the next symbol of w;
    else if (X is a terminal) error();
    else if (M[X, a] is an error entry) error();
    else if (M[X, a] = X → Y1 Y2 … Yk) {
        output the production X → Y1 Y2 … Yk;
        pop the stack;
        push Yk, Yk-1, …, Y1 onto the stack, with Y1 on top;
    }
    let X be the top stack symbol;
}
```

Puntos clave:
- Los símbolos del cuerpo se apilan **en orden inverso**, para que Y₁ quede arriba.
- Si la producción es `X → ε`, **no se apila nada**; solo se desapila X.
- La cadena se **acepta** cuando la pila llega a `$` **y** la entrada también está en `$`. Si la pila se vacía y todavía queda entrada, es error. Esta condición está implícita en el `while`, pero el código tiene que revisarla.
- El parser es **lineal**: cada paso consume un símbolo o aplica una producción. No hay retroceso.

#### Traza: `adbc` con la gramática del Ejemplo 2 (formato de la Fig. 4.21)

En la columna PILA, la cima está a la **izquierda**.

| RECONOCIDO | PILA | ENTRADA | ACCIÓN |
|---|---|---|---|
| | S $ | adbc$ | salida S → AB |
| | A B $ | adbc$ | salida A → aA |
| | a A B $ | adbc$ | reconocer a |
| a | A B $ | dbc$ | salida A → d |
| a | d B $ | dbc$ | reconocer d |
| ad | B $ | bc$ | salida B → bBc |
| ad | b B c $ | bc$ | reconocer b |
| adb | B c $ | c$ | salida B → ε |
| adb | c $ | c$ | reconocer c |
| adbc | $ | $ | **aceptar → `yes`** |

Con la entrada `a`: tras S → AB, A → aA y reconocer `a`, la pila queda en `A B $` y la entrada en `$`. M[A, $] está vacía, así que es **error → `no`**, como en el enunciado.

> **En el proyecto:**
> - **Construcción del árbol (para el ítem 3).** El libro dice que, al elegir una producción, *"additional code could be executed here, for example, code to construct a node in a parse tree"*. En la práctica, la pila guarda **referencias a nodos del árbol** en vez de símbolos sueltos:
>   - Al expandir X → Y₁…Yₖ, se crean k hijos para el nodo de X y se apilan en orden inverso.
>   - Si la producción es X → ε, se crea un hijo hoja ε.
> - **Advertencia práctica:** jamás corran el parser LL sobre una tabla con conflictos tomando "la primera opción". Con una gramática recursiva por la izquierda como `S → S+T | T`, el parser expandiría `S → S+T` para siempre y la pila crecería sin límite. Al verificar los ejemplos de esta guía pasó exactamente eso. Por eso **primero** se prueba si es LL(1) y solo entonces se usa el parser.

---

## 3. §4.5 Análisis ascendente (bottom-up)

**Idea.** El análisis ascendente construye el árbol **desde las hojas hacia la raíz** (Fig. 4.25). Se ve como un proceso de **reducir** la cadena de entrada hasta llegar al símbolo inicial.

### §4.5.1 Reducciones

- Una **reducción** reemplaza una subcadena que coincide con el **cuerpo** de una producción por la **cabeza** de esa producción.
- Una reducción es **un paso de derivación al revés**.
- Las decisiones clave son **cuándo** reducir y **por qué producción**.
- El análisis ascendente reconstruye una **derivación por la derecha al revés**. En el Ejemplo 4.37:
  - Reducciones: `id*id, F*id, T*id, T*F, T, E`.
  - Leídas al revés: `E ⇒rm T ⇒rm T*F ⇒rm T*id ⇒rm F*id ⇒rm id*id`.

### §4.5.2 Poda de mangos (handle pruning)

**Definición formal.** Si `S ⇒*rm αAw ⇒rm αβw`, entonces la producción `A → β` en la posición que sigue a α es un **mango (handle)** de `αβw`. Observaciones:
- La cadena `w` a la derecha del mango **solo tiene terminales**.
- Por comodidad se llama "mango" al cuerpo β.
- Si la gramática es **no ambigua**, cada forma sentencial derecha tiene **exactamente un** mango.

**Cuidado:** la subcadena más a la izquierda que coincide con un cuerpo **no siempre es el mango**. En `T * id₂`, T coincide con el cuerpo de `E → T`. Pero si se redujera, quedaría `E * id₂`, que no se puede derivar de E. El mango correcto es `id₂` (Fig. 4.26).

**Poda de mangos.** Se parte de w = γₙ, se localiza el mango βₙ en γₙ y se reemplaza por la cabeza Aₙ para obtener γₙ₋₁. Se repite hasta llegar a S. La sucesión de producciones usadas, leída al revés, es una derivación por la derecha.

### §4.5.3 Análisis de desplazamiento-reducción (shift-reduce)

- Usa una **pila** de símbolos y un **búfer** con el resto de la entrada.
- En el análisis ascendente la cima de la pila se dibuja a la **derecha**.
- Configuración inicial: pila `$`, entrada `w$`.
- Configuración final de éxito: pila `$S`, entrada `$`.

**Las cuatro acciones posibles:**
1. **Desplazar (shift):** pasar el siguiente símbolo de la entrada a la cima de la pila.
2. **Reducir (reduce):** el extremo derecho del mango está en la cima. Se localiza su extremo izquierdo dentro de la pila y se reemplaza el mango por la cabeza.
3. **Aceptar (accept):** el análisis terminó con éxito.
4. **Error:** se detectó un error de sintaxis.

**Hecho fundamental (justificado con la Fig. 4.29):**

> **El mango siempre termina apareciendo en la cima de la pila, nunca dentro de ella.**

La razón: al ver dos pasos consecutivos de una derivación por la derecha, después de cada reducción el parser solo necesita **desplazar** cero o más símbolos para que el siguiente mango quede en la cima. Por eso alcanza con una pila.

Fig. 4.28, `id₁ * id₂` con la gramática de expresiones:

| PILA | ENTRADA | ACCIÓN |
|---|---|---|
| $ | id₁ * id₂ $ | desplazar |
| $ id₁ | * id₂ $ | reducir F → id |
| $ F | * id₂ $ | reducir T → F |
| $ T | * id₂ $ | desplazar |
| $ T * | id₂ $ | desplazar |
| $ T * id₂ | $ | reducir F → id |
| $ T * F | $ | reducir T → T * F |
| $ T | $ | reducir E → T |
| $ E | $ | aceptar |

### §4.5.4 Conflictos (lectura especialmente pedida en el enunciado)

Hay gramáticas para las que el parser llega a una configuración en la que, aun conociendo **toda la pila** y los siguientes k símbolos de la entrada, no puede decidir qué hacer:
- **Conflicto desplazar/reducir (shift/reduce):** no sabe si desplazar o reducir.
- **Conflicto reducir/reducir (reduce/reduce):** no sabe por cuál de varias producciones reducir.

Esas gramáticas **no son LR(k)**.

- **Ejemplo 4.38 (dangling else):** con `… if expr then stmt` en la pila y `else` en la entrada, se puede reducir `if expr then stmt` a `stmt` o desplazar `else`. Es un conflicto desplazar/reducir. **Una gramática ambigua nunca es LR.**
- **Ejemplo 4.39 (Fig. 4.30):** con `id ( id , id )`, el `id` de la cima se puede reducir como *parameter* (producción 5) o como *expr* (producción 7). Es un conflicto reducir/reducir: la pila no dice si `p` es un procedimiento o un arreglo.

> **En el proyecto:** "la gramática es SLR(1)" significa exactamente que **al construir la tabla SLR no aparece ningún conflicto** (ni desplazar/reducir ni reducir/reducir).

---

## 4. §4.6 LR y SLR

**LR(k)**:
- **L**: lee de izquierda a derecha.
- **R**: construye una derivación por la derecha al revés.
- **k**: símbolos de *lookahead*. Si se omite, k = 1.

**SLR** ("Simple LR") es el método más sencillo de construir la tabla. Usa el **autómata LR(0)** y los conjuntos **FOLLOW**.

### §4.6.1 ¿Por qué LR?

- Reconoce casi todos los constructos de los lenguajes de programación.
- Es el método de desplazamiento-reducción **sin retroceso** más general que se conoce, y es igual de eficiente.
- **Detecta un error de sintaxis tan pronto como es posible** en una lectura de izquierda a derecha.
- **La clase de gramáticas LR es un superconjunto propio de la clase LL.** Para LR(k) basta con reconocer el cuerpo completo de una producción, **después de haberlo visto**, más k símbolos de *lookahead*. Para LL(k) hay que decidir la producción viendo solo los primeros k símbolos de lo que deriva el cuerpo.
- La desventaja es que construir la tabla a mano es mucho trabajo. Por eso existen generadores como Yacc, que **el proyecto prohíbe usar**.

> **Matiz que pueden preguntarles:** "LR es más general que LL" se refiere a LR(k) / LR(1) canónico. **No es cierto que toda gramática LL(1) sea SLR(1).** En la [sección 5](#5-los-ejemplos-del-enunciado-resueltos) hay un contraejemplo verificado. Por eso el enunciado contempla el caso "LL(1) pero no SLR(1)".

### 4.1 §4.6.2 Ítems LR(0), CLOSURE, GOTO y el autómata LR(0)

#### Ítem LR(0)

Un **ítem LR(0)** es una producción con un **punto** en algún lugar del cuerpo. `A → XYZ` da cuatro ítems:

```
A → ·XYZ     (espero ver algo derivable de XYZ)
A → X·YZ     (ya vi algo derivable de X; espero algo de YZ)
A → XY·Z
A → XYZ·     (ya vi todo el cuerpo: tal vez sea momento de reducir a A)
```

**La producción `A → ε` genera un solo ítem: `A → ·`**, que es a la vez inicial y completo. Esto importa para el proyecto.

**Representación sugerida por el libro** (recuadro "Representing Item Sets"): un ítem se guarda como un **par de enteros** (número de producción, posición del punto).

#### Gramática aumentada

Si G tiene símbolo inicial S, **G' es G más un nuevo símbolo inicial S' y la producción `S' → S`**. Sirve para saber cuándo aceptar: **se acepta cuando, y solo cuando, el parser va a reducir por `S' → S`.**

#### CLOSURE(I)

1. Todo ítem de I está en CLOSURE(I).
2. Si `A → α·Bβ` está en CLOSURE(I) y `B → γ` es una producción, se agrega `B → ·γ`, si no estaba. Esto se repite hasta que no haya ítems nuevos.

Intuición: si espero ver algo derivable de Bβ, entonces espero que empiece algo derivable de B, y eso puede venir de cualquier producción de B.

Fig. 4.32:

```
SetOfItems CLOSURE(I) {
    J = I;
    repeat
        for (each item A → α·Bβ in J)
            for (each production B → γ of G)
                if (B → ·γ is not in J)
                    add B → ·γ to J;
    until no more items are added to J on one round;
    return J;
}
```

- **Ítems núcleo (kernel):** `S' → ·S` y todos los ítems con el punto que **no** está al inicio.
- **Ítems no núcleo:** los que tienen el punto al inicio, excepto `S' → ·S`.
- Cada conjunto de interés es la clausura de su núcleo.

#### GOTO(I, X)

**GOTO(I, X)** es la **clausura** del conjunto de ítems `[A → αX·β]` tales que `[A → α·Xβ]` ∈ I. En palabras: se mueve el punto por encima de X en los ítems que lo permiten y se toma la clausura. Así se definen las **transiciones** del autómata.

Ejemplo 4.41: si I = {[E' → E·], [E → E·+T]}, GOTO(I, +) = {E → E+·T, T → ·T*F, T → ·F, F → ·(E), F → ·id}.

#### Colección canónica LR(0) (Fig. 4.33)

```
void items(G') {
    C = { CLOSURE({[S' → ·S]}) };
    repeat
        for (each set of items I in C)
            for (each grammar symbol X)
                if (GOTO(I, X) is not empty and not in C)
                    add GOTO(I, X) to C;
    until no new sets of items are added to C on a round;
}
```

- **Autómata LR(0):** los estados son los conjuntos de C y las transiciones son GOTO.
- El estado inicial es CLOSURE({[S' → ·S]}). **Todos** los estados son de aceptación.
- La nota al pie aclara que técnicamente no es un AFD completo, porque no tiene estado muerto.
- Recuadro "Items as States of an NFA": si cada ítem se ve como un estado de un AFN (transiciones X que mueven el punto y transiciones ε de `A → α·Bβ` a `B → ·γ`), **CLOSURE es la ε-clausura y `items(G')` es la construcción de subconjuntos**. Es una buena conexión con lo visto en autómatas.

**Uso del autómata para decidir.** Si la cadena γ de la pila lleva el autómata del estado 0 al estado j:
- Si j tiene transición con el siguiente símbolo de la entrada `a`, se **desplaza**.
- Si no, se **reduce**, y los ítems de j indican por cuál producción.

### 4.2 §4.6.3 El algoritmo de análisis LR

**Modelo (Fig. 4.35).** Tiene una entrada, una pila de **estados**, un programa conductor **igual para todo parser LR** y una tabla con dos partes: **ACTION** y **GOTO**.
- Cada estado, salvo el 0, corresponde a un único símbolo gramatical: el de la transición por la que se entra.
- Por eso la pila guarda solo estados; los símbolos se pueden recuperar a partir de ellos.

**Tabla:**
- **ACTION[i, a]**, con `a` terminal o `$`, puede ser:
  - **shift j** (desplazar y apilar el estado j),
  - **reduce A → β**,
  - **accept**,
  - **error** (celda vacía).
- **GOTO[i, A]**, con A no terminal, es el estado j tal que GOTO(Iᵢ, A) = Iⱼ.

**Configuración:** `(s₀ s₁ … sₘ , aᵢ aᵢ₊₁ … aₙ $)`. Representa la forma sentencial derecha `X₁…Xₘ aᵢ…aₙ`.

**Movimientos:**
1. Si ACTION[sₘ, aᵢ] = shift s, se apila s y se avanza en la entrada.
2. Si ACTION[sₘ, aᵢ] = reduce A → β, se **desapilan r = |β| estados**, quedando arriba sₘ₋ᵣ. Luego se apila GOTO[sₘ₋ᵣ, A]. **La entrada no avanza.** Se emite la producción.
3. Si es accept, termina con éxito.
4. Si es error, se rechaza la cadena.

#### Algoritmo 4.44 (programa de la Fig. 4.36)

```
let a be the first symbol of w$;
while (1) {                              /* repeat forever */
    let s be the state on top of the stack;
    if (ACTION[s, a] = shift t) {
        push t onto the stack;
        let a be the next input symbol;
    } else if (ACTION[s, a] = reduce A → β) {
        pop |β| symbols off the stack;
        let state t now be on top of the stack;
        push GOTO[t, A] onto the stack;
        output the production A → β;
    } else if (ACTION[s, a] = accept) break;   /* parsing is done */
    else call error-recovery routine;
}
```

> **En el proyecto:** cuando se reduce por `A → ε`, **|β| = 0, así que no se desapila nada**: se mira el estado de la cima y se apila GOTO[cima, A]. Es un error clásico olvidar este caso.

#### Ejemplo 4.45: tabla SLR de la gramática de expresiones (Fig. 4.37)

Producciones: (1) E → E+T, (2) E → T, (3) T → T*F, (4) T → F, (5) F → (E), (6) F → id.

| Estado | id | + | * | ( | ) | $ | E | T | F |
|---|---|---|---|---|---|---|---|---|---|
| 0 | s5 | | | s4 | | | 1 | 2 | 3 |
| 1 | | s6 | | | | acc | | | |
| 2 | | r2 | s7 | | r2 | r2 | | | |
| 3 | | r4 | r4 | | r4 | r4 | | | |
| 4 | s5 | | | s4 | | | 8 | 2 | 3 |
| 5 | | r6 | r6 | | r6 | r6 | | | |
| 6 | s5 | | | s4 | | | | 9 | 3 |
| 7 | s5 | | | s4 | | | | | 10 |
| 8 | | s6 | | | s11 | | | | |
| 9 | | r1 | s7 | | r1 | r1 | | | |
| 10 | | r3 | r3 | | r3 | r3 | | | |
| 11 | | r5 | r5 | | r5 | r5 | | | |

La Fig. 4.38 muestra los 14 movimientos del parser con `id * id + id`.

### 4.3 §4.6.4 Construcción de la tabla SLR

#### Algoritmo 4.46

**Entrada:** gramática aumentada G'. **Salida:** ACTION y GOTO.

1. Construir C = {I₀, I₁, …, Iₙ}, la colección LR(0) de G'.
2. El estado i se construye a partir de Iᵢ:
   - **(a)** Si `[A → α·aβ]` ∈ Iᵢ (con `a` **terminal**) y GOTO(Iᵢ, a) = Iⱼ, entonces ACTION[i, a] = **shift j**.
   - **(b)** Si `[A → α·]` ∈ Iᵢ, entonces ACTION[i, a] = **reduce A → α** para **todo `a` ∈ FOLLOW(A)**. Aquí A ≠ S'.
   - **(c)** Si `[S' → S·]` ∈ Iᵢ, entonces ACTION[i, $] = **accept**.

   **Si las reglas anteriores generan acciones en conflicto, la gramática no es SLR(1)** y el algoritmo no produce un parser.
3. Si GOTO(Iᵢ, A) = Iⱼ con A no terminal, entonces GOTO[i, A] = j.
4. Todas las demás celdas son **error**.
5. El estado inicial es el que contiene `[S' → ·S]`.

**Lo que distingue a SLR es la regla (b):** solo se reduce por A → α si el siguiente símbolo **puede seguir a A** (está en FOLLOW(A)). Así se evitan muchos conflictos que tendría LR(0) puro. Pero FOLLOW(A) es una aproximación global: no tiene en cuenta en qué contexto concreto está A. Por eso hay gramáticas no ambiguas que no son SLR.

#### Ejemplo 4.48: gramática no ambigua que no es SLR(1)

```
S → L = R | R
L → * R | id
R → L
```

- I₂ = { S → L·=R, R → L· }.
- El primer ítem da ACTION[2, =] = shift.
- `=` ∈ FOLLOW(R) por la derivación `S ⇒ L=R ⇒ *R=R`, así que el segundo ítem da ACTION[2, =] = reduce R → L.
- Resultado: **conflicto desplazar/reducir**.

La gramática no es ambigua; el problema es que SLR no recuerda suficiente contexto. Los métodos LR(1) canónico y LALR (§4.7, no exigidos en el proyecto) sí la manejan. Además, la gramática tampoco es LL(1), porque M[S, id] y M[S, *] tienen dos producciones. **En formato del proyecto** (con `i` en lugar de `id`): `3 / S -> L=R R / L -> *R i / R -> L`. **Salida esperada: "Grammar is neither LL(1) nor SLR(1)."**

> **Teorema (Ejemplo 4.48): toda gramática SLR(1) es no ambigua.** El recíproco es falso.

### 4.4 §4.6.5 Prefijos viables

¿Por qué funciona el autómata LR(0)? Porque **reconoce exactamente lo que puede haber en la pila**.

- **Prefijo viable:** un prefijo de una forma sentencial derecha que **no se extiende más allá del extremo derecho del mango** de esa forma.
  - Ejemplo: si `E ⇒*rm F*id ⇒rm (E)*id`, la pila puede contener `(`, `(E` y `(E)`, pero **nunca** `(E)*`, porque `(E)` es un mango y debe reducirse antes de desplazar `*`.
- **Ítem válido:** `A → β₁·β₂` es válido para el prefijo viable αβ₁ si existe una derivación `S' ⇒*rm αAw ⇒rm αβ₁β₂w`.
  - Si β₂ ≠ ε, todavía no se ha desplazado todo el mango, así que se **desplaza**.
  - Si β₂ = ε, parece que `A → β₁` es el mango, así que se **reduce**.

> **Teorema central de LR (el libro lo enuncia sin demostración):** el conjunto de ítems válidos para un prefijo viable γ es **exactamente** el conjunto de ítems del estado al que se llega desde el estado inicial siguiendo el camino γ en el autómata LR(0).

Ejemplo 4.50: después de leer `E+T*`, el autómata está en el estado 7 = {T → T*·F, F → ·(E), F → ·id}, y esos son exactamente los ítems válidos para `E+T*`.

---

## 5. Los ejemplos del enunciado, resueltos

### Ejemplo 1 del enunciado: `S → S+T | T`, `T → T*F | F`, `F → (S) | i`

Es la gramática 4.1 del libro con `E` renombrado como `S` e `id` como `i`.

- FIRST(S) = FIRST(T) = FIRST(F) = {(, i}.
- FOLLOW(S) = {), +, $}; FOLLOW(T) = {), *, +, $}; FOLLOW(F) = {), *, +, $}.
- **No es LL(1).** Es recursiva por la izquierda: M[S, (] y M[S, i] contienen `S → S+T` **y** `S → T`; M[T, (] y M[T, i] contienen `T → T*F` **y** `T → F`.
- **Sí es SLR(1).** Su tabla es la Fig. 4.37, sin conflictos.
- Salida: `Grammar is SLR(1).`
  - `i+i` → yes
  - `(i)` → yes
  - `(i+i)*i)` → no (sobra un paréntesis)

### Ejemplo 2 del enunciado: `S → AB`, `A → aA | d`, `B → bBc | ε`

Es LL(1) (tabla de §2.3) **y** SLR(1), así que el programa muestra el menú `Select a parser (T: for LL(1), B: for SLR(1), Q: quit):`.

**Gramática aumentada y producciones numeradas:** (0) S' → S, (1) S → AB, (2) A → aA, (3) A → d, (4) B → bBc, (5) B → ε.

**Colección LR(0):**

```
I0: S' → ·S      S → ·AB      A → ·aA      A → ·d
I1 = GOTO(I0,S): S' → S·
I2 = GOTO(I0,A): S → A·B      B → ·bBc     B → ·
I3 = GOTO(I0,a): A → a·A      A → ·aA      A → ·d
I4 = GOTO(I0,d): A → d·
I5 = GOTO(I2,B): S → AB·
I6 = GOTO(I2,b): B → b·Bc     B → ·bBc     B → ·
I7 = GOTO(I3,A): A → aA·
I8 = GOTO(I6,B): B → bB·c
I9 = GOTO(I8,c): B → bBc·
```

Otras transiciones: GOTO(I3, a) = I3, GOTO(I3, d) = I4, GOTO(I6, b) = I6.

Esta es la numeración que imprime el programa con `--automaton`. Fíjense en `B → ·` en I2 e I6: es un ítem **completo**, así que genera reducciones por B → ε en FOLLOW(B) = {c, $}.

**Tabla SLR(1):**

| Estado | a | b | c | d | $ | S | A | B |
|---|---|---|---|---|---|---|---|---|
| 0 | s3 | | | s4 | | 1 | 2 | |
| 1 | | | | | acc | | | |
| 2 | | s6 | r5 | | r5 | | | 5 |
| 3 | s3 | | | s4 | | | 7 | |
| 4 | | r3 | | | r3 | | | |
| 5 | | | | | r1 | | | |
| 6 | | s6 | r5 | | r5 | | | 8 |
| 7 | | r2 | | | r2 | | | |
| 8 | | | s9 | | | | | |
| 9 | | | r4 | | r4 | | | |

Por ejemplo, r3 (A → d) está en las columnas `b` y `$` porque FOLLOW(A) = {b, $}.

**Traza de `adbc` (formato de la Fig. 4.38):**

| | PILA | SÍMBOLOS | ENTRADA | ACCIÓN |
|---|---|---|---|---|
| 1 | 0 | | adbc$ | shift 3 |
| 2 | 0 3 | a | dbc$ | shift 4 |
| 3 | 0 3 4 | a d | bc$ | reduce A → d (desapilar 1; GOTO[3, A] = 7) |
| 4 | 0 3 7 | a A | bc$ | reduce A → aA (desapilar 2; GOTO[0, A] = 2) |
| 5 | 0 2 | A | bc$ | shift 6 |
| 6 | 0 2 6 | A b | c$ | reduce B → ε (**desapilar 0**; GOTO[6, B] = 8) |
| 7 | 0 2 6 8 | A b B | c$ | shift 9 |
| 8 | 0 2 6 8 9 | A b B c | $ | reduce B → bBc (desapilar 3; GOTO[2, B] = 5) |
| 9 | 0 2 5 | A B | $ | reduce S → AB (desapilar 2; GOTO[0, S] = 1) |
| 10 | 0 1 | S | $ | **accept → `yes`** |

Las reducciones, leídas al revés, dan la derivación por la derecha `S ⇒ AB ⇒ AbBc ⇒ Abc ⇒ aAbc ⇒ adbc`.

### Ejemplo 3 del enunciado: `S → SS | a`

- FIRST(S) = {a}, FOLLOW(S) = {a, $}.
- **No es LL(1):** M[S, a] = {S → SS, S → a}.
- **No es SLR(1):** el estado GOTO(GOTO(I₀, S), S) = {S → SS·, S → S·S, S → ·SS, S → ·a} con la entrada `a` tiene shift (por `S → ·a`) **y** reduce S → SS (porque `a` ∈ FOLLOW(S)). Es un conflicto desplazar/reducir.
- La causa de fondo es que la gramática es **ambigua**: `aaa` tiene dos árboles.
- Salida: `Grammar is neither LL(1) nor SLR(1).`

### Contraejemplo útil: una gramática LL(1) que **no** es SLR(1)

Sirve para probar el caso 2 del enunciado ("Grammar is LL(1).").

```
3
S -> AaAb BbBa
A -> e
B -> e
```

- **LL(1):** M[S, a] = S → AaAb, M[S, b] = S → BbBa, y A → ε, B → ε van en las columnas `a` y `b`. No hay conflictos.
- **No es SLR(1):** I₀ contiene los ítems completos `A → ·` y `B → ·`, y FOLLOW(A) = FOLLOW(B) = {a, b}. En ACTION[0, a] y ACTION[0, b] hay un **conflicto reducir/reducir** entre A → ε y B → ε.
- Con esta gramática, `ab` → yes y `ba` → yes (con el parser LL(1)).

---

## 6. §5.1 Definiciones dirigidas por la sintaxis (SDD)

### Definición

Una **definición dirigida por la sintaxis (SDD)** es una **gramática libre de contexto con atributos y reglas**:
- Los **atributos** se asocian a **símbolos** de la gramática.
- Las **reglas semánticas** se asocian a **producciones**.

`X.a` es el valor del atributo `a` en un **nodo concreto** del árbol etiquetado con X. En la implementación, los atributos son campos del objeto que representa al nodo. Pueden ser de cualquier tipo: números, cadenas, tipos, referencias, etc.

### §5.1.1 Atributos sintetizados y heredados

| | **Sintetizado** | **Heredado** |
|---|---|---|
| Lo define | una regla de la producción **del propio nodo N**, que tiene a A como **cabeza** | una regla de la producción **del padre de N**, que tiene a B en su **cuerpo** |
| Puede usar | atributos de **los hijos de N** y de **N mismo** | atributos del **padre** de N, de **N mismo** y de sus **hermanos** |
| La información fluye | de abajo hacia arriba | de arriba hacia abajo y entre hermanos |

Reglas adicionales del libro:
- Un atributo sintetizado de N **sí puede** usar atributos **heredados de N mismo**. Por ejemplo, `P.m = P.d` en `P → ε`.
- Un atributo heredado **no puede** usar atributos de los **hijos** de N.
- **Los terminales solo tienen atributos sintetizados**, y sus valores vienen del analizador léxico. La SDD **no tiene reglas** para calcularlos.
  > **En el proyecto:** el atributo `lexval` de un terminal es **el propio carácter**, así que no hace falta escribir un analizador léxico.

**Ejemplo 5.1: calculadora de escritorio (Fig. 5.1).** Es **S-atribuida**: solo tiene atributos sintetizados.

| Producción | Reglas semánticas |
|---|---|
| 1) L → E **n** | L.val = E.val |
| 2) E → E₁ + T | E.val = E₁.val + T.val |
| 3) E → T | E.val = T.val |
| 4) T → T₁ * F | T.val = T₁.val × F.val |
| 5) T → F | T.val = F.val |
| 6) F → ( E ) | F.val = E.val |
| 7) F → **digit** | F.val = **digit**.lexval |

Los subíndices (E₁, T₁) distinguen las apariciones de un mismo símbolo dentro de una producción.

- **Atributos definidos solo por constantes y otros atributos, sin efectos secundarios:** una SDD así se llama **gramática de atributos (attribute grammar)**.
- **Advertencia del libro: puede no existir ningún orden de evaluación.** Ejemplo:

  | Producción | Reglas |
  |---|---|
  | A → B | A.s = B.i;  B.i = A.s + 1 |

  A.s depende de B.i y B.i depende de A.s, así que es **circular** (Fig. 5.2).
- **Nota al pie 1:** decidir si **alguno** de los infinitos árboles de una SDD tiene un ciclo es decidible, pero requiere **tiempo exponencial**. Por eso el proyecto les pide detectar ciclos **en el grafo de cada árbol concreto**, que es fácil.

### §5.1.2 Evaluar una SDD en los nodos del árbol

- Un **árbol de análisis anotado** es un árbol que muestra los valores de los atributos en cada nodo.
- **Antes de evaluar un atributo hay que evaluar todos aquellos de los que depende.**
- Si todos los atributos son sintetizados, sirve **cualquier orden ascendente**, por ejemplo el **postorden**.
- Si hay atributos sintetizados y heredados, **no hay garantía** de que exista un orden. Ahí entra el grafo de dependencias.

**Ejemplo 5.2:** el árbol anotado de `3*5+4n` (Fig. 5.3) da L.val = 19. Se calcula T.val = 15 a partir de T.val = 3 y F.val = 5, y luego E.val = 15 + 4 = 19.

**Ejemplo 5.3: atributos heredados (Fig. 5.4).** Es la parte de la gramática sin recursión izquierda para `3*5*7`:

| Producción | Reglas semánticas |
|---|---|
| 1) T → F T' | T'.inh = F.val;  T.val = T'.syn |
| 2) T' → * F T'₁ | T'₁.inh = T'.inh × F.val;  T'.syn = T'₁.syn |
| 3) T' → ε | T'.syn = T'.inh |
| 4) F → **digit** | F.val = **digit**.lexval |

**Idea:** en el análisis descendente, el operando izquierdo (3) queda en un subárbol **distinto** del de `*`, que lo genera T'. El atributo **heredado** `inh` pasa el valor acumulado **hacia la derecha y hacia abajo**. Al llegar a `T' → ε`, el resultado se **copia** a `syn` y sube con los atributos **sintetizados**.

Para `3*5` (Fig. 5.5): F.val = 3 → T'.inh = 3 → T'₁.inh = 3 × 5 = 15 → T'₁.syn = 15 → T'.syn = 15 → T.val = 15.

> **Esta es la técnica típica para tener un atributo heredado en su SDD.** Una gramática pensada para el análisis (sin recursión izquierda, buena para LL(1)) "rompe" la estructura natural de la expresión, y los heredados la reconstruyen. **Ojo:** no pueden entregar este SDD ni el de la Fig. 5.1, porque la condición G3 del enunciado prohíbe usar SDD del libro.

---

## 7. §5.2 Orden de evaluación: grafos de dependencias

### §5.2.1 Grafo de dependencias

El **grafo de dependencias** describe el flujo de información entre las **instancias** de atributos de **un árbol concreto**. **Una arista de X a Y significa que el valor de X se necesita para calcular Y.**

Construcción:
- **Vértices:** para cada nodo del árbol etiquetado con X, hay **un vértice por cada atributo de X**.
- **Atributos sintetizados:** si la regla de la producción p define `A.b` usando `X.c`, entonces en **cada nodo N etiquetado con A donde se aplicó p** hay una arista **desde el atributo c del hijo de N que corresponde a esa aparición de X, hacia el atributo b de N**.
- **Atributos heredados:** si la regla de p define `B.c` usando `X.a`, entonces en **cada nodo N que corresponde a esa aparición de B en el cuerpo de p** hay una arista **desde el atributo a del nodo M que corresponde a X, hacia el atributo c de N**. M puede ser el **padre** o un **hermano** de N.

> **La dirección importa:** la arista va **del atributo que se usa al atributo que se define**. El enunciado señala como error frecuente dibujar las aristas al revés.

**Convención de las figuras del libro:** las aristas del árbol se dibujan punteadas y las de dependencia, sólidas (Fig. 5.6).

**Ejemplo 5.5 (Fig. 5.7), grafo del árbol de `3*5` con la SDD de la Fig. 5.4:**

| Vértice | Atributo | Aristas que **entran** | Regla que la origina |
|---|---|---|---|
| 1 | digit.lexval (de 3) | — | (léxico) |
| 2 | digit.lexval (de 5) | — | (léxico) |
| 3 | F.val (izq.) | 1 → 3 | F.val = digit.lexval |
| 4 | F.val (der.) | 2 → 4 | F.val = digit.lexval |
| 5 | T'.inh | 3 → 5 | T'.inh = F.val |
| 6 | T'₁.inh | 5 → 6, 4 → 6 | T'₁.inh = T'.inh × F.val |
| 7 | T'₁.syn | 6 → 7 | T'.syn = T'.inh (en T' → ε) |
| 8 | T'.syn | 7 → 8 | T'.syn = T'₁.syn |
| 9 | T.val | 8 → 9 | T.val = T'.syn |

"La arista representa **dependencia, no igualdad**": F.val es igual a digit.lexval, pero lo que el grafo registra es que uno se calcula a partir del otro.

### §5.2.2 Orden de evaluación de los atributos

- Si hay una arista M → N, el atributo de M se evalúa **antes** que el de N.
- Un orden válido es una secuencia N₁, …, Nₖ en la que toda arista Nᵢ → Nⱼ cumple i < j. Esto es un **ordenamiento topológico**.

> **Teorema:**
> - **Si el grafo tiene un ciclo, no hay ningún ordenamiento topológico:** la SDD no se puede evaluar en ese árbol.
> - **Si no tiene ciclos, siempre hay al menos uno.**
>
> **Demostración del libro:** si no hay ciclos, existe un vértice sin aristas de entrada. Si no existiera, se podría ir de predecesor en predecesor indefinidamente y, como el grafo es finito, se repetiría un vértice, lo que formaría un ciclo. Ese vértice se pone primero, se elimina del grafo y se repite el proceso.

**Esa demostración es literalmente el algoritmo que deben implementar.** Se conoce como algoritmo de Kahn:

```
calcular grado_entrada[v] para todo vértice v
cola ← todos los v con grado_entrada[v] = 0
orden ← []
mientras cola no vacía:
    v ← sacar de cola;  orden.agregar(v)
    para cada arista v → w:
        grado_entrada[w] -= 1
        si grado_entrada[w] = 0: meter w en cola
si |orden| < |vértices|:   ⇒ hay un CICLO → "la SDD es circular", parar
si no: evaluar los atributos en el orden 'orden'
```

**Ejemplo 5.6:** para la Fig. 5.7, 1, 2, …, 9 es un orden topológico válido, y también 1, 3, 5, 2, 4, 6, 7, 8, 9. **En general hay varios órdenes válidos.** En el informe basta con dar uno.

### §5.2.3 Definiciones S-atribuidas

> **Una SDD es S-atribuida si todos sus atributos son sintetizados.**

- Se puede evaluar con un **recorrido en postorden**:
  ```
  postorder(N) { for (each child C of N, from the left) postorder(C);
                 evaluate the attributes associated with node N; }
  ```
- El postorden coincide **exactamente** con el orden en que un parser LR reduce. Por eso las SDD S-atribuidas se pueden evaluar durante el análisis ascendente.
- Ejemplo 5.7: la SDD de la Fig. 5.1 es S-atribuida.

### §5.2.4 Definiciones L-atribuidas

**Idea:** dentro del cuerpo de una producción, las aristas del grafo pueden ir **de izquierda a derecha, pero no de derecha a izquierda**. Por eso se llaman "L-atribuidas".

> **Definición.** Cada atributo debe ser:
> 1. **Sintetizado**, o
> 2. **Heredado**, con esta restricción: si `A → X₁X₂…Xₙ` y la regla define el heredado `Xᵢ.a`, solo puede usar:
>    - (a) atributos **heredados de la cabeza A**;
>    - (b) atributos heredados o sintetizados de **X₁, …, Xᵢ₋₁**, es decir, los que están **a la izquierda** de Xᵢ;
>    - (c) atributos heredados o sintetizados de **esta misma aparición de Xᵢ**, siempre que no se formen ciclos entre los atributos de Xᵢ.

- **Ejemplo 5.8:** la Fig. 5.4 es L-atribuida. `T'.inh = F.val` usa F, que está a la izquierda de T'. `T'₁.inh = T'.inh × F.val` usa el heredado de la cabeza y F, que está a la izquierda.
- **Ejemplo 5.9:** esta SDD **no puede ser L-atribuida**:

  | Producción | Reglas |
  |---|---|
  | A → B C | A.s = B.b;  B.i = f(C.c, A.s) |

  - `B.i` usa `C.c`, que está **a la derecha** de B.
  - Además usa `A.s`, que es un **sintetizado** de la cabeza. La regla (a) solo permite los heredados de la cabeza.
  - Tampoco es S-atribuida, porque tiene un heredado.

**Relación entre las clases:**
- Toda SDD S-atribuida es L-atribuida, porque solo tiene sintetizados y la condición 1 se cumple siempre.
- Una SDD puede ser S, L, ambas (si es S, es ambas) o ninguna.
- Las SDD S-atribuidas y las L-atribuidas **garantizan** que no habrá ciclos en ningún árbol.

> **En el proyecto (paso 4):** deben clasificar su SDD y justificarlo con estas definiciones, regla por regla. Lo esperable es que sea **L-atribuida y no S-atribuida**, porque deben tener al menos un heredado. **Aunque sea L-atribuida, deben implementar el método general del grafo de dependencias**; no vale recorrer el árbol en un orden fijo.

### §5.2.5 Reglas semánticas con efectos secundarios controlados

Esta subsección no es obligatoria en el proyecto, pero viene en 5.2.

- **Efectos secundarios incidentales:** se permiten si cualquier orden topológico da una traducción "correcta". Por ejemplo, `print(E.val)` en `L → E n`.
- Las reglas que solo hacen efectos secundarios se tratan como si definieran un **atributo sintetizado ficticio (dummy)** de la cabeza.
- **Ejemplo 5.10 (Fig. 5.8):** declaraciones `float id₁, id₂, id₃`. El tipo `T.type` se pasa con el heredado `L.inh` a lo largo de la lista, y `addType(id.entry, L.inh)` guarda el tipo en la tabla de símbolos.
- Fig. 5.9: en su grafo de dependencias, los vértices 6, 8 y 10 son los atributos ficticios de `addType`.

---

## 8. El ítem 3 paso a paso, con un ejemplo completo

Para entender el procedimiento se usa el **ejemplo ilustrativo del propio enunciado**. **No lo pueden entregar**; deben diseñar uno propio con al menos 3 no terminales, 6 producciones y un no terminal recursivo.

```
S → P
P → ( P ) P | ε
```

Esta gramática genera paréntesis balanceados. En formato del proyecto: `2 / S -> P / P -> (P)P e`. Es LL(1) y SLR(1) (verificado).

**Tabla de atributos (paso 2.1):**

| Símbolo | Atributo | Tipo de atributo | Tipo de dato | Significado |
|---|---|---|---|---|
| S | m | sintetizado | entero | profundidad máxima de anidamiento de toda la cadena |
| P | d | heredado | entero | profundidad a la que aparece este P |
| P | m | sintetizado | entero | profundidad máxima en el subárbol de P |
| `(` `)` | lexval | sintetizado (léxico) | carácter | el propio carácter |

**Reglas semánticas (paso 2.2), en el formato de la Fig. 5.1:**

| Producción | Reglas semánticas |
|---|---|
| S → P | P.d = 0;  S.m = P.m |
| P → ( P₁ ) P₂ | P₁.d = P.d + 1;  P₂.d = P.d;  P.m = max(P₁.m, P₂.m) |
| P → ε | P.m = P.d |

**Revisión de consistencia (§5.1.1, la exige el enunciado):**
- `S → P`: define el **heredado de P**, un símbolo del cuerpo, y el **sintetizado de S**, la cabeza. ✓
- `P → (P₁)P₂`: define los heredados de P₁ y P₂ (cuerpo) y el sintetizado P.m (cabeza). Cada uno se define **exactamente una vez**. ✓
- `P → ε`: define el sintetizado P.m. No hay no terminales en el cuerpo, así que no hay heredados que definir. ✓
- **S no tiene heredados.** ✓
- Hay al menos un sintetizado (m) y al menos un heredado (d). ✓

**Ejemplo a mano (paso 3) con la cadena `(())`.** El enunciado pide al menos 4 terminales, y esta tiene 4.

Árbol anotado, con un nodo por línea e indentado por profundidad (el formato de salida que pide el enunciado):

```
S [m=2]
  P [d=0, m=2]                 P → (P)P          (nodo Pa)
    ( [lexval=(]
    P [d=1, m=2]               P → (P)P          (nodo Pb)
      ( [lexval=(]
      P [d=2, m=2]             P → ε             (nodo Pc)
        ε
      ) [lexval=)]
      P [d=1, m=1]             P → ε             (nodo Pd)
        ε
    ) [lexval=)]
    P [d=0, m=0]               P → ε             (nodo Pe)
      ε
```

**Grafo de dependencias:** hay un vértice por cada atributo de cada nodo. Las aristas van **del atributo usado al atributo definido**:

| Arista | Por la regla |
|---|---|
| (Pa.d no tiene entrantes: se define con la constante 0) | P.d = 0 en S → P |
| Pa.m → S.m | S.m = P.m |
| Pa.d → Pb.d | P₁.d = P.d + 1 (en Pa) |
| Pa.d → Pe.d | P₂.d = P.d (en Pa) |
| Pb.m → Pa.m,  Pe.m → Pa.m | P.m = max(P₁.m, P₂.m) (en Pa) |
| Pb.d → Pc.d | P₁.d = P.d + 1 (en Pb) |
| Pb.d → Pd.d | P₂.d = P.d (en Pb) |
| Pc.m → Pb.m,  Pd.m → Pb.m | P.m = max(P₁.m, P₂.m) (en Pb) |
| Pc.d → Pc.m;  Pd.d → Pd.m;  Pe.d → Pe.m | P.m = P.d (en P → ε) |

Los `lexval` de los paréntesis son vértices **aislados**, porque ninguna regla los usa. Igual existen y ya tienen valor desde el inicio.

**Un orden topológico válido (paso 3):**

`Pa.d (=0), Pb.d (=1), Pc.d (=2), Pc.m (=2), Pd.d (=1), Pd.m (=1), Pb.m (=2), Pe.d (=0), Pe.m (=0), Pa.m (=2), S.m (=2)`

Se puede comprobar que **toda arista va de un elemento anterior a uno posterior** en la lista. **Valor del atributo principal: S.m = 2.**

**Clasificación (paso 4):**
- **No es S-atribuida**, porque `d` es heredado.
- **Es L-atribuida:**
  - `P.d = 0` en S → P usa solo una constante.
  - `P₁.d = P.d + 1` usa solo el **heredado de la cabeza**, lo que permite la regla (a).
  - `P₂.d = P.d` también usa solo el heredado de la cabeza (regla (a)).
  - Todo lo demás es sintetizado.

**Prueba de circularidad (paso 6).** Se cambia temporalmente una regla, por ejemplo en `S → P`: `P.d = P.m` en lugar de `P.d = 0`. Entonces:
- P.d depende de P.m.
- P.m depende, a través de los hijos, de los `d` de abajo, que dependen de P.d.

Se forma un **ciclo**: Kahn no puede ordenar todos los vértices y el programa debe reportar **"SDD is circular"** y detenerse.

**Pruebas mínimas (paso 6):** al menos 5 cadenas, entre ellas:
- La **más corta** del lenguaje. En este ejemplo es `e` (ε), que da S.m = 0.
- **Una que no esté en el lenguaje**, por ejemplo `(()`, que da `no`.
- **Una con anidamiento profundo**, por ejemplo `((((()))))`.

---

## 9. Del libro al código: decisiones de implementación

El informe pide documentar "las estructuras de datos que usaron". Estas son las decisiones que conviene tomar y justificar.

**Representación de la gramática**
- Guarden cada producción como `(cabeza, cuerpo)`, con el cuerpo como **lista de símbolos**. ε es la lista vacía (`[]`) y nunca el carácter `e` dentro del cuerpo.
- Numeren las producciones. Se necesitan para `reduce j` y para los ítems (pares (producción, punto), como sugiere el libro).
- Usen **cadenas** (no caracteres) para representar símbolos. Así el símbolo aumentado puede ser `"S'"` y no choca con ningún terminal, que podría ser cualquier carácter que no sea una mayúscula, `e` ni `$`.
- Terminal ⇔ no es una letra mayúscula, según las convenciones de §2.2 del enunciado.
- La primera línea de la gramática **no** es necesariamente la de S.

**FIRST y FOLLOW**
- Calcúlenlos con iteración de punto fijo (`while cambió:`), como dice el libro: "apply the rules until nothing can be added".
- Escriban una función `first_of_string(lista_de_símbolos)` y úsenla en la regla 2 de FOLLOW y en el Algoritmo 4.31.
- Representen ε y `$` con marcadores internos (por ejemplo `"ε"` y `"$"`) y conviértanlos a `e` y `$` solo al imprimir.

**LL(1)**
- La tabla es un diccionario `(A, a) → lista de producciones`. **Si alguna lista tiene más de un elemento, la gramática no es LL(1).** Es la misma prueba que la definición de §4.4.3, como se explicó en la sección 2.3.
- Si quieren, implementen también la verificación explícita por pares (FIRST(α) ∩ FIRST(β), etc.) para mostrar que sigue la definición. Las dos deben coincidir.

**SLR(1)**
- Un ítem es `(nro_producción, posición_punto)` y un estado es un `frozenset` de ítems, para poder compararlos y buscarlos en `C`.
- `ACTION` es un diccionario `(estado, terminal) → conjunto de acciones`. **Si algún conjunto tiene más de una acción, la gramática no es SLR(1).** Esto detecta tanto conflictos desplazar/reducir como reducir/reducir.
- `GOTO` es un diccionario `(estado, no_terminal) → estado`.
- La reducción por ε desapila **0** estados.

**Entrada y salida**
- Agreguen `$` al final de cada cadena.
- La línea `e` representa la cadena vacía, y una **línea vacía** termina la lectura.
- Una cadena con un carácter que no es terminal de la gramática no tiene entrada en la tabla, así que da `no`.

**Árbol de análisis (para el ítem 3)**
- **Con LL(1):** la pila guarda nodos. Al expandir `X → Y₁…Yₖ`, se crean los hijos del nodo X y se apilan en orden inverso. Al reconocer un terminal, la hoja ya existe y solo se desapila.
- **Con SLR(1):** se mantiene una pila de nodos paralela a la de estados. Al desplazar se apila una hoja. Al reducir por `A → β` se desapilan |β| nodos, se crea un nodo A con ellos como hijos (en orden) y se apila. Para ε, se crea un nodo A con una hoja ε o sin hijos.

**SDD como datos (exigido)**
- Cada regla guarda tres cosas:
  - el **atributo que define**, como `(posición, nombre)`, donde la posición 0 es la cabeza y 1…n son los símbolos del cuerpo;
  - la **lista de atributos que usa**, en el mismo formato;
  - **la función** que calcula el valor.
- Ejemplo (pseudo-Python) para `P → (P)P`:
  ```python
  SDD[("P", ("(", "P", ")", "P"))] = [
      Rule(target=(2, "d"), deps=[(0, "d")],           fn=lambda d: d + 1),
      Rule(target=(4, "d"), deps=[(0, "d")],           fn=lambda d: d),
      Rule(target=(0, "m"), deps=[(2, "m"), (4, "m")], fn=lambda a, b: max(a, b)),
  ]
  ```
- El evaluador recorre el árbol y, en cada nodo interno, **instancia** las reglas de su producción: traduce cada posición al nodo concreto (el propio nodo o su hijo i) y crea los vértices y aristas.
- **El evaluador no debe saber nada de su SDD en particular**: cambiar la SDD solo debe requerir cambiar estos datos.

---

## 10. Teoremas y propiedades para justificar

| # | Enunciado | Fuente |
|---|---|---|
| 1 | G es LL(1) ⇔ para todo par `A → α \| β`: FIRST(α) ∩ FIRST(β) = ∅ y, si ε ∈ FIRST(β), FIRST(α) ∩ FOLLOW(A) = ∅ (y simétrico). | §4.4.3 |
| 2 | G es LL(1) ⇔ la tabla del Algoritmo 4.31 no tiene celdas con más de una producción. | §4.4.3 (después del Ej. 4.32) |
| 3 | Ninguna gramática recursiva por la izquierda o ambigua es LL(1). | §4.4.3 |
| 4 | Hay lenguajes sin ninguna gramática LL(1) (por ejemplo, el dangling-else). | §4.4.3, Ej. 4.33 |
| 5 | El parser LL simula una derivación por la izquierda: si se reconoció w, la pila contiene α con `S ⇒*lm wα`. | §4.4.4 |
| 6 | El análisis ascendente construye una derivación por la derecha al revés. | §4.5.1, §4.5.2 |
| 7 | En una gramática no ambigua, cada forma sentencial derecha tiene exactamente un mango. | §4.5.2 |
| 8 | En un parser de desplazamiento-reducción, el mango siempre aparece en la cima de la pila. | §4.5.3 (Fig. 4.29) |
| 9 | Una gramática ambigua nunca es LR. | §4.5.4, Ej. 4.38 |
| 10 | Las gramáticas LR son un superconjunto propio de las LL (para LR(k) en general; **no** toda LL(1) es SLR(1)). | §4.6.1 |
| 11 | G es SLR(1) ⇔ la tabla del Algoritmo 4.46 no tiene conflictos. | §4.6.4 |
| 12 | Toda gramática SLR(1) es no ambigua; hay no ambiguas que no son SLR(1). | §4.6.4, Ej. 4.48 |
| 13 | El autómata LR(0) reconoce los prefijos viables; los ítems válidos para γ son los del estado al que se llega con γ. | §4.6.5 |
| 14 | CLOSURE es una ε-clausura y `items(G')` es la construcción de subconjuntos sobre el AFN de ítems. | §4.6.5 (recuadro) |
| 15 | Hay un orden de evaluación ⇔ el grafo de dependencias es acíclico (existe un orden topológico). | §5.2.2 |
| 16 | Decidir si una SDD puede producir un grafo con ciclos en **algún** árbol es exponencial. | §5.1.2 (nota al pie) |
| 17 | Una SDD S-atribuida se evalúa en postorden, que coincide con el orden de reducción LR. | §5.2.3 |
| 18 | Las SDD S-atribuidas y las L-atribuidas garantizan que existe un orden de evaluación. | §5.2.3, §5.2.4 |

---

## 11. Errores frecuentes

**Ítems 1 y 2**
1. Olvidar que FOLLOW nunca lleva ε, o meter ε en FOLLOW.
2. En FIRST(X₁…Xₙ), no seguir con X₂ cuando X₁ deriva ε, o agregar ε aunque solo **algunos** Xᵢ sean anulables.
3. Olvidar `$` ∈ FOLLOW(S).
4. Aplicar las reglas de FOLLOW solo a la primera aparición de B en un cuerpo.
5. Quitar la recursión izquierda antes de probar si es LL(1). **Está prohibido.**
6. En la tabla LL, no poner las producciones `A → ε` en las columnas de FOLLOW(A), incluida `$`.
7. En SLR, poner las reducciones en **todas** las columnas (eso es LR(0)) en lugar de solo las de FOLLOW(A).
8. Al reducir por `A → ε`, desapilar 1 en vez de 0.
9. Aceptar sin comprobar que la entrada es `$`. Aceptar en LL con la pila vacía pero entrada sobrante.
10. Olvidar aumentar la gramática con `S' → S`, o usar como S' una letra que podría coincidir con un no terminal.
11. Usar el parser LL sobre una tabla con conflictos, lo que puede producir un ciclo infinito.
12. Imprimir los conjuntos en otro orden o formato distinto al de `--sets`.

**Ítem 3** (los cuatro primeros los nombra el enunciado)
13. Dibujar las aristas al revés. Deben ir de lo **usado** a lo **definido**.
14. Evaluar en un orden fijo (postorden, preorden) en vez de usar el orden topológico del grafo.
15. Olvidar que los atributos de los terminales ya se conocen, o definir un atributo dos veces.
16. Darle atributos heredados a S.
17. Escribir la SDD dentro del evaluador en lugar de como datos.

---

## 12. Preguntas probables en la sustentación

Todos los integrantes deben poder responderlas.

- **¿Qué es FIRST(α)? ¿Y FOLLOW(A)? ¿Por qué FOLLOW nunca tiene ε?**
  FOLLOW se define como un conjunto de **terminales** (más `$`) que aparecen a la derecha de A. ε no es un terminal.
- **¿Por qué se itera hasta que nada cambie?**
  Las definiciones son mutuamente recursivas (FIRST(A) puede depender de FIRST(B) y viceversa). El resultado es el menor punto fijo, y se llega a él porque los conjuntos solo crecen y son finitos.
- **¿Por qué una gramática recursiva por la izquierda no es LL(1)?**
  Con `A → Aα | β`, FIRST(β) ⊆ FIRST(Aα), así que hay una celda con dos producciones.
- **¿Por qué los símbolos se apilan al revés en el parser LL?**
  Para que Y₁ quede en la cima y se procese primero, ya que se busca una derivación por la izquierda.
- **¿Qué es un ítem? ¿Qué significa el punto?**
  Indica cuánto del cuerpo se ha visto.
- **¿Para qué sirve aumentar la gramática?**
  Para saber cuándo aceptar: al reducir por `S' → S` con `$` en la entrada.
- **¿Qué hacen CLOSURE y GOTO? ¿Qué relación tienen con los AFN y AFD?**
  CLOSURE es una ε-clausura y la colección canónica es la construcción de subconjuntos (§4.6.5).
- **¿Por qué SLR usa FOLLOW?**
  Para reducir por `A → α` solo cuando el siguiente símbolo puede seguir a A.
- **¿Cuál es la diferencia entre un conflicto desplazar/reducir y uno reducir/reducir?** Den un ejemplo de cada uno (sección 5).
- **¿Una gramática puede ser LL(1) y no SLR(1)?**
  Sí. Contraejemplo de la sección 5: `S → AaAb | BbBa`, `A → ε`, `B → ε`.
- **¿Toda gramática SLR es no ambigua? ¿Y al revés?**
  Sí. No: ver el Ejemplo 4.48.
- **¿Qué es un mango? ¿Por qué siempre está en la cima de la pila?**
- **Hagan a mano FIRST, FOLLOW, la tabla LL(1) o el autómata y la tabla SLR de una gramática nueva.**
  Practiquen con las gramáticas de la sección 5 y con los ejercicios 4.4.x y 4.6.x del libro.
- **Diferencia entre atributo sintetizado y heredado. ¿Por qué S no puede tener heredados?**
  No tiene padre que se los defina.
- **¿Qué es un grafo de dependencias? ¿En qué dirección van las aristas?**
- **¿Por qué no basta con recorrer el árbol en postorden?**
  Solo sirve para SDD S-atribuidas. Si hay heredados, un valor puede depender de un hermano o del padre que todavía no se ha calculado.
- **¿Cómo detectan un ciclo?**
  Kahn termina con vértices sin ordenar.
- **Su SDD, ¿es S-atribuida, L-atribuida o ninguna? Justifíquenlo regla por regla.**
- **Modifiquen una regla en el momento** (por ejemplo, cambien `max` por suma). Como la SDD está guardada como datos, solo se toca la tabla de reglas.

---

*Fuente de todas las definiciones, algoritmos y ejemplos numerados: Aho, A. V., Lam, M. S., Sethi, R. y Ullman, J. D. (2007). Compilers: Principles, Techniques, and Tools (2.ª ed.). Addison-Wesley, §4.4–4.6 (pp. 217–257) y §5.1–5.2 (pp. 304–317).*
