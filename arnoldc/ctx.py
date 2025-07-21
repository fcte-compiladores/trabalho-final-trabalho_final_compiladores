import math
import time
from dataclasses import field
from typing import TYPE_CHECKING, Iterator, Optional, TypeVar

from dataclasses import dataclass

if TYPE_CHECKING:
    from .arnoldc_ast import Value

T = TypeVar("T")
ScopeDict = dict[str, "Value"]


@dataclass
class Ctx:
    """
    Contexto de execução. Por enquanto é só um dicionário que armazena nomes
    das variáveis e seus respectivos valores.
    """

    scope: ScopeDict = field(default_factory=dict)
    parent: Optional["Ctx"] = None

    @classmethod
    def from_dict(cls, env: ScopeDict) -> "Ctx":
        """
        Cria um novo contexto a partir de um dicionário.
        O contexto inicial criado por esta função será o escopo global, sem pai.
        """
        return cls(env, None) 

    def __getitem__(self, name: str) -> "Value":
        """
        Obtém o valor de uma variável pelo nome.
        """
        if name in self.scope:
            return self.scope[name]
        elif self.parent is not None:
            return self.parent[name]
        raise KeyError(f"Variable '{name}' not found in context.")

    def __setitem__(self, name: str, value: "Value") -> None:
        """
        Define o valor de uma variável pelo nome.
        """
        if name in self.scope:
            self.scope[name] = value
        elif self.parent is not None:
            self.parent[name] = value
        else:
            raise KeyError(f"Variable '{name}' not found in context.")

    def __contains__(self, name: str) -> bool:
        """
        Verifica se uma variável existe no contexto.
        """
        return name in self.scope or (self.parent is not None and name in self.parent)

    def var_def(self, name: str, value: "Value") -> None:
        """
        Define uma variável no contexto atual.
        Se a variável já existe no escopo atual e não é o escopo global, lança um erro.
        """
        if name in self.scope and not self.is_global():
            raise NameError(f"Variável '{name}' já foi declarada neste escopo.")
        self.scope[name] = value


    def to_dict(self) -> ScopeDict:
        """
        Converte o contexto para um dicionário.
        """
        if self.parent is None:
            return self.scope.copy()
        return {**self.parent.to_dict(), **self.scope}

    def iter_scopes(self, reverse: bool = False) -> Iterator[ScopeDict]:
        """
        Itera sobre os ambientes do contexto, começando pelo mais interno.
        """
        if reverse:
            if self.parent is not None:
                yield from self.parent.iter_scopes(reverse=True)
            yield self.scope
        else:
            yield self.scope
            if self.parent is not None:
                yield from self.parent.iter_scopes()

    def pretty(self) -> str:
        """
        Representação do contexto como string.
        """

        lines: list[str] = []
        for i, scope in enumerate(self.iter_scopes(reverse=True)):
            lines.append(pretty_scope(scope, i))
        return "\n".join(reversed(lines))

    def pop(self) -> tuple[ScopeDict, "Ctx"]:
        """
        Remove o escopo mais interno e retorna o contexto atualizado.
        """
        if self.parent is None:
            raise RuntimeError("Cannot pop the global scope.")
        return self.scope, self.parent

    def push(self, env: ScopeDict) -> "Ctx":
        """
        Empilha um novo escopo no contexto atual.
        """
        return Ctx(env, self)

    def is_global(self) -> bool:
        """
        Verifica se o contexto atual é o escopo global.
        Um contexto é considerado global se não possui um pai.
        """
        return self.parent is None
    
    def assign(self, name, value):
        current_ctx = self
        while current_ctx:
            if name in current_ctx.scope:
                current_ctx.scope[name] = value
                return 
            current_ctx = current_ctx.parent
        
        raise NameError(f"Variável '{name}' não definida.")


def pretty_scope(env: ScopeDict, index: int) -> str:
    """
    Representa um escopo como string.
    """
    if not env:
        return f"{index:>2}: <empty>"
    items = (f"{k} = {v}" for k, v in sorted(env.items()))
    data = "; ".join(items)
    return f"{index:>2}: {data}"