"""
Ítem 2: parser LL(1) (descendente, predictivo, no recursivo).

    * Prueba LL(1): definición al inicio de §4.4.3.
    * Tabla predictiva M[A, a]: Algoritmo 4.31 (§4.4.3).
    * Análisis con pila y tabla: Algoritmo 4.34, Fig. 4.20 (§4.4.4).

La gramática NO se transforma (no se elimina la recursión izquierda) antes de
la prueba, tal como exige el enunciado.
"""

from .grammar import EPSILON, END, is_nonterminal
from .first_follow import first_of_string, format_set
from .parse_tree import Node, terminal_leaf, epsilon_leaf


def ll1_violations(grammar, first, follow):
    """
    Prueba de §4.4.3. G es LL(1) si y solo si, para cada par de producciones
    distintas A -> α | β:
      1. α y β no derivan cadenas que empiecen con el mismo terminal;
      2. a lo sumo una de las dos deriva ε;
      3. si β =>* ε, α no deriva cadenas que empiecen con un terminal de
         FOLLOW(A) (y lo mismo intercambiando α y β).
    Con conjuntos: 1 y 2 equivalen a FIRST(α) ∩ FIRST(β) = ∅, y 3 a
    "si ε ∈ FIRST(β), FIRST(α) ∩ FOLLOW(A) = ∅".
    Devuelve la lista de violaciones (vacía si la gramática es LL(1)).
    """
    violations = []
    for A in grammar.nonterminals:
        indices = grammar.by_head[A]
        for x in range(len(indices)):
            for y in range(x + 1, len(indices)):        # cada par distinto
                alpha = grammar.productions[indices[x]]
                beta = grammar.productions[indices[y]]
                first_alpha = first_of_string(alpha.body, first)
                first_beta = first_of_string(beta.body, first)
                pair = f"{alpha} | {beta.body_text()}"

                common = (first_alpha & first_beta) - {EPSILON}
                if common:
                    violations.append(f"{pair}: condition 1, both can start with {format_set(common)}")
                if EPSILON in first_alpha and EPSILON in first_beta:
                    violations.append(f"{pair}: condition 2, both derive the empty string")
                if EPSILON in first_beta and (first_alpha - {EPSILON}) & follow[A]:
                    violations.append(f"{pair}: condition 3, FIRST({alpha.body_text()}) and FOLLOW({A}) intersect")
                if EPSILON in first_alpha and (first_beta - {EPSILON}) & follow[A]:
                    violations.append(f"{pair}: condition 3, FIRST({beta.body_text()}) and FOLLOW({A}) intersect")
    return violations


def build_ll1_table(grammar, first, follow):
    """
    Algoritmo 4.31. Para cada producción A -> α:
      1. para cada terminal a ∈ FIRST(α), agregar A -> α a M[A, a];
      2. si ε ∈ FIRST(α), agregar A -> α a M[A, b] para cada b ∈ FOLLOW(A)
         (incluido $ si $ ∈ FOLLOW(A)).
    Las celdas ausentes son error. Cada celda es una lista de índices de
    producciones; si alguna tiene más de una, la gramática no es LL(1).
    """
    table = {}

    def add(A, a, index):
        cell = table.setdefault((A, a), [])
        if index not in cell:          # evita contar dos veces la misma producción
            cell.append(index)

    for index, production in enumerate(grammar.productions):
        first_alpha = first_of_string(production.body, first)
        for a in first_alpha - {EPSILON}:                 # paso 1
            add(production.head, a, index)
        if EPSILON in first_alpha:                        # paso 2
            for b in follow[production.head]:
                add(production.head, b, index)
    return table


class LL1Parser:
    name = "LL(1)"

    def __init__(self, grammar, first, follow):
        self.grammar = grammar
        self.violations = ll1_violations(grammar, first, follow)
        self.is_ll1 = not self.violations
        self.table = build_ll1_table(grammar, first, follow)

    def table_conflicts(self):
        """Celdas con más de una producción (existen si y solo si no es LL(1))."""
        return {cell: prods for cell, prods in self.table.items() if len(prods) > 1}

    def parse(self, tokens, trace=None):
        """
        Algoritmo 4.34 (Fig. 4.20). tokens es la lista de terminales de la
        cadena, SIN el $ (aquí se agrega). Devuelve la raíz del árbol de
        análisis si la cadena pertenece al lenguaje, o None si no.
        Si trace es una lista, se le agregan las filas de la Fig. 4.21.
        """
        if not self.is_ll1:
            raise ValueError("la gramática no es LL(1)")

        symbols = list(tokens) + [END]     # w$ en el búfer de entrada
        position = 0
        a = symbols[position]              # "let a be the first symbol of w$"

        root = Node(self.grammar.start)
        # La pila guarda pares (símbolo, nodo del árbol). La cima es el final
        # de la lista. Al inicio: S encima de $.
        stack = [(END, None), (self.grammar.start, root)]
        X, node = stack[-1]                # "let X be the top stack symbol"

        while X != END:                    # mientras la pila no esté vacía
            if X == a:
                self._record(trace, symbols, position, stack, f"match {a}")
                stack.pop()                # se reconoce el terminal
                position += 1
                a = symbols[position]
            elif not is_nonterminal(X):
                self._record(trace, symbols, position, stack, "error")
                return None                # terminal en la pila que no coincide
            elif (X, a) not in self.table:
                self._record(trace, symbols, position, stack, "error")
                return None                # celda vacía de la tabla
            else:
                production = self.grammar.productions[self.table[(X, a)][0]]
                self._record(trace, symbols, position, stack, f"output {production}")
                # Se construye el subárbol: los hijos del nodo de X son los
                # símbolos del cuerpo (o una hoja ε si el cuerpo es vacío).
                node.production = production
                children = [Node(Y) if is_nonterminal(Y) else terminal_leaf(Y)
                            for Y in production.body]
                node.children = children if children else [epsilon_leaf()]
                stack.pop()
                # Se apilan Yk, ..., Y1 para que Y1 quede en la cima.
                for Y, child in reversed(list(zip(production.body, children))):
                    stack.append((Y, child))
            X, node = stack[-1]            # "let X be the top stack symbol"

        # La pila llegó a $: se acepta solo si también se consumió la entrada.
        accepted = a == END
        self._record(trace, symbols, position, stack, "accept" if accepted else "error")
        return root if accepted else None

    def _record(self, trace, symbols, position, stack, action):
        """Guarda una fila (reconocido, pila con la cima a la izquierda, entrada, acción)."""
        if trace is None:
            return
        matched = "".join(symbols[:position])
        stack_text = " ".join(symbol for symbol, _ in reversed(stack))
        remaining = "".join(symbols[position:])
        trace.append((matched, stack_text, remaining, action))

    def table_lines(self):
        """Tabla M en texto: una fila por no terminal, una columna por terminal y $."""
        columns = self.grammar.terminals + [END]
        rows = [["", *columns]]
        for A in sorted(self.grammar.nonterminals):
            row = [A]
            for a in columns:
                cell = self.table.get((A, a), [])
                row.append(" | ".join(str(self.grammar.productions[i]) for i in cell))
            rows.append(row)
        return format_grid(rows)


def format_grid(rows):
    """Alinea una tabla de texto en columnas."""
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    return ["  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip()
            for row in rows]
