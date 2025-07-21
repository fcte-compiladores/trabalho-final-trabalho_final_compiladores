import builtins
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from arnoldc.arnoldc_ast import Program

from .ctx import Ctx

if TYPE_CHECKING:
    from .arnoldc_ast import Stmt, Value
    from .errors import ForceReturn

__all__ = [
    "print_arnoldc", 
    "is_arnoldc_true", 
    "ArnoldCError", 
    "ArnoldCMethod", 
]


@dataclass(frozen=True)
class ArnoldCMethod: 
    name: str
    params: list[str]
    body: list["Stmt"]
    ctx: Ctx
    returns_value: bool = False

    def __call__(self, *args: "Value") -> Optional["Value"]:
        if len(args) != len(self.params):
            raise ArnoldCError(
                f"Número incorreto de argumentos para o método '{self.name}'. "
                f"Esperava {len(self.params)}, mas recebeu {len(args)}."
            )

        exec_ctx = self.ctx.push({})

        for param_name, arg_value in zip(self.params, args):
            exec_ctx.var_def(param_name, arg_value)

        try:
            for stmt in self.body:
                stmt.eval(exec_ctx)
        except ForceReturn as ex:
            if self.returns_value and ex.value is None:
                raise ArnoldCError(f"Método '{self.name}' deve retornar um valor explícito.")
            if not self.returns_value and ex.value is not None:
                raise ArnoldCError(f"Método void '{self.name}' não pode retornar um valor.")
            return ex.value 

        if self.returns_value:
            raise ArnoldCError(f"Método '{self.name}' que retorna valor não possui 'I'LL BE BACK' explícito.")

        return None

    def __str__(self) -> str:
        return f"<method {self.name}>"

    def __eq__(self, other: object) -> bool:
        return self is other


class ArnoldCError(Exception):
    """Exceção para erros de tempo de execução em ArnoldC."""
    pass


# --- FUNÇÕES AUXILIARES ---

def print_arnoldc(value: "Value") -> None:
    builtins.print(value)


def evaluate(program: "Program", ctx: Ctx) -> None:
    for stmt in program.stmts:
        stmt.eval(ctx)