"""
Árbol de análisis (parse tree) que construyen los dos parsers.

Cada nodo guarda (sección 3, paso 5.2 del enunciado):
    * su símbolo,
    * la producción usada (si es un no terminal),
    * sus hijos,
    * los valores de sus atributos.
"""

from .grammar import EPSILON


class Node:
    def __init__(self, symbol, production=None):
        self.symbol = symbol
        self.production = production   # objeto Production, o None si es hoja
        self.children = []
        self.attrs = {}                # nombre del atributo -> valor
        self.id = None                 # número en preorden (lo asigna number_nodes)

    def is_leaf(self):
        return self.production is None

    def is_epsilon(self):
        return self.symbol == EPSILON


def terminal_leaf(symbol):
    """Hoja para un terminal. Su atributo lexval es el propio carácter (paso 2.1)."""
    leaf = Node(symbol)
    leaf.attrs["lexval"] = symbol
    return leaf


def epsilon_leaf():
    """Hoja ε: hija única de un nodo cuya producción es A -> ε."""
    return Node(EPSILON)


def preorder(node):
    """Recorre el árbol en preorden (nodo, luego hijos de izquierda a derecha)."""
    yield node
    for child in node.children:
        yield from preorder(child)


def number_nodes(root):
    """Asigna a cada nodo un número en preorden (1, 2, 3, ...)."""
    for number, node in enumerate(preorder(root), start=1):
        node.id = number


def node_label(node):
    """Nombre corto de un nodo, por ejemplo 'L#2' o 'ε'."""
    return node.symbol if node.is_epsilon() else f"{node.symbol}#{node.id}"


def format_attrs(node):
    return ", ".join(f"{name}={value!r}" for name, value in node.attrs.items())


def format_tree(root):
    """Una línea por nodo, con sangría según la profundidad y sus atributos."""
    lines = []

    def visit(node, depth):
        text = "  " * depth + node_label(node)
        if node.production is not None:
            text += f"  ({node.production})"
        if node.attrs:
            text += "  " + format_attrs(node)
        lines.append(text)
        for child in node.children:
            visit(child, depth + 1)

    visit(root, 0)
    return lines
