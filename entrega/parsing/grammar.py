"""
Lectura y representación de gramáticas libres de contexto.

Formato de entrada (sección 2.2 del enunciado):
    n
    <no terminal> -> <alternativas separadas por espacios>
    ... (n líneas)

Convenciones:
    * Los no terminales son letras mayúsculas; 'S' es el símbolo inicial.
    * Los terminales son cualquier otro carácter (sin espacios), excepto 'e' y '$'.
    * La alternativa 'e' representa la cadena vacía (épsilon).
"""

from dataclasses import dataclass

# Marcadores internos. Usamos símbolos que nunca pueden ser terminales de la
# entrada, para no confundirlos con caracteres de la gramática.
EPSILON = "ε"          # cadena vacía (en la entrada y en la salida se escribe 'e')
END = "$"              # marcador de fin de entrada (§4.4.2)
START = "S"            # símbolo inicial de toda gramática del proyecto
AUGMENTED_START = "S'"  # símbolo inicial de la gramática aumentada (§4.6.2)


class GrammarError(Exception):
    """La entrada no respeta el formato de la sección 2.2 del enunciado."""


def is_nonterminal(symbol):
    """Un símbolo es no terminal si es una letra mayúscula A-Z (o el S' aumentado)."""
    return symbol == AUGMENTED_START or (len(symbol) == 1 and "A" <= symbol <= "Z")


@dataclass(frozen=True)
class Production:
    """Una producción  head -> body.  El cuerpo vacío () representa  head -> ε."""
    head: str
    body: tuple

    def body_text(self):
        """Cuerpo escrito como en la entrada: 'e' si es vacío."""
        return "".join(self.body) if self.body else "e"

    def __str__(self):
        return f"{self.head} -> {self.body_text()}"


class Grammar:
    """Gramática libre de contexto G = (N, T, P, S)."""

    def __init__(self, productions, nonterminals):
        # Las producciones se numeran según su posición en esta lista.
        self.productions = list(productions)
        # No terminales en el orden en que aparecen como cabeza en la entrada.
        self.nonterminals = list(nonterminals)
        self.start = START

        # Terminales en orden de primera aparición (sirve para numerar los
        # estados LR(0) igual que el libro) y en orden ASCII (para imprimir).
        seen = []
        for production in self.productions:
            for symbol in production.body:
                if not is_nonterminal(symbol) and symbol not in seen:
                    seen.append(symbol)
        self.terminals_in_order = seen
        self.terminals = sorted(seen)

        # Para cada no terminal A, la lista de índices de sus producciones.
        self.by_head = {A: [] for A in self.nonterminals}
        for index, production in enumerate(self.productions):
            self.by_head[production.head].append(index)

    def __str__(self):
        lines = []
        for A in self.nonterminals:
            alternatives = " ".join(self.productions[i].body_text() for i in self.by_head[A])
            lines.append(f"{A} -> {alternatives}")
        return "\n".join(lines)


def parse_production_line(line):
    """Convierte 'B -> bBc e' en ('B', [('b','B','c'), ()])."""
    if "->" not in line:
        raise GrammarError(f"falta '->' en la línea: {line!r}")
    head, right_side = line.split("->", 1)
    head = head.strip()
    if not (len(head) == 1 and is_nonterminal(head)):
        raise GrammarError(f"la cabeza debe ser una letra mayúscula: {head!r}")

    alternatives = right_side.split()      # separa por espacios en blanco
    if not alternatives:
        raise GrammarError(f"el no terminal {head} no tiene alternativas")

    bodies = []
    for alternative in alternatives:
        if alternative == "e":
            bodies.append(())              # la alternativa 'e' es épsilon
            continue
        for symbol in alternative:
            if symbol in ("e", "$"):
                raise GrammarError(f"'{symbol}' no puede usarse como terminal ({alternative!r})")
        bodies.append(tuple(alternative))  # cada carácter es un símbolo
    return head, bodies


def read_grammar(read_line):
    """
    Lee una gramática usando read_line(), que devuelve la siguiente línea sin
    el salto de línea, o None al final de la entrada.
    """
    first_line = read_line()
    while first_line is not None and first_line.strip() == "":
        first_line = read_line()           # tolera líneas vacías antes de n
    if first_line is None:
        raise GrammarError("la entrada está vacía")
    try:
        n = int(first_line.strip())
    except ValueError:
        raise GrammarError(f"la primera línea debe ser un número: {first_line!r}")
    if n <= 0:
        raise GrammarError("n debe ser mayor que 0")

    productions = []
    nonterminals = []
    for _ in range(n):
        line = read_line()
        if line is None or line.strip() == "":
            raise GrammarError(f"se esperaban {n} líneas de producciones")
        head, bodies = parse_production_line(line)
        if head in nonterminals:
            raise GrammarError(f"el no terminal {head} aparece en más de una línea")
        nonterminals.append(head)
        productions.extend(Production(head, body) for body in bodies)

    # Validaciones de las suposiciones del enunciado.
    if START not in nonterminals:
        raise GrammarError("el símbolo inicial S no tiene producciones")
    for production in productions:
        for symbol in production.body:
            if is_nonterminal(symbol) and symbol not in nonterminals:
                raise GrammarError(f"el no terminal {symbol} se usa pero no tiene producciones")

    return Grammar(productions, nonterminals)


def grammar_from_text(text):
    """Lee una gramática desde un texto (útil para el ítem 3 y para las pruebas)."""
    lines = iter(text.strip("\n").splitlines())
    return read_grammar(lambda: next(lines, None))
