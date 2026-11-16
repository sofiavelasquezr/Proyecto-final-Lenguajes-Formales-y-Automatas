# Formal Languages Project: FIRST/FOLLOW, LL(1), SLR(1) and SDD evaluation

## Group members

- `<Full name 1>`
- `<Full name 2>`
- `<Full name 3>`

## Environment

| Item | Version |
|---|---|
| Operating system | macOS 26.6.2 (Darwin 25.6.0) |
| Programming language | Python 3.15.1 (any Python 3.8 or newer works) |
| Libraries | Only the Python standard library (`argparse`, `collections`, `dataclasses`, `itertools`, `subprocess`, `unittest`). No parser generators or parsing libraries. |

There is nothing to build or install: the programs are run directly with Python. They were tested with Python 3.9, 3.11, 3.12, 3.14 and 3.15.

### Running on Windows

- Use `py` (or `python`) instead of `python3` in every command below.
- Input redirection with `<` works in the Command Prompt (`cmd`), but not in PowerShell. In PowerShell, use one of these two forms instead:

  ```powershell
  Get-Content tests\inputs\example1.txt | py main.py
  ```

  ```powershell
  cmd /c "py main.py < tests\inputs\example1.txt"
  ```

- Output is always written in UTF-8, so characters such as `ε` print correctly even when the output is redirected to a file.

## Project structure

```
main.py                    Items 1 and 2: command-line program (Section 2.2 of the statement)
sdd_main.py                Item 3: SDD evaluation program
parsing/
    grammar.py             reading the grammar (format of Section 2.2)
    first_follow.py        FIRST and FOLLOW sets (book, Section 4.4.2)
    ll1.py                 LL(1) test, predictive table (Alg. 4.31) and parser (Alg. 4.34)
    slr1.py                LR(0) items, CLOSURE/GOTO, SLR table (Alg. 4.46) and LR parser (Alg. 4.44)
    parse_tree.py          parse-tree nodes
sdd/
    evaluator.py           generic SDD evaluator: dependency graph and topological order (Sections 5.1-5.2)
    nested_list_sdd.py     our SDD (data only)
tests/
    test_project.py        automated tests
    inputs/                example inputs
```

## Items 1 and 2: `main.py`

Run it from this folder. The program reads the grammar and then the strings from the standard input.

```bash
python3 main.py < tests/inputs/example1.txt
```

You can also type the input by hand:

```bash
python3 main.py
```

```
3
S -> AB
A -> aA d
B -> bBc e
```

The program then follows the four cases of Section 2.2.2 of the statement:

- If the grammar is both LL(1) and SLR(1), it asks `Select a parser (T: for LL(1), B: for SLR(1), Q: quit):`.
- If it is only one of them, it prints `Grammar is LL(1).` or `Grammar is SLR(1).`.
- If it is neither, it prints `Grammar is neither LL(1) nor SLR(1).` and ends.

How strings are entered:

- Strings are read one per line, and an empty line ends them.
- The empty string is written `e`.
- For every string the program prints `yes` or `no`.

Options:

| Option | Meaning |
|---|---|
| `--sets` | Prints `First(A) = {...}` and `Follow(A) = {...}` for every nonterminal (alphabetical order), then continues normally. Required by the statement. |
| `--table` | Extra: prints the LL(1) table and, if the grammar is not LL(1), which LL(1) condition fails. |
| `--automaton` | Extra: prints the augmented grammar, the canonical LR(0) collection, the SLR(1) table and its conflicts. |
| `--trace` | Extra: prints every parse step by step, in the format of the book's Figs. 4.21 and 4.38. |

Without the extra options, the output is exactly the one in the statement.

Example:

```bash
python3 main.py --sets --table --automaton --trace < tests/inputs/example2.txt
```

## Item 3: `sdd_main.py`

**Our SDD** works on nested lists of digits, such as `[1,[2,3]]`. It computes the depth-weighted sum: each digit is multiplied by the depth of the list that contains it, so `[1,[2,3]]` gives 1·1 + 2·2 + 3·2 = 11.

**Grammar and SDD:** both are in `sdd/nested_list_sdd.py`.

- The grammar is LL(1) and SLR(1).
- The SDD is stored as data: attribute table and semantic rules.
- The evaluator in `sdd/evaluator.py` does not depend on this particular SDD.

Run it like this:

```bash
python3 sdd_main.py < tests/inputs/sdd_strings.txt
```

Strings are read one per line until an empty line. For each string the program prints:

- `no` if the string is not in the language;
- otherwise, the annotated parse tree (one node per line, indented by depth), the evaluation order (a topological order of the dependency graph) and the value of `S.v`.

Options:

| Option | Meaning |
|---|---|
| `--parser LL` / `--parser SLR` | Parser from Item 2 used to build the tree (default `LL`). |
| `--rules` | Prints the grammar, the attribute table, the semantic rules and the S-/L-attributed classification. |
| `--graph` | Also prints the vertices and edges of the dependency graph. |
| `--circular` | Uses a circular variant of the SDD (rule `L.d = L.s` in `S -> L`) to show that circularity is detected (Step 6). |

Examples:

```bash
python3 sdd_main.py --rules --graph < tests/inputs/sdd_strings.txt
```

```bash
python3 sdd_main.py --circular < tests/inputs/sdd_circular.txt
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests check:

- the exact output of the three examples in the statement;
- the `--sets` format;
- FIRST/FOLLOW against Example 4.30 of the book;
- the SLR table against Fig. 4.37 of the book;
- that both parsers agree with the language on every string up to length 6;
- the values of our SDD, and that circularity is detected;
- that the evaluator works unchanged with a different SDD.

Python creates `__pycache__` folders when the programs run. Delete them before submitting:

```bash
find . -name __pycache__ -exec rm -rf {} +
```

## Use of generative AI

Claude (Anthropic), through Claude Code, was used to:

- write and explain the code;
- write the test suite;
- prepare a study guide of Sections 4.4–4.6 and 5.1–5.2 of the book.

The course professor authorized this use. All group members reviewed the code, traced the algorithms by hand on the examples, and are able to explain and modify every part of it.
