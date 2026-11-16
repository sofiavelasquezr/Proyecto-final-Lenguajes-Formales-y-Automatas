"""
Ítem 1: conjuntos FIRST y FOLLOW (Aho et al., §4.4.2).

Las dos funciones aplican las reglas del libro "hasta que no se pueda agregar
nada más a ningún conjunto" (iteración de punto fijo).
"""

from .grammar import EPSILON, END, is_nonterminal


def first_of_symbol(symbol, first):
    """FIRST(X) para un símbolo. Regla 1: si X es terminal, FIRST(X) = {X}."""
    if is_nonterminal(symbol):
        return first[symbol]
    return {symbol}


def first_of_string(symbols, first):
    """
    FIRST(X1 X2 ... Xn) para una cadena de símbolos (§4.4.2):
      - se agregan los símbolos distintos de ε de FIRST(X1);
      - si ε ∈ FIRST(X1), también los de FIRST(X2), y así sucesivamente;
      - ε se agrega solo si ε ∈ FIRST(Xi) para TODO i.
    Para la cadena vacía (cuerpo de A -> ε) el ciclo no se ejecuta y el
    resultado es {ε}.
    """
    result = set()
    for symbol in symbols:
        first_x = first_of_symbol(symbol, first)
        result |= first_x - {EPSILON}
        if EPSILON not in first_x:
            return result          # Xi no deriva ε: los siguientes no aportan
    result.add(EPSILON)            # todos los Xi derivan ε (o la cadena es vacía)
    return result


def compute_first(grammar):
    """
    FIRST(A) para todo no terminal A.
      Regla 2: si A -> Y1...Yk, se agrega FIRST(Y1...Yk) a FIRST(A).
      Regla 3: si A -> ε, se agrega ε (es el caso k = 0 de first_of_string).
    """
    first = {A: set() for A in grammar.nonterminals}
    changed = True
    while changed:                                   # hasta un punto fijo
        changed = False
        for production in grammar.productions:
            new_symbols = first_of_string(production.body, first)
            if not new_symbols <= first[production.head]:
                first[production.head] |= new_symbols
                changed = True
    return first


def compute_follow(grammar, first):
    """
    FOLLOW(A) para todo no terminal A:
      Regla 1: $ ∈ FOLLOW(S).
      Regla 2: si A -> αBβ, todo FIRST(β) excepto ε está en FOLLOW(B).
      Regla 3: si A -> αB, o A -> αBβ con ε ∈ FIRST(β), todo FOLLOW(A)
               está en FOLLOW(B).
    """
    follow = {A: set() for A in grammar.nonterminals}
    follow[grammar.start].add(END)                   # regla 1
    changed = True
    while changed:                                   # hasta un punto fijo
        changed = False
        for production in grammar.productions:
            A = production.head
            for i, B in enumerate(production.body):  # cada aparición de B
                if not is_nonterminal(B):
                    continue
                beta = production.body[i + 1:]
                first_beta = first_of_string(beta, first)
                new_symbols = first_beta - {EPSILON}            # regla 2
                if EPSILON in first_beta:                       # regla 3 (β vacía
                    new_symbols |= follow[A]                    #  o anulable)
                if not new_symbols <= follow[B]:
                    follow[B] |= new_symbols
                    changed = True
    return follow


def format_set(symbols):
    """
    Formato de salida del enunciado: terminales en orden ASCII, luego 'e'
    (si está ε) y luego '$' (si está). Ejemplo: {a, d}  o  {b, $}.
    """
    terminals = sorted(s for s in symbols if s not in (EPSILON, END))
    if EPSILON in symbols:
        terminals.append("e")
    if END in symbols:
        terminals.append("$")
    return "{" + ", ".join(terminals) + "}"


def sets_report(grammar, first, follow):
    """Líneas que imprime la opción --sets (no terminales en orden alfabético)."""
    lines = [f"First({A}) = {format_set(first[A])}" for A in sorted(grammar.nonterminals)]
    lines += [f"Follow({A}) = {format_set(follow[A])}" for A in sorted(grammar.nonterminals)]
    return lines
