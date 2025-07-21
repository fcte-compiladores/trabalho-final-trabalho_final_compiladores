from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Union

from .ctx import Ctx

from .node import Node, Cursor
from .errors import ArnoldCError, SemanticError, ForceReturn


RESERVED_KEYWORDS = {
    "IT'S SHOWTIME", "YOU HAVE BEEN TERMINATED", "HEY CHRISTMAS TREE", "YOU SET US UP",
    "TALK TO THE HAND", "GET TO THE CHOPPER", "HERE IS MY INVITATION", "ENOUGH TALK",
    "GET UP", "GET DOWN", "YOU'RE FIRED", "HE HAD TO SPLIT", "YOU ARE NOT YOU YOU ARE ME", 
    "LET OFF SOME STEAM BENNET", "CONSIDER THAT A DIVORCE", "KNOCK KNOCK",
    "BECAUSE I'M GOING TO SAY PLEASE", "BULLSHIT", "YOU HAVE NO RESPECT FOR LOGIC",
    "STICK AROUND", "CHILL", "LISTEN TO ME VERY CAREFULLY", 
    "I NEED YOUR CLOTHES YOUR BOOTS AND YOUR MOTORCYCLE", "GIVE THESE PEOPLE AIR", "HASTA LA VISTA, BABY", 
    "I'LL BE BACK", "@I LIED", "@NO PROBLEMO", "GET YOUR ASS TO MARS", "DO IT NOW"
}

#
# TIPOS BÁSICOS
#

Value = Union[int, str]

class Expr(Node, ABC):
    """
    Classe base para expressões.
    Em ArnoldC, expressões geralmente resultam em um valor para a 'pilha de avaliação'
    dentro de um bloco de atribuição ou são literais/variáveis.
    """
    pass


class Stmt(Node, ABC):
    """
    Classe base para comandos.
    Comandos em ArnoldC são as frases de ação ou blocos de controle de fluxo.
    """
    pass


@dataclass
class Program(Node):
    """
    Representa um programa ArnoldC completo.
    Contém uma lista de comandos que formam o corpo principal do programa.
    """
    stmts: list[Stmt]

    def eval(self, ctx: Ctx):
        for stmt in self.stmts:
            stmt.eval(ctx)
        return None
    
    def validate_self(self, cursor: Cursor):
        for stmt in self.stmts:
            stmt.validate_self(stmt.cursor(cursor))

#
# EXPRESSÕES
#


@dataclass
class Var(Expr):
    """
    Uma variável no código
    Ex.: myvar
    """
    name: str

    def eval(self, ctx: Ctx):
        return ctx[self.name]


@dataclass
class Literal(Expr):
    """
    Representa valores literais no código: strings, números inteiros.
    @I LIED e @NO PROBLEMO serão tratados como literais numéricos (0 e 1).
    Ex.: "Hello, world!", 42, @I LIED, @NO PROBLEMO
    """
    value: Value

    def eval(self, ctx: Ctx):
        return self.value
    
    def validate_self(self, cursor: 'Cursor'):
        pass
    
@dataclass
class Bool(Expr): 
    value: bool
    
    def eval(self, ctx: Ctx) -> bool:
        return self.value

    def validate_self(self, cursor: 'Cursor'):
        pass


#
# COMANDOS
#

@dataclass
class Print(Stmt):
    """
    Representa uma instrução de impressão.
    Ex.: TALK TO THE HAND "Hello, world!"
    Ex.: TALK TO THE HAND myvar
    """
    target: Union[Literal, Var]
    
    def eval(self, ctx: Ctx):
        from .runtime import print_arnoldc
        value_to_print = self.target.eval(ctx)
        print_arnoldc(value_to_print)

    def validate_self(self, cursor: Cursor):
        self.target.validate_self(self.target.cursor(cursor))
        

@dataclass
class Return(Stmt):
    """
    Representa uma instrução de retorno em métodos.
    Ex.: I'LL BE BACK my_value
    """
    value: Optional[Expr] = None

    def eval(self, ctx: Ctx):
        val = self.value.eval(ctx) if self.value is not None else None
        raise ForceReturn(val)

    def validate_self(self, cursor: Cursor):
        in_method = False
        for ancestor_cursor in cursor.parents():
            if isinstance(ancestor_cursor.node, Method):
                in_method = True
                break
        if not in_method:
            raise SemanticError("Não é possível usar 'I'LL BE BACK' fora de um método.", token="I'LL BE BACK")
        
        if self.value:
            self.value.validate_self(self.value.cursor(cursor))


@dataclass
class VarDef(Stmt):
    """
    Representa uma declaração de variável.
    Ex.: HEY CHRISTMAS TREE myvar YOU SET US UP 42
    """
    name: str
    value: Expr

    def eval(self, ctx: Ctx):
        initial_value = self.value.eval(ctx)
        ctx.var_def(self.name, initial_value)
        
    def validate_self(self, cursor: Cursor):
        if self.name in RESERVED_KEYWORDS:
            raise SemanticError("nome inválido", token=self.name)
        
        for ancestor_cursor in cursor.parents():
            ancestor_node = ancestor_cursor.node
            if isinstance(ancestor_node, Method): 
                param_names = {p for p in ancestor_node.params} 
                if self.name in param_names:
                    raise SemanticError("variável com nome de parâmetro", token=self.name)
                break
        self.value.validate_self(self.value.cursor(cursor))


@dataclass
class If(Stmt):
    """
    Representa uma instrução condicional.
    Ex.: BECAUSE I'M GOING TO SAY PLEASE cond_value [then_stmts] BULLSHIT [else_stmts] YOU HAVE NO RESPECT FOR LOGIC
    """
    cond: Expr
    then_branch: 'StatementBlock'
    else_branch: Optional['StatementBlock'] = None

    def eval(self, ctx: Ctx):
        if is_arnoldc_true(self.cond.eval(ctx)):
            self.then_branch.eval(ctx)
        elif self.else_branch is not None:
            self.else_branch.eval(ctx)

    def validate_self(self, cursor: Cursor):
        self.cond.validate_self(self.cond.cursor(cursor))
        self.then_branch.validate_self(self.then_branch.cursor(cursor))
        if self.else_branch:
            self.else_branch.validate_self(self.else_branch.cursor(cursor))


@dataclass
class While(Stmt):
    """
    Representa um laço de repetição.
    Ex.: STICK AROUND cond_value [body_stmts] CHILL
    """
    cond: Expr
    body: 'StatementBlock'

    def eval(self, ctx: Ctx):
        while is_arnoldc_true(self.cond.eval(ctx)):
            self.body.eval(ctx)

    def validate_self(self, cursor: Cursor):
        self.cond.validate_self(self.cond.cursor(cursor))
        self.body.validate_self(self.body.cursor(cursor))


@dataclass
class StatementBlock(Stmt):
    """
    Representa um bloco de comandos em ArnoldC (qualquer sequência de comandos
    delimitada por frases-chave, não por chaves {}).
    Ex.: o corpo de um método, o corpo de um if/else, o corpo de um loop.
    """
    stmts: list[Stmt]

    def eval(self, ctx: Ctx):
        inner_ctx = ctx.push({})
        for stmt in self.stmts:
            stmt.eval(inner_ctx)
            
    def validate_self(self, cursor: Cursor):
        declared_vars_in_block = set()
        for stmt in self.stmts:
            if isinstance(stmt, VarDef):
                var_name = stmt.name
                if var_name in declared_vars_in_block:
                    raise SemanticError("variável já declarada", token=var_name)
                declared_vars_in_block.add(var_name)
            stmt.validate_self(stmt.cursor(cursor))


@dataclass
class Method(Stmt):
    """
    Representa um método (função) em ArnoldC.
    Ex.: LISTEN TO ME VERY CAREFULLY myMethod I NEED YOUR CLOTHES...
    """
    name: str
    params: List[str] 
    body: 'StatementBlock' 
    returns_value: bool = False 
    
    def eval(self, ctx: Ctx):
        def arnoldc_method_callable(*args_values):
            if len(args_values) != len(self.params):
                raise TypeError(f"Número incorreto de argumentos para o método '{self.name}'. Esperado {len(self.params)}, recebido {len(args_values)}")
            
            method_ctx = ctx.push({}) 
            for param_name, arg_value in zip(self.params, args_values):
                method_ctx.var_def(param_name, arg_value)
            
            try:
                self.body.eval(method_ctx)
                if self.returns_value:
                    raise SemanticError(f"Método '{self.name}' que retorna valor não tem 'I'LL BE BACK' explícito.")
                return None # Void method
            except ForceReturn as e:
                if not self.returns_value and e.value is not None:
                     raise SemanticError(f"Método void '{self.name}' não pode retornar um valor.")
                return e.value
            
        ctx.var_def(self.name, arnoldc_method_callable)

    def validate_self(self, cursor: Cursor):
        if self.name in RESERVED_KEYWORDS:
            raise SemanticError("nome inválido", token=self.name)
        
        if len(self.params) != len(set(self.params)):
            seen_params = set()
            duplicated_name = None
            for p_name in self.params:
                if p_name in seen_params:
                    duplicated_name = p_name
                    break
                seen_params.add(p_name)
            raise SemanticError("parâmetro duplicado", token=duplicated_name)
        
        self.body.validate_self(self.body.cursor(cursor))


@dataclass
class AssignmentBlock(Stmt):
    """
    Representa o bloco de atribuição complexo do ArnoldC.
    GET TO THE CHOPPER myvar
    HERE IS MY INVITATION initial_value
    [operations]
    ENOUGH TALK
    """
    target_var: str
    initial_value_expr: Expr
    operations: list['OperationExpr'] 

    def eval(self, ctx: Ctx):
        current_value = self.initial_value_expr.eval(ctx)

        for op_node in self.operations:
            operand_value = op_node.operand.eval(ctx)
            if isinstance(op_node, AddOp):
                current_value = current_value + operand_value
            elif isinstance(op_node, SubOp):
                current_value = current_value - operand_value
            elif isinstance(op_node, MulOp):
                current_value = current_value * operand_value
            elif isinstance(op_node, DivOp):
                if operand_value == 0:
                    raise ArnoldCError("Divisão por zero!") 
                current_value = current_value // operand_value
            elif isinstance(op_node, EqOp):
                current_value = 1 if current_value == operand_value else 0
            elif isinstance(op_node, GtOp):
                current_value = 1 if current_value > operand_value else 0
            elif isinstance(op_node, OrOp):
                current_value = 1 if (is_arnoldc_true(current_value) or is_arnoldc_true(operand_value)) else 0
            elif isinstance(op_node, AndOp):
                current_value = 1 if (is_arnoldc_true(current_value) and is_arnoldc_true(operand_value)) else 0
            else:
                raise NotImplementedError(f"Operação ArnoldC não implementada: {type(op_node).__name__}")
        
        ctx.assign(self.target_var, current_value)

    def validate_self(self, cursor: Cursor):
        self.initial_value_expr.validate_self(self.initial_value_expr.cursor(cursor))
        for op_node in self.operations:
            op_node.validate_self(op_node.cursor(cursor))


@dataclass
class OperationExpr(Expr, ABC):
    operand: Expr


@dataclass
class AddOp(OperationExpr): # GET UP
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class SubOp(OperationExpr): # GET DOWN
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class MulOp(OperationExpr): # YOU'RE FIRED
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class DivOp(OperationExpr): # HE HAD TO SPLIT
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class EqOp(OperationExpr): # YOU ARE NOT YOU YOU ARE ME
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class GtOp(OperationExpr): # LET OFF SOME STEAM BENNET
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class OrOp(OperationExpr): # CONSIDER THAT A DIVORCE
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))

@dataclass
class AndOp(OperationExpr): # KNOCK KNOCK
    def eval(self, ctx: Ctx): pass
    def validate_self(self, cursor: Cursor): self.operand.validate_self(self.operand.cursor(cursor))


@dataclass
class CallMethod(Stmt):
    """
    Representa uma chamada de método em ArnoldC.
    GET YOUR ASS TO MARS resultVar DO IT NOW methodName arg1 arg2
    """
    result_var: str
    method_name: str
    arguments: list[Expr]

    def eval(self, ctx: Ctx):
        method_callable = ctx[self.method_name]
        args_values = [arg.eval(ctx) for arg in self.arguments]

        if callable(method_callable):
            try:
                result = method_callable(*args_values)
                if result is not None:
                    ctx.assign(self.result_var, result)
            except TypeError as e:
                raise ArnoldCError(f"Erro na chamada do método '{self.method_name}': {e}")
            except ForceReturn as e:
                 ctx.assign(self.result_var, e.value)
            
        else:
            raise ArnoldCError(f"'{self.method_name}' não é um método.")

    def validate_self(self, cursor: Cursor):
        for arg in self.arguments:
            arg.validate_self(arg.cursor(cursor))
            
            
def is_arnoldc_true(value: "Value") -> bool:
    """Em ArnoldC, 0 é falso, qualquer outro inteiro é verdadeiro. Strings são verdadeiras."""
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return True
    return False

