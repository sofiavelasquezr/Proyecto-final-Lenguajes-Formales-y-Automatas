"""
Ítems 1 y 2 del proyecto.

Lee una gramática (formato de la sección 2.2 del enunciado), decide si es
LL(1) y si es SLR(1), y analiza cadenas según los cuatro casos de 2.2.2.

Uso:
    python3 main.py [--sets] [--table] [--automaton] [--trace] < entrada.txt

    --sets       imprime FIRST y FOLLOW (requerido por el enunciado).
    --table      imprime la tabla LL(1) y por qué la gramática es o no LL(1).
    --automaton  imprime el autómata LR(0) y la tabla SLR(1) (con conflictos).
    --trace      imprime el análisis paso a paso de cada cadena.
Las tres últimas opciones son extra (para el informe); sin ellas la salida es
exactamente la del enunciado.
"""

import argparse
import sys

from parsing.grammar import GrammarError, read_grammar
from parsing.first_follow import compute_first, compute_follow, sets_report
from parsing.ll1 import LL1Parser, format_grid
from parsing.slr1 import SLR1Parser

PROMPT = "Select a parser (T: for LL(1), B: for SLR(1), Q: quit):"


def use_utf8_output():
    """
    Fuerza UTF-8 en la salida. En Windows, cuando la salida se redirige a un
    archivo o a otro programa, Python usa por defecto cp1252, que no tiene
    caracteres como 'ε' y haría fallar el programa al imprimir el árbol.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def make_line_reader(stream):
    """Devuelve una función que lee una línea (sin el salto) o None al final."""
    def read_line():
        line = stream.readline()
        if line == "":
            return None                 # fin de la entrada (EOF)
        return line.rstrip("\r\n")
    return read_line


def string_to_tokens(line):
    """La cadena vacía se escribe 'e'; cualquier otra es una lista de caracteres."""
    return [] if line == "e" else list(line)


def parse_strings(parser, read_line, show_trace):
    """Lee cadenas, una por línea, hasta una línea vacía; imprime yes o no."""
    while True:
        line = read_line()
        if line is None or line.strip() == "":
            return
        trace = [] if show_trace else None
        tree = parser.parse(string_to_tokens(line.strip()), trace)
        if show_trace:
            print_trace(parser, line.strip(), trace)
        print("yes" if tree is not None else "no", flush=True)


def print_trace(parser, text, trace):
    if parser.name == "LL(1)":
        header = ["MATCHED", "STACK", "INPUT", "ACTION"]
    else:
        header = ["STACK", "SYMBOLS", "INPUT", "ACTION"]
    print(f"{parser.name} parse of {text!r}:")
    for line in format_grid([header] + [list(row) for row in trace]):
        print("  " + line)


def print_extras(args, ll1, slr1):
    """Información adicional para el informe (opciones --table y --automaton)."""
    if args.table:
        print("LL(1) parsing table:")
        for line in ll1.table_lines():
            print("  " + line)
        if ll1.is_ll1:
            print("The grammar satisfies the LL(1) conditions of Section 4.4.3.")
        else:
            print("LL(1) conditions violated:")
            for violation in ll1.violations:
                print("  " + violation)
    if args.automaton:
        for line in slr1.automaton_lines():
            print(line)
        print("SLR(1) parsing table:")
        for line in slr1.table_lines():
            print("  " + line)
        if slr1.conflicts:
            print("SLR(1) conflicts:")
            for (state, terminal), actions in sorted(slr1.conflicts.items()):
                texts = ", ".join(slr1.action_text(act) for act in actions)
                print(f"  ACTION[{state}, {terminal}] = {texts}")


def main(argv=None):
    arg_parser = argparse.ArgumentParser(description="FIRST/FOLLOW, LL(1) and SLR(1) parsers.")
    arg_parser.add_argument("--sets", action="store_true", help="print FIRST and FOLLOW sets")
    arg_parser.add_argument("--table", action="store_true", help="print the LL(1) table")
    arg_parser.add_argument("--automaton", action="store_true",
                            help="print the LR(0) automaton and the SLR(1) table")
    arg_parser.add_argument("--trace", action="store_true", help="print every parse step by step")
    args = arg_parser.parse_args(argv)
    use_utf8_output()

    read_line = make_line_reader(sys.stdin)
    try:
        grammar = read_grammar(read_line)
    except GrammarError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    # Ítem 1: FIRST y FOLLOW.
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    if args.sets:
        for line in sets_report(grammar, first, follow):
            print(line)

    # Ítem 2: se construyen ambos parsers y se prueba cada condición.
    ll1 = LL1Parser(grammar, first, follow)
    slr1 = SLR1Parser(grammar, first, follow)
    print_extras(args, ll1, slr1)

    if ll1.is_ll1 and slr1.is_slr1:                         # caso 1
        while True:
            print(PROMPT, flush=True)
            line = read_line()
            if line is None:
                break
            choice = line.strip().upper()
            if choice == "Q":
                break
            if choice == "T":
                parse_strings(ll1, read_line, args.trace)
            elif choice == "B":
                parse_strings(slr1, read_line, args.trace)
            # cualquier otra respuesta: se vuelve a preguntar
    elif ll1.is_ll1:                                        # caso 2
        print("Grammar is LL(1).", flush=True)
        parse_strings(ll1, read_line, args.trace)
    elif slr1.is_slr1:                                      # caso 3
        print("Grammar is SLR(1).", flush=True)
        parse_strings(slr1, read_line, args.trace)
    else:                                                   # caso 4
        print("Grammar is neither LL(1) nor SLR(1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
