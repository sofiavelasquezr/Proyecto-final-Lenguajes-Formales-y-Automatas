"""
Ítem 3: evaluador GENERAL de definiciones dirigidas por la sintaxis (SDD).

    * Atributos sintetizados y heredados: §5.1.1.
    * Grafo de dependencias: §5.2.1.
    * Orden de evaluación (ordenamiento topológico): §5.2.2.
    * Clasificación S-atribuida / L-atribuida: §5.2.3 y §5.2.4.

Este módulo NO sabe nada de ninguna SDD en particular: la SDD llega como datos
(un objeto SDD con sus atributos y sus reglas). Cambiar la SDD solo requiere
cambiar esos datos (paso 5.1 del enunciado).

Convención de posiciones en una producción A -> X1 X2 ... Xn:
    posición 0 = la cabeza A; posición i (1..n) = el símbolo Xi del cuerpo.
"""

from collections import Counter, deque
from dataclasses import dataclass

from parsing.grammar import is_nonterminal
from parsing.parse_tree import preorder, number_nodes, node_label

SYN = "synthesized"
INH = "inherited"
LEXVAL = "lexval"     # único atributo de los terminales (lo da el "scanner")


@dataclass(frozen=True)
class Attribute:
    """Una fila de la tabla de atributos (paso 2.1 del enunciado)."""
    kind: str          # SYN o INH
    type: str          # tipo del valor, por ejemplo "int"
    meaning: str       # significado


@dataclass(frozen=True)
class Rule:
    """
    Una regla semántica, guardada como datos (paso 5.1):
        target: (posición, atributo) que la regla DEFINE;
        deps:   ((posición, atributo), ...) que la regla USA;
        fn:     función que calcula el valor; recibe los valores de deps en orden;
        text:   la regla escrita como en el libro (para imprimirla).
    """
    target: tuple
    deps: tuple
    fn: object
    text: str


class SDD:
    def __init__(self, attributes, rules, main_attribute):
        self.attributes = attributes          # símbolo -> {nombre: Attribute}
        self.rules = rules                    # "A -> cuerpo" -> [Rule, ...]
        self.main_attribute = main_attribute  # atributo principal de S

    def rules_for(self, production):
        return self.rules.get(str(production), [])

    def kind(self, symbol, name):
        """SYN, INH o None (si el símbolo no tiene ese atributo)."""
        if not is_nonterminal(symbol):
            return SYN if name == LEXVAL else None   # terminales: solo lexval
        attribute = self.attributes.get(symbol, {}).get(name)
        return attribute.kind if attribute else None


class SDDError(Exception):
    """La SDD está mal definida (regla inválida, atributo sin definir, ...)."""


class CircularSDDError(SDDError):
    """El grafo de dependencias tiene un ciclo (§5.2.2)."""
    def __init__(self, cycle):
        self.cycle = cycle            # lista de etiquetas "X#n.attr" del ciclo
        super().__init__("the SDD is circular: " + " -> ".join(cycle))


def symbol_at(production, position):
    return production.head if position == 0 else production.body[position - 1]


# ----------------------------------------------------------------------
# Revisión de la SDD (paso 2 del enunciado y §5.1.1)
# ----------------------------------------------------------------------

def validate_sdd(grammar, sdd):
    """
    Revisa, para cada producción, que:
      * cada regla defina un sintetizado de la cabeza o un heredado de un
        no terminal del cuerpo, usando solo atributos de esa misma producción;
      * cada sintetizado de la cabeza y cada heredado de cada no terminal del
        cuerpo se defina EXACTAMENTE una vez;
    y además que S no tenga atributos heredados. Devuelve la lista de problemas.
    """
    problems = []
    for name, attribute in sdd.attributes.get(grammar.start, {}).items():
        if attribute.kind == INH:
            problems.append(f"the start symbol {grammar.start} has the inherited attribute {name}")

    known = {str(p) for p in grammar.productions}
    for key in sdd.rules:
        if key not in known:
            problems.append(f"there are rules for '{key}', which is not a production")

    for production in grammar.productions:
        where = f"[{production}]"
        defined = Counter()
        for rule in sdd.rules_for(production):
            position, name = rule.target
            if not 0 <= position <= len(production.body):
                problems.append(f"{where} {rule.text}: position {position} does not exist")
                continue
            symbol = symbol_at(production, position)
            kind = sdd.kind(symbol, name)
            if not is_nonterminal(symbol):
                problems.append(f"{where} {rule.text}: terminals have no semantic rules")
            elif position == 0 and kind != SYN:
                problems.append(f"{where} {rule.text}: only synthesized attributes of the head can be defined")
            elif position > 0 and kind != INH:
                problems.append(f"{where} {rule.text}: only inherited attributes of the body can be defined")
            defined[(position, name)] += 1
            for dep_position, dep_name in rule.deps:
                if not 0 <= dep_position <= len(production.body):
                    problems.append(f"{where} {rule.text}: position {dep_position} does not exist")
                elif sdd.kind(symbol_at(production, dep_position), dep_name) is None:
                    problems.append(f"{where} {rule.text}: "
                                    f"{symbol_at(production, dep_position)} has no attribute {dep_name}")

        required = [(0, name) for name, attribute in sdd.attributes.get(production.head, {}).items()
                    if attribute.kind == SYN]
        for position, symbol in enumerate(production.body, start=1):
            if is_nonterminal(symbol):
                required += [(position, name) for name, attribute in sdd.attributes.get(symbol, {}).items()
                             if attribute.kind == INH]
        for position, name in required:
            symbol = symbol_at(production, position)
            if defined[(position, name)] == 0:
                problems.append(f"{where} {symbol}.{name} (position {position}) is never defined")
            elif defined[(position, name)] > 1:
                problems.append(f"{where} {symbol}.{name} (position {position}) is defined more than once")
    return problems


def classify_sdd(grammar, sdd):
    """
    §5.2.3: S-atribuida si todos los atributos son sintetizados.
    §5.2.4: L-atribuida si cada heredado Xi.a de una regla de A -> X1...Xn usa
    solo (a) heredados de la cabeza A, (b) atributos de X1..X(i-1), o (c)
    atributos de la misma Xi sin formar ciclos.
    Devuelve (es_S, es_L, explicación). es_L es True, False o None (None
    significa que depende de la condición (c), que no se verifica aquí).
    """
    is_s = all(attribute.kind == SYN
               for attributes in sdd.attributes.values() for attribute in attributes.values())
    is_l = True
    notes = []
    for production in grammar.productions:
        for rule in sdd.rules_for(production):
            i, name = rule.target
            if i == 0:
                continue                              # sintetizado: siempre permitido
            for j, dep_name in rule.deps:
                dep_symbol = symbol_at(production, j)
                if j == 0 and sdd.kind(dep_symbol, dep_name) == INH:
                    continue                          # (a) heredado de la cabeza
                if 1 <= j < i:
                    continue                          # (b) símbolo a la izquierda
                if j == i:
                    notes.append(f"[{production}] {rule.text}: uses {dep_symbol}.{dep_name} "
                                 f"of the same symbol, allowed only if condition (c) holds")
                    if is_l:
                        is_l = None
                    continue
                reason = ("a synthesized attribute of the head" if j == 0
                          else f"{dep_symbol}.{dep_name}, which is to the right")
                notes.append(f"[{production}] {rule.text}: uses {reason}, so it is not L-attributed")
                is_l = False
    return is_s, is_l, notes


# ----------------------------------------------------------------------
# Grafo de dependencias (§5.2.1)
# ----------------------------------------------------------------------

class DependencyGraph:
    def __init__(self):
        self.vertices = []      # vértice k -> (nodo, atributo)
        self.number = {}        # (id del nodo, atributo) -> vértice k
        self.edges = {}         # vértice -> lista de sucesores
        self.rule_of = {}       # vértice -> (Rule, nodo donde se aplica la regla)

    def vertex(self, node, name):
        """Devuelve el número del vértice de node.name, creándolo si no existe."""
        key = (node.id, name)
        if key not in self.number:
            self.number[key] = len(self.vertices)
            self.vertices.append((node, name))
            self.edges[self.number[key]] = []
        return self.number[key]

    def label(self, v):
        node, name = self.vertices[v]
        return f"{node_label(node)}.{name}"


def node_at(node, position):
    """Nodo que corresponde a una posición de la producción aplicada en node."""
    return node if position == 0 else node.children[position - 1]


def build_dependency_graph(root, sdd):
    """
    Un vértice por cada atributo de cada nodo. Para cada nodo interno se
    instancian las reglas de su producción: por cada regla, una arista DESDE
    cada atributo que usa HACIA el atributo que define. Las hojas aportan su
    lexval (vértices que ya tienen valor).
    """
    graph = DependencyGraph()
    for node in preorder(root):
        if node.is_leaf():
            if not node.is_epsilon():
                graph.vertex(node, LEXVAL)            # atributo ya conocido
            continue
        for rule in sdd.rules_for(node.production):
            target = graph.vertex(node_at(node, rule.target[0]), rule.target[1])
            if target in graph.rule_of:
                raise SDDError(f"{graph.label(target)} is defined twice")
            graph.rule_of[target] = (rule, node)
            for position, name in rule.deps:
                source = graph.vertex(node_at(node, position), name)
                graph.edges[source].append(target)    # usado -> definido
    return graph


# ----------------------------------------------------------------------
# Orden topológico y evaluación (§5.2.2)
# ----------------------------------------------------------------------

def topological_order(graph):
    """
    Algoritmo de la demostración de §5.2.2 (algoritmo de Kahn): se toma un
    vértice sin aristas de entrada, se pone en el orden, se elimina del grafo
    y se repite. Si quedan vértices pero ninguno sin entradas, hay un ciclo.
    """
    indegree = [0] * len(graph.vertices)
    for v in graph.edges:
        for w in graph.edges[v]:
            indegree[w] += 1
    ready = deque(v for v in range(len(graph.vertices)) if indegree[v] == 0)
    order = []
    while ready:
        v = ready.popleft()
        order.append(v)
        for w in graph.edges[v]:           # "eliminar" v del grafo
            indegree[w] -= 1
            if indegree[w] == 0:
                ready.append(w)
    if len(order) < len(graph.vertices):
        raise CircularSDDError(find_cycle(graph, indegree))
    return order


def find_cycle(graph, indegree):
    """
    Encuentra un ciclo con el argumento del libro: desde un vértice que todavía
    tiene aristas de entrada se retrocede de predecesor en predecesor hasta
    repetir un vértice.
    """
    predecessors = {v: [] for v in graph.edges}
    for v in graph.edges:
        for w in graph.edges[v]:
            predecessors[w].append(v)
    v = next(v for v in range(len(indegree)) if indegree[v] > 0)
    path = []
    while v not in path:
        path.append(v)
        v = next(u for u in predecessors[v] if indegree[u] > 0)
    cycle = path[path.index(v):]
    cycle.reverse()                        # en el sentido de las aristas
    return [graph.label(u) for u in cycle + [cycle[0]]]


def evaluate(root, sdd):
    """
    Construye el grafo, calcula un orden topológico y evalúa los atributos en
    ese orden. Devuelve (grafo, orden completo, vértices calculados por reglas).
    Lanza CircularSDDError si el grafo tiene un ciclo.
    """
    number_nodes(root)
    graph = build_dependency_graph(root, sdd)
    order = topological_order(graph)
    computed = []
    for v in order:
        node, name = graph.vertices[v]
        if v in graph.rule_of:
            rule, owner = graph.rule_of[v]
            arguments = [node_at(owner, position).attrs[dep] for position, dep in rule.deps]
            node.attrs[name] = rule.fn(*arguments)
            computed.append(v)
        elif name != LEXVAL:
            raise SDDError(f"{graph.label(v)} is used but no rule defines it")
    # Los atributos se muestran en el orden de la tabla de atributos.
    for node in preorder(root):
        declared = list(sdd.attributes.get(node.symbol, {}))
        node.attrs = {name: node.attrs[name] for name in declared + [LEXVAL] if name in node.attrs}
    return graph, order, computed
