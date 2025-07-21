"""
Esse módulo usa a biblioteca `argparse` para criar uma interface de linha de comando
(CLI) para o compilador de Lox.

Ele permite que o usuário execute o compilador com diferentes opções, como especificar
o arquivo de entrada, ativar o modo para imprimir as árvores
sintáticas, lexer, etc.

Argparse talvez não seja a melhor opção para criar uma CLI, mas é uma biblioteca
padrão do Python e não requer instalação de dependências externas.
"""

import argparse

from lark import Token


from . import arnoldc_eval
from .ctx import Ctx
from .parser import lex, parse, parse_cst, parse_expr
from .runtime import print_arnoldc


def make_argparser():
    parser = argparse.ArgumentParser(description="Compilador ArnoldC") 
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    run_parser = subparsers.add_parser("run", help="Executa um arquivo ArnoldC")
    run_parser.add_argument(
        "file",
        help="Arquivo de entrada",
    )
    run_parser.add_argument(
        "-t",
        "--ast",
        action="store_true",
        help="Imprime a árvore sintática.",
    )
    run_parser.add_argument(
        "-l",
        "--lex",
        action="store_true",
        help="Imprime o lexer.",
    )
    run_parser.add_argument(
        "-c",
        "--cst",
        action="store_true",
        help="Imprime a árvore sintática concreta produzida pelo Lark.",
    )
    run_parser.add_argument(
        "-p",
        "--pm",
        action="store_true",
        help="Habilita o post-mortem debugger em caso de falha.",
    )
    run_parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        help="Mostra o código fonte do arquivo de entrada.",
    )

    return parser


def main():
    """
    Função principal que cria a interface de linha de comando (CLI) para o compilador ArnoldC.
    """
    parser = make_argparser()
    args = parser.parse_args()

    if args.command == "run":
        try:
            with open(args.file, "r") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"Arquivo {args.file} não encontrado.")
            exit(1)

        if args.show:
            line_len = 60
            head = f"=== {args.file} ="
            head += "=" * (line_len - len(head))
            print_color(head, "blue")
            print()
            print_color(source, "yellow")
            print_color("=" * line_len, "blue")
            print()

        if not args.ast and not args.cst and not args.lex:
            try:
                ast = parse(source) 
                arnoldc_eval(ast, Ctx.from_dict({}))
            except Exception as e:
                on_error(e, args.pm)

        else:
            debug_source(source, args)
    else:
        parser.print_help()
        
def print_color(str: str, color: str):
    try:
        from rich import print

        print(f"[{color}]{str}[/{color}]")
    except ImportError:
        print(str)
        
def on_error(exception: Exception, pm: bool):
    if not pm:
        raise exception

    from ipdb import post_mortem  # type: ignore[import-untyped]

    post_mortem(exception.__traceback__)

def debug_source(source: str, args):
    """
    Mostra informações de depuração sobre o código ArnoldC passado como argumento.
    """
    if args.ast:
        ast = parse(source)
        for node in ast.lark_descendents():
            if isinstance(node, Token):
                descr = repr(node)
                tail = f"Implemente o método {node.type} no ArnoldCTransformer para lidar com estes terminais."
            else:
                descr = node.data
                tail = f"Implemente o método {node.data} no ArnoldCTransformer para lidar com regras do tipo {node.data}."
            msg = f"Atenção: A árvore sintática contém nós Lark ({descr}).\n"
            msg += tail
            print(msg)

        print(ast.pretty())

    if args.cst:
        cst = parse_cst(source)
        print(cst.pretty())

    if args.lex:
        for token in lex(source):
            print(f"{token.type}: {token.value}")