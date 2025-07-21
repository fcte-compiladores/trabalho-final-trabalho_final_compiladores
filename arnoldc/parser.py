"""
Define a gramática da Linguagem e funções para realizar a análise sintática,
análise léxica, etc.
"""

from pathlib import Path
from typing import Iterator

from lark import Lark, Token, Tree

from .arnoldc_ast import Expr, Program
from .transformer import ArnoldCTransformer

DIR = Path(__file__).parent
GRAMMAR_PATH = DIR / "grammar.lark"


ast_parser = Lark(
    GRAMMAR_PATH.open(),
    transformer=ArnoldCTransformer(),
    parser="lalr",
    start=["start", "expr"],
)
cst_parser = Lark(
    GRAMMAR_PATH.open(),
    parser="lalr",
    start=["start", "expr"],
)


def parse(src: str):
    with open("arnoldc/grammar.lark", "r") as f:
        grammar = f.read()
    
    ast_parser = Lark(grammar, start="start", parser="lalr", propagate_positions=True)
    
    
    tree = ast_parser.parse(src)
    # --- Mostrando a árvore sintática bruta (Lark Tree) ---
    # print("--- RAW PARSE TREE (Lark Tree) ---")
    # print(tree.pretty()) # This will print a formatted version of the parse tree
    # print("---------------------------------")
   
    tree = ArnoldCTransformer().transform(tree)
    tree.validate_tree()
    return tree


def parse_expr(src: str) -> Expr:
    """
    Função que recebe um código fonte e retorna a árvore sintática
    representando uma expressão.

    """
    tree = ast_parser.parse(src, start="expr")
    assert isinstance(tree, Expr), f"Esperava um Expr, mas recebi {type(tree)}"
    tree.validate_tree()
    tree.desugar_tree()
    return tree


def parse_cst(src: str, expr: bool = False) -> Tree:
    """
    Similar a função `parse`, mas retorna a árvore sintática produzida pelo
    Lark.

    Não é exatamente a árvore concreta, pois o Lark produz algumas
    simplificações, mas é próxima o suficiente.

    Args:
        src (str):
            Código fonte a ser analisado.
        expr (bool):
            Se True, analisa o código como se fosse apenas uma expressão.
    """
    start = "expr" if expr else "start"
    return cst_parser.parse(src, start=start)


def lex(src: str) -> Iterator[Token]:
    """
    Retorna um iterador sobre os tokens do código fonte.
    """
    return ast_parser.lex(src)