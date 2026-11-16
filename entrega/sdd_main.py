"""
Ítem 3 del proyecto: evaluación de nuestra SDD sobre el árbol de análisis.

Lee cadenas (una por línea, hasta una línea vacía). Para cada una:
    * si no pertenece al lenguaje, imprime  no ;
    * si pertenece, imprime el árbol anotado, el orden de evaluación y el
      valor del atributo principal de S.

Uso:
    python3 sdd_main.py [--parser LL|SLR] [--rules] [--graph] [--circular] < cadenas.txt

    --parser    parser del ítem 2 que se usa (por defecto LL; la gramática es
                LL(1) y SLR(1)).
    --rules     imprime la gramática, la tabla de atributos, las reglas y la
                clasificación S/L-atribuida.
    --graph     imprime también los vértices y las aristas del grafo de dependencias.
    --circular  usa la variante circular de la SDD (paso 6 del enunciado).
"""

import argparse
import sys

from parsing.grammar import grammar_from_text
from parsing.first_follow import compute_first, compute_follow
from parsing.ll1 import LL1Parser, format_grid
from parsing.slr1 import SLR1Parser
from parsing.parse_tree import format_tree
from sdd.evaluator import (CircularSDDError, SDDError, classify_sdd, evaluate,
                           validate_sdd)
from sdd.nested_list_sdd import GRAMMAR_TEXT, build_circular_sdd, build_sdd
from main import make_line_reader, string_to_tokens, use_utf8_output


def print_rules(grammar, sdd):
    print("Grammar:")
    for line in str(grammar).splitlines():
        print("  " + line)
    print("Attributes:")
    rows = [["SYMBOL", "ATTRIBUTE", "KIND", "TYPE", "MEANING"]]
    for symbol, attributes in sdd.attributes.items():
        for name, attribute in attributes.items():
            rows.append([symbol, name, attribute.kind, attribute.type, attribute.meaning])
    rows.append(["terminals", "lexval", "synthesized", "char", "the character itself (given)"])
    for line in format_grid(rows):
        print("  " + line)
    print("Semantic rules:")
    rows = [["PRODUCTION", "SEMANTIC RULES"]]
    for production in grammar.productions:
        rows.append([str(production), "; ".join(rule.text for rule in sdd.rules_for(production))])
    for line in format_grid(rows):
        print("  " + line)
    is_s, is_l, notes = classify_sdd(grammar, sdd)
    print(f"S-attributed: {'yes' if is_s else 'no'}")
    print(f"L-attributed: {'yes' if is_l else 'no' if is_l is False else 'only if condition (c) holds'}")
    for note in notes:
        print("  " + note)
    print()


def print_graph(graph):
    print("Dependency graph:")
    for v in range(len(graph.vertices)):
        successors = ", ".join(graph.label(w) for w in graph.edges[v])
        print(f"  {graph.label(v)} -> {successors if successors else '(no outgoing edges)'}")


def main(argv=None):
    arg_parser = argparse.ArgumentParser(description="Evaluate our SDD with a dependency graph.")
    arg_parser.add_argument("--parser", choices=["LL", "SLR"], default="LL")
    arg_parser.add_argument("--rules", action="store_true")
    arg_parser.add_argument("--graph", action="store_true")
    arg_parser.add_argument("--circular", action="store_true")
    args = arg_parser.parse_args(argv)
    use_utf8_output()

    grammar = grammar_from_text(GRAMMAR_TEXT)
    sdd = build_circular_sdd() if args.circular else build_sdd()

    problems = validate_sdd(grammar, sdd)
    if problems:
        print("The SDD is not well defined:")
        for problem in problems:
            print("  " + problem)
        return 1
    if args.rules:
        print_rules(grammar, sdd)

    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    parser = LL1Parser(grammar, first, follow) if args.parser == "LL" else SLR1Parser(grammar, first, follow)
    if not (parser.is_ll1 if args.parser == "LL" else parser.is_slr1):
        print(f"The grammar of the SDD is not {parser.name}.")
        return 1

    read_line = make_line_reader(sys.stdin)
    while True:
        line = read_line()
        if line is None or line.strip() == "":
            return 0
        tree = parser.parse(string_to_tokens(line.strip()))
        if tree is None:
            print("no")
            continue
        try:
            graph, order, computed = evaluate(tree, sdd)
        except CircularSDDError as error:
            print(f"Input {line.strip()!r}: the SDD is circular, so it cannot be evaluated.")
            print("Cycle found in the dependency graph: " + " -> ".join(error.cycle))
            return 1
        except SDDError as error:
            print(f"Error: {error}")
            return 1

        print(f"Input: {line.strip()}")
        print("Annotated parse tree:")
        for tree_line in format_tree(tree):
            print("  " + tree_line)
        if args.graph:
            print_graph(graph)
        print("Evaluation order (topological order of the dependency graph):")
        for step, v in enumerate(computed, start=1):
            node, name = graph.vertices[v]
            print(f"  {step}. {graph.label(v)} = {node.attrs[name]!r}")
        print(f"Result: {tree.symbol}.{sdd.main_attribute} = {tree.attrs[sdd.main_attribute]!r}")
        print()


if __name__ == "__main__":
    sys.exit(main())
