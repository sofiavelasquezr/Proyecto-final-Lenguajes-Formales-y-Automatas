"""
Ítem 2: parser SLR(1) (ascendente, desplazamiento-reducción).

    * Gramática aumentada, ítems LR(0), CLOSURE, GOTO y colección canónica:
      §4.6.2, Figs. 4.32 y 4.33.
    * Tablas ACTION y GOTO: Algoritmo 4.46 (§4.6.4). La gramática es SLR(1)
      si y solo si la tabla no tiene conflictos.
    * Análisis: algoritmo LR, Algoritmo 4.44, Fig. 4.36 (§4.6.3).
"""

from .grammar import END, AUGMENTED_START, Production, is_nonterminal
from .parse_tree import Node, terminal_leaf, epsilon_leaf
from .ll1 import format_grid

# Un ítem LR(0) se representa con el par (número de producción, posición del
# punto), como sugiere el libro en el recuadro "Representing Item Sets".
# Un estado (conjunto de ítems) es un frozenset de esos pares.

SHIFT, REDUCE, ACCEPT = "shift", "reduce", "accept"


class SLR1Parser:
    name = "SLR(1)"

    def __init__(self, grammar, first, follow):
        self.grammar = grammar
        # Gramática aumentada G': la producción 0 es S' -> S y la producción i
        # (i >= 1) es la producción i-1 de la gramática original. Así los
        # números de "reduce" coinciden con la numeración 1, 2, ... del libro.
        self.productions = [Production(AUGMENTED_START, (grammar.start,))] + grammar.productions
        self.by_head = {}
        for index, production in enumerate(self.productions):
            self.by_head.setdefault(production.head, []).append(index)

        # Orden en que se prueban los símbolos X en GOTO(I, X): primero los no
        # terminales y luego los terminales, en orden de aparición. Con este
        # orden los estados se numeran como en la Fig. 4.31 del libro.
        self.symbols = grammar.nonterminals + grammar.terminals_in_order

        self.states, self.transitions = self.canonical_collection()
        self.action, self.goto_table = self.build_table(follow)
        self.conflicts = {cell: acts for cell, acts in self.action.items() if len(acts) > 1}
        self.is_slr1 = not self.conflicts

    # ------------------------------------------------------------------
    # §4.6.2: CLOSURE, GOTO y colección canónica de conjuntos de ítems LR(0)
    # ------------------------------------------------------------------

    def closure(self, items):
        """
        CLOSURE(I), Fig. 4.32:
          1. todo ítem de I está en CLOSURE(I);
          2. si A -> α·Bβ está en CLOSURE(I) y B -> γ es una producción, se
             agrega B -> ·γ. Se repite hasta que no se agreguen ítems.
        """
        J = set(items)
        changed = True
        while changed:                                  # repeat ... until
            changed = False
            for production_index, dot in list(J):
                body = self.productions[production_index].body
                if dot < len(body) and is_nonterminal(body[dot]):
                    B = body[dot]                       # símbolo después del punto
                    for b_index in self.by_head[B]:
                        if (b_index, 0) not in J:
                            J.add((b_index, 0))         # B -> ·γ
                            changed = True
        return frozenset(J)

    def goto(self, items, X):
        """
        GOTO(I, X): clausura de los ítems [A -> αX·β] tales que [A -> α·Xβ]
        está en I (se mueve el punto sobre X).
        """
        moved = set()
        for production_index, dot in items:
            body = self.productions[production_index].body
            if dot < len(body) and body[dot] == X:
                moved.add((production_index, dot + 1))
        return self.closure(moved) if moved else frozenset()

    def canonical_collection(self):
        """
        Fig. 4.33 (procedimiento items(G')):
            C = { CLOSURE({[S' -> ·S]}) };
            repeat
                for (cada conjunto I en C)
                    for (cada símbolo X)
                        if (GOTO(I, X) no es vacío y no está en C) agregarlo a C;
            until no se agreguen conjuntos nuevos.
        Recorrer la lista C con un índice que avanza mientras C crece es
        equivalente: cuando el índice alcanza el final, ninguna ronda puede
        agregar conjuntos nuevos. También se guardan las transiciones.
        """
        states = [self.closure({(0, 0)})]   # I0 = CLOSURE({[S' -> ·S]})
        number_of = {states[0]: 0}          # conjunto de ítems -> número de estado
        transitions = {}                    # (estado, símbolo) -> estado
        i = 0
        while i < len(states):
            for X in self.symbols:
                target = self.goto(states[i], X)
                if not target:
                    continue
                if target not in number_of:
                    number_of[target] = len(states)
                    states.append(target)
                transitions[(i, X)] = number_of[target]
            i += 1
        return states, transitions

    # ------------------------------------------------------------------
    # §4.6.4: Algoritmo 4.46, tabla SLR
    # ------------------------------------------------------------------

    def build_table(self, follow):
        """
        Para cada estado i (conjunto Ii):
          (a) si [A -> α·aβ] ∈ Ii, a terminal, y GOTO(Ii, a) = Ij:
              ACTION[i, a] = shift j;
          (b) si [A -> α·] ∈ Ii, A ≠ S': ACTION[i, a] = reduce A -> α para
              todo a ∈ FOLLOW(A);
          (c) si [S' -> S·] ∈ Ii: ACTION[i, $] = accept.
          GOTO[i, A] = j si GOTO(Ii, A) = Ij.
        Cada celda de ACTION es una lista de acciones; si alguna tiene más de
        una, hay un conflicto y la gramática no es SLR(1).
        """
        action = {}

        def add(state, terminal, act):
            cell = action.setdefault((state, terminal), [])
            if act not in cell:            # varios ítems pueden dar el mismo shift
                cell.append(act)

        for i, items in enumerate(self.states):
            for production_index, dot in sorted(items):
                production = self.productions[production_index]
                if dot < len(production.body):
                    a = production.body[dot]
                    if not is_nonterminal(a):                         # regla (a)
                        add(i, a, (SHIFT, self.transitions[(i, a)]))
                elif production_index == 0:                           # regla (c)
                    add(i, END, (ACCEPT,))
                else:                                                 # regla (b)
                    for a in follow[production.head]:
                        add(i, a, (REDUCE, production_index))

        goto_table = {(i, X): j for (i, X), j in self.transitions.items()
                      if is_nonterminal(X)}
        return action, goto_table

    # ------------------------------------------------------------------
    # §4.6.3: Algoritmo 4.44, el programa de análisis LR
    # ------------------------------------------------------------------

    def parse(self, tokens, trace=None):
        """
        Algoritmo 4.44 (Fig. 4.36). tokens es la lista de terminales SIN el $.
        Devuelve la raíz del árbol de análisis (nodo S) o None si la cadena no
        pertenece al lenguaje. Si trace es una lista, se le agregan las filas
        de la Fig. 4.38.
        """
        if not self.is_slr1:
            raise ValueError("la gramática no es SLR(1)")

        symbols = list(tokens) + [END]
        position = 0
        a = symbols[position]          # "let a be the first symbol of w$"
        states = [0]                   # pila de estados; s0 en el fondo
        nodes = []                     # pila paralela de nodos del árbol
                                       # (nodes[k] corresponde a states[k+1])
        while True:
            s = states[-1]             # "let s be the state on top of the stack"
            cell = self.action.get((s, a))
            if not cell:
                self._record(trace, states, nodes, symbols, position, "error")
                return None            # celda vacía: error de sintaxis
            act = cell[0]

            if act[0] == SHIFT:
                t = act[1]
                self._record(trace, states, nodes, symbols, position, f"shift {t}")
                states.append(t)                        # push t
                nodes.append(terminal_leaf(a))
                position += 1
                a = symbols[position]                   # siguiente símbolo

            elif act[0] == REDUCE:
                production = self.productions[act[1]]
                r = len(production.body)                # |β|; es 0 si A -> ε
                self._record(trace, states, nodes, symbols, position,
                             f"reduce {production}")
                children = nodes[len(nodes) - r:]       # los r nodos de β
                del states[len(states) - r:]            # pop |β| estados
                del nodes[len(nodes) - r:]
                t = states[-1]                          # estado expuesto
                states.append(self.goto_table[(t, production.head)])  # push GOTO[t, A]
                parent = Node(production.head, production)
                parent.children = children if children else [epsilon_leaf()]
                nodes.append(parent)

            else:  # ACCEPT
                self._record(trace, states, nodes, symbols, position, "accept")
                return nodes[-1]                        # el nodo S es la raíz

    def _record(self, trace, states, nodes, symbols, position, action):
        """Guarda una fila (pila, símbolos, entrada, acción) como en la Fig. 4.38."""
        if trace is None:
            return
        trace.append((" ".join(map(str, states)),
                      " ".join(node.symbol for node in nodes),
                      "".join(symbols[position:]),
                      action))

    # ------------------------------------------------------------------
    # Impresión del autómata y de la tabla (para el informe)
    # ------------------------------------------------------------------

    def item_text(self, item):
        production_index, dot = item
        production = self.productions[production_index]
        body = list(production.body)
        body.insert(dot, "·")
        return f"{production.head} -> {''.join(body)}"

    def action_text(self, act):
        if act[0] == SHIFT:
            return f"s{act[1]}"
        if act[0] == REDUCE:
            return f"r{act[1]}"
        return "acc"

    def automaton_lines(self):
        lines = ["Productions of the augmented grammar:"]
        for index, production in enumerate(self.productions):
            lines.append(f"  ({index}) {production}")
        lines.append("Canonical collection of sets of LR(0) items:")
        for i, items in enumerate(self.states):
            lines.append(f"  I{i}:")
            for item in sorted(items):
                lines.append(f"      {self.item_text(item)}")
            for X in self.symbols:
                if (i, X) in self.transitions:
                    lines.append(f"      GOTO(I{i}, {X}) = I{self.transitions[(i, X)]}")
        return lines

    def table_lines(self):
        terminals = self.grammar.terminals + [END]
        nonterminals = self.grammar.nonterminals
        rows = [["STATE", *terminals, *nonterminals]]
        for i in range(len(self.states)):
            row = [str(i)]
            for a in terminals:
                row.append("/".join(self.action_text(act) for act in self.action.get((i, a), [])))
            for A in nonterminals:
                row.append(str(self.goto_table[(i, A)]) if (i, A) in self.goto_table else "")
            rows.append(row)
        return format_grid(rows)
