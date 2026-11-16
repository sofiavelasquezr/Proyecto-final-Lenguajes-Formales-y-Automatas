"""
La SDD de nuestro grupo para el ítem 3 (SOLO DATOS; no tiene lógica).

Lenguaje: listas anidadas de dígitos, por ejemplo  [1,[2,3]]  o  [[],[4]].
Traducción: la SUMA PONDERADA POR PROFUNDIDAD, donde cada dígito se multiplica
por la profundidad de la lista que lo contiene (la lista exterior tiene
profundidad 1):
        [1,[2,3]]  ->  1*1 + 2*2 + 3*2 = 11

Gramática (formato de la sección 2.2; es LL(1) y SLR(1)):
    S -> L                        lista principal
    L -> [E]                      una lista entre corchetes
    E -> IR | ε                   elementos de la lista (o lista vacía)
    R -> ,IR | ε                  resto de los elementos
    I -> L | 0 | 1 | ... | 9      un elemento: una sublista o un dígito
5 no terminales, 17 producciones; L es recursivo (L -> [E], E -> IR, I -> L).
"""

from sdd.evaluator import SDD, Attribute, Rule, SYN, INH

GRAMMAR_TEXT = """\
5
S -> L
L -> [E]
E -> IR e
R -> ,IR e
I -> L 0 1 2 3 4 5 6 7 8 9
"""

# Tabla de atributos (paso 2.1): símbolo, nombre, tipo de atributo, tipo de dato y significado.
ATTRIBUTES = {
    "S": {"v": Attribute(SYN, "int", "depth-weighted sum of the whole list (main attribute)")},
    "L": {"d": Attribute(INH, "int", "depth of the level where this list appears (0 for the outer list)"),
          "s": Attribute(SYN, "int", "depth-weighted sum of the digits inside this list")},
    "E": {"d": Attribute(INH, "int", "depth of the elements of this list"),
          "s": Attribute(SYN, "int", "depth-weighted sum of these elements")},
    "R": {"d": Attribute(INH, "int", "depth of the remaining elements"),
          "s": Attribute(SYN, "int", "depth-weighted sum of the remaining elements")},
    "I": {"d": Attribute(INH, "int", "depth of this element"),
          "s": Attribute(SYN, "int", "contribution of this element to the sum")},
}

# Reglas semánticas (paso 2.2), indexadas por producción.
# Posición 0 = cabeza; posición i = i-ésimo símbolo del cuerpo.
#   Por ejemplo, en "L -> [E]": 0 = L, 1 = '[', 2 = E, 3 = ']'.
RULES = {
    "S -> L": [
        Rule(target=(1, "d"), deps=(), fn=lambda: 0, text="L.d = 0"),
        Rule(target=(0, "v"), deps=((1, "s"),), fn=lambda s: s, text="S.v = L.s"),
    ],
    "L -> [E]": [
        Rule(target=(2, "d"), deps=((0, "d"),), fn=lambda d: d + 1, text="E.d = L.d + 1"),
        Rule(target=(0, "s"), deps=((2, "s"),), fn=lambda s: s, text="L.s = E.s"),
    ],
    "E -> IR": [
        Rule(target=(1, "d"), deps=((0, "d"),), fn=lambda d: d, text="I.d = E.d"),
        Rule(target=(2, "d"), deps=((0, "d"),), fn=lambda d: d, text="R.d = E.d"),
        Rule(target=(0, "s"), deps=((1, "s"), (2, "s")), fn=lambda a, b: a + b, text="E.s = I.s + R.s"),
    ],
    "E -> e": [
        Rule(target=(0, "s"), deps=(), fn=lambda: 0, text="E.s = 0"),
    ],
    "R -> ,IR": [
        Rule(target=(2, "d"), deps=((0, "d"),), fn=lambda d: d, text="I.d = R.d"),
        Rule(target=(3, "d"), deps=((0, "d"),), fn=lambda d: d, text="R1.d = R.d"),
        Rule(target=(0, "s"), deps=((2, "s"), (3, "s")), fn=lambda a, b: a + b, text="R.s = I.s + R1.s"),
    ],
    "R -> e": [
        Rule(target=(0, "s"), deps=(), fn=lambda: 0, text="R.s = 0"),
    ],
    "I -> L": [
        Rule(target=(1, "d"), deps=((0, "d"),), fn=lambda d: d, text="L.d = I.d"),
        Rule(target=(0, "s"), deps=((1, "s"),), fn=lambda s: s, text="I.s = L.s"),
    ],
}

# I -> 0 | 1 | ... | 9 : el aporte de un dígito es profundidad * valor.
for digit in "0123456789":
    RULES[f"I -> {digit}"] = [
        Rule(target=(0, "s"), deps=((0, "d"), (1, "lexval")),
             fn=lambda d, lexval: d * int(lexval),
             text=f"I.s = I.d * int({digit}.lexval)"),
    ]


def build_sdd():
    return SDD(ATTRIBUTES, RULES, main_attribute="v")


def build_circular_sdd():
    """
    Variante circular para el paso 6: en S -> L se cambia  L.d = 0  por
    L.d = L.s. Ahora L.d depende de L.s, que depende (bajando por el árbol)
    de los I.d, que a su vez dependen de L.d: hay un ciclo en cuanto la lista
    contiene al menos un dígito (por ejemplo, [1]).
    """
    rules = dict(RULES)
    rules["S -> L"] = [
        Rule(target=(1, "d"), deps=((1, "s"),), fn=lambda s: s, text="L.d = L.s"),
        Rule(target=(0, "v"), deps=((1, "s"),), fn=lambda s: s, text="S.v = L.s"),
    ]
    return SDD(ATTRIBUTES, rules, main_attribute="v")
