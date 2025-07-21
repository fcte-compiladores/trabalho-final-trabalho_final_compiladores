"""
Carrega os nomes principais do módulo ArnoldC.
"""


from typing import Optional
from .arnoldc_ast import Expr, Stmt, Value, Program 
from .ctx import Ctx
from .errors import SemanticError, ArnoldCError
from .node import Node
from .parser import lex, parse, parse_cst, parse_expr
from .runtime import evaluate as runtime_evaluate

__all__ = [
    "Ctx",
    "arnoldc_eval",
    "Expr",
    "lex",
    "Node",
    "parse_cst",
    "parse",
    "parse_expr",
    "Stmt",
    "SemanticError",
    "ArnoldCError",
]


def arnoldc_eval( 
    src: str | Node, 
    env: Ctx | dict[str, Value] | None = None,
    skip_validation: bool = False,
) -> Optional[Value]: 
    """
    Avalia o código fonte ArnoldC e retorna o valor resultante (se for uma expressão)
    ou executa o programa (se for um conjunto de comandos).

    Args:
        src:
            Código fonte em formato de string ou um nó AST (Program ou Expr).
        env:
            Ambiente onde as variáveis serão avaliadas. Se omitido, um novo
            ambiente vazio será criado. Aceita um dicionário mapeando nomes de
            variáveis para seus valores ou uma instância de `Ctx`.
        skip_validation:
            Se `True`, ignora a validação do código fonte antes da avaliação.
    """
    if env is None:
        env = Ctx.from_dict({})
    elif not isinstance(env, Ctx):
        env = Ctx.from_dict(env)

    ast_node: Node 

    if isinstance(src, str):
        try:
            ast_node = parse_expr(src)
        except Exception: 
            ast_node = parse(src)
    else:
        ast_node = src

    if not skip_validation:
        ast_node.validate_tree()

    try:
        if isinstance(ast_node, Program):
            runtime_evaluate(ast_node, env)
            return None
        else:
            return ast_node.eval(env)
    except (SemanticError, ArnoldCError) as e:
        print(f"Programa terminou com um erro: {e}")
        print("Variáveis:", env)
        raise
    except Exception as e:
        print(f"Programa terminou com um erro inesperado: {e}")
        print("Variáveis:", env)
        raise