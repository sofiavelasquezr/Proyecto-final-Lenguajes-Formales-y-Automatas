"""
Pruebas automáticas del proyecto.

Ejecutar desde la carpeta raíz de la entrega:
    python3 -m unittest discover -s tests -v
"""

import itertools
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS = os.path.join(ROOT, "tests", "inputs")
sys.path.insert(0, ROOT)

from parsing.grammar import GrammarError, grammar_from_text, EPSILON, END   # noqa: E402
from parsing.first_follow import compute_first, compute_follow           # noqa: E402
from parsing.ll1 import LL1Parser                                         # noqa: E402
from parsing.slr1 import SLR1Parser                                       # noqa: E402
from sdd.evaluator import (SDD, Attribute, Rule, SYN, INH, CircularSDDError,  # noqa: E402
                           evaluate, validate_sdd, classify_sdd)
from sdd.nested_list_sdd import GRAMMAR_TEXT, build_sdd, build_circular_sdd  # noqa: E402


def run_program(script, input_file, *args):
    """Ejecuta un programa del proyecto con un archivo como entrada estándar."""
    with open(os.path.join(INPUTS, input_file)) as stdin:
        result = subprocess.run([sys.executable, os.path.join(ROOT, script), *args],
                                stdin=stdin, capture_output=True, text=True, cwd=ROOT,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return result.stdout


def build(text):
    grammar = grammar_from_text(text)
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    return grammar, first, follow, LL1Parser(grammar, first, follow), SLR1Parser(grammar, first, follow)


def productions_of(tree):
    """Lista de producciones del árbol en preorden (para comparar árboles)."""
    if tree.production is None:
        return []
    result = [str(tree.production)]
    for child in tree.children:
        result += productions_of(child)
    return result


class TestStatementExamples(unittest.TestCase):
    """Los tres ejemplos de la sección 5 del enunciado, con la salida exacta."""

    def test_example_1(self):
        self.assertEqual(run_program("main.py", "example1.txt"),
                         "Grammar is SLR(1).\nyes\nyes\nno\n")

    def test_example_2(self):
        prompt = "Select a parser (T: for LL(1), B: for SLR(1), Q: quit):\n"
        self.assertEqual(run_program("main.py", "example2.txt"),
                         prompt + "yes\nyes\nno\n" + prompt)

    def test_example_3(self):
        self.assertEqual(run_program("main.py", "example3.txt"),
                         "Grammar is neither LL(1) nor SLR(1).\n")

    def test_sets_option(self):
        output = run_program("main.py", "example2.txt", "--sets").splitlines()
        self.assertEqual(output[:6], [
            "First(A) = {a, d}", "First(B) = {b, e}", "First(S) = {a, d}",
            "Follow(A) = {b, $}", "Follow(B) = {c, $}", "Follow(S) = {$}"])

    def test_ll1_but_not_slr1(self):
        self.assertEqual(run_program("main.py", "ll1_not_slr1.txt"),
                         "Grammar is LL(1).\nyes\nyes\nno\n")

    def test_neither(self):
        self.assertEqual(run_program("main.py", "neither_lr.txt"),
                         "Grammar is neither LL(1) nor SLR(1).\n")


class TestFirstFollow(unittest.TestCase):

    def test_book_example_4_30(self):
        # Gramática 4.28 del libro con E' -> A, T' -> B, id -> i.
        grammar, first, follow, _, _ = build(
            "5\nS -> TA\nA -> +TA e\nT -> FB\nB -> *FB e\nF -> (S) i")
        self.assertEqual(first["S"], {"(", "i"})
        self.assertEqual(first["A"], {"+", EPSILON})
        self.assertEqual(first["B"], {"*", EPSILON})
        self.assertEqual(follow["S"], {")", END})
        self.assertEqual(follow["A"], {")", END})
        self.assertEqual(follow["T"], {"+", ")", END})
        self.assertEqual(follow["B"], {"+", ")", END})
        self.assertEqual(follow["F"], {"+", "*", ")", END})

    def test_nullable_chain(self):
        _, first, follow, _, _ = build("3\nS -> ABc\nA -> a e\nB -> b e")
        self.assertEqual(first["S"], {"a", "b", "c"})
        self.assertEqual(follow["A"], {"b", "c"})


class TestParsers(unittest.TestCase):

    def test_book_slr_table_fig_4_37(self):
        _, _, _, _, slr = build("3\nS -> S+T T\nT -> T*F F\nF -> (S) i")
        self.assertTrue(slr.is_slr1)
        expected = {(0, "i"): "s5", (0, "("): "s4", (1, "+"): "s6", (1, "$"): "acc",
                    (2, "+"): "r2", (2, "*"): "s7", (5, ")"): "r6", (8, ")"): "s11",
                    (9, "*"): "s7", (11, "$"): "r5"}
        for cell, text in expected.items():
            self.assertEqual(slr.action_text(slr.action[cell][0]), text, cell)
        self.assertEqual(slr.goto_table[(0, "S")], 1)
        self.assertEqual(slr.goto_table[(7, "F")], 10)
        self.assertEqual(len(slr.states), 12)

    def test_parsers_agree_with_the_language(self):
        # L = { a^n d b^m c^m : n, m >= 0 } para la gramática del ejemplo 2.
        _, _, _, ll, slr = build("3\nS -> AB\nA -> aA d\nB -> bBc e")

        def in_language(w):
            n = len(w) - len(w.lstrip("a"))
            rest = w[n:]
            if not rest.startswith("d"):
                return False
            rest = rest[1:]
            m = len(rest) // 2
            return rest == "b" * m + "c" * m

        for length in range(7):
            for letters in itertools.product("abcd", repeat=length):
                w = "".join(letters)
                expected = in_language(w)
                ll_tree, slr_tree = ll.parse(list(w)), slr.parse(list(w))
                self.assertEqual(ll_tree is not None, expected, w)
                self.assertEqual(slr_tree is not None, expected, w)
                if expected:  # los dos parsers construyen el mismo árbol
                    self.assertEqual(productions_of(ll_tree), productions_of(slr_tree))

    def test_empty_string_and_unknown_symbols(self):
        _, _, _, ll, slr = build("1\nS -> aS e")
        for parser in (ll, slr):
            self.assertIsNotNone(parser.parse([]))          # la cadena 'e'
            self.assertIsNotNone(parser.parse(list("aaa")))
            self.assertIsNone(parser.parse(list("ab")))     # 'b' no es terminal

    def test_left_recursion_is_not_ll1(self):
        _, _, _, ll, _ = build("1\nS -> Sa b")
        self.assertFalse(ll.is_ll1)
        self.assertTrue(ll.table_conflicts())

    def test_reduce_reduce_conflict(self):
        _, _, _, ll, slr = build("3\nS -> AaAb BbBa\nA -> e\nB -> e")
        self.assertTrue(ll.is_ll1)
        self.assertFalse(slr.is_slr1)
        self.assertEqual({slr.action_text(a) for a in slr.conflicts[(0, "a")]}, {"r3", "r4"})

    def test_invalid_grammars(self):
        for text in ("1\nS -> aeb", "1\nA -> a", "2\nS -> A\nS -> b", "1\nS -> aB", "x"):
            with self.assertRaises(GrammarError):
                grammar_from_text(text)


class TestSDD(unittest.TestCase):

    def setUp(self):
        self.grammar, _, _, self.ll, self.slr = build(GRAMMAR_TEXT)

    def value(self, text, parser=None, sdd=None):
        tree = (parser or self.ll).parse(list(text))
        if tree is None:
            return None
        evaluate(tree, sdd or build_sdd())
        return tree.attrs["v"]

    def test_grammar_is_ll1_and_slr1(self):
        self.assertTrue(self.ll.is_ll1)
        self.assertTrue(self.slr.is_slr1)

    def test_values(self):
        cases = {"[]": 0, "[5]": 5, "[1,[2,3]]": 11, "[[[[5]]]]": 20, "[7,0,[1,[2]],9]": 24}
        for text, expected in cases.items():
            self.assertEqual(self.value(text), expected, text)
            self.assertEqual(self.value(text, self.slr), expected, text)

    def test_strings_not_in_language(self):
        for text in ("[1,]", "[12]", "", "[[]", "1"):
            self.assertIsNone(self.value(text), text)

    def test_sdd_is_well_defined_and_l_attributed(self):
        self.assertEqual(validate_sdd(self.grammar, build_sdd()), [])
        is_s, is_l, _ = classify_sdd(self.grammar, build_sdd())
        self.assertFalse(is_s)
        self.assertTrue(is_l)

    def test_circular_variant(self):
        self.assertEqual(self.value("[]", sdd=build_circular_sdd()), 0)   # este árbol no tiene ciclo
        with self.assertRaises(CircularSDDError):
            self.value("[1]", sdd=build_circular_sdd())

    def test_output_of_the_program(self):
        output = run_program("sdd_main.py", "sdd_strings.txt")
        self.assertIn("Result: S.v = 11", output)
        self.assertIn("Result: S.v = 24", output)
        self.assertTrue(output.rstrip().endswith("no"))
        circular = run_program("sdd_main.py", "sdd_circular.txt", "--circular")
        self.assertIn("the SDD is circular", circular)

    def test_evaluator_is_generic(self):
        # El ejemplo ilustrativo del enunciado (profundidad máxima de paréntesis),
        # escrito solo como datos: el mismo evaluador funciona sin cambios.
        grammar, _, _, ll, _ = build("2\nS -> P\nP -> (P)P e")
        sdd = SDD(
            {"S": {"m": Attribute(SYN, "int", "")},
             "P": {"d": Attribute(INH, "int", ""), "m": Attribute(SYN, "int", "")}},
            {"S -> P": [Rule((1, "d"), (), lambda: 0, "P.d = 0"),
                        Rule((0, "m"), ((1, "m"),), lambda m: m, "S.m = P.m")],
             "P -> (P)P": [Rule((2, "d"), ((0, "d"),), lambda d: d + 1, "P1.d = P.d + 1"),
                           Rule((4, "d"), ((0, "d"),), lambda d: d, "P2.d = P.d"),
                           Rule((0, "m"), ((2, "m"), (4, "m")), max, "P.m = max(P1.m, P2.m)")],
             "P -> e": [Rule((0, "m"), ((0, "d"),), lambda d: d, "P.m = P.d")]},
            "m")
        self.assertEqual(validate_sdd(grammar, sdd), [])
        tree = ll.parse(list("(())()"))
        evaluate(tree, sdd)
        self.assertEqual(tree.attrs["m"], 2)


if __name__ == "__main__":
    unittest.main()
