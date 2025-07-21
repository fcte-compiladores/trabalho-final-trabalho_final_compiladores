"""
Implementa o transformador da árvore sintática que converte entre as representações

    lark.Tree -> arnoldc.arnoldc_ast.Node.

A resolução de vários exercícios requer a modificação ou implementação de vários
métodos desta classe.
"""

from typing import Any, Optional, List, Union
from lark import Transformer, Tree, v_args, Token

from arnoldc.errors import ArnoldCError

from .arnoldc_ast import (
    Bool,
    OperationExpr,
    Program,
    Literal,
    Var,
    Print,
    Return,
    VarDef,
    If,
    While,
    StatementBlock,
    Method,
    AssignmentBlock,
    AddOp, SubOp, MulOp, DivOp, EqOp, GtOp, OrOp, AndOp,
    CallMethod,
    Expr,
    Value
)


@v_args(inline=True)
class ArnoldCTransformer(Transformer):
    # Programa
    # IT'S SHOWTIME ... YOU HAVE BEEN TERMINATED
    def program(self, start_token: Token, body: StatementBlock, end_token: Token) -> Program:
        return Program(body.stmts)

    # Terminais
    def VAR(self, token: Token) -> Var:
        return Var(str(token))

    def STRING(self, token: Token) -> Literal:
        return Literal(str(token)[1:-1])

    def NUMBER(self, token: Token) -> Literal:
        return Literal(int(token))

    def BOOL(self, token: Token) -> Bool: 
        if str(token) == "@NO PROBLEMO":
            return Bool(True) 
        return Bool(False) 

    # Comandos
    def print_cmd(self, _talk_to_the_hand_token: Token, value_to_print_expr: Expr) -> Print:
        return Print(value_to_print_expr)


    def var_def(self, _hey_christmas_tree_token: Token, var_name_node: Var, _you_set_us_up_token: Token, initial_value_expr: Expr) -> VarDef:
        return VarDef(var_name_node.name, initial_value_expr)

    def operation_list(self, *operations: OperationExpr) -> list[OperationExpr]:
        return list(operations)

    def assignment_stmt(self, _get_to_the_chopper_token: Token, target_var_node: Var, _here_is_my_invitation_token: Token, initial_value: Expr, operations_list_node: list[OperationExpr], _enough_talk_token: Token) -> AssignmentBlock:
        return AssignmentBlock(target_var_node.name, initial_value, operations_list_node)
    
    
    # Operações dentro do AssignmentBlock
    def add_op(self, _get_up_token: Token, operand: Expr) -> AddOp: # GET UP
        return AddOp(operand)

    def sub_op(self, _get_down_token: Token, operand: Expr) -> SubOp: # GET DOWN
        return SubOp(operand)

    def mul_op(self, _you_re_fired_token: Token, operand: Expr) -> MulOp: # YOU'RE FIRED
        return MulOp(operand)

    def div_op(self, _he_had_to_split_token: Token, operand: Expr) -> DivOp: # HE HAD TO SPLIT
        return DivOp(operand)

    def eq_op(self, _you_are_not_you_token: Token, operand: Expr) -> EqOp: # YOU ARE NOT YOU YOU ARE ME
        return EqOp(operand)

    def gt_op(self, _let_off_some_steam_bennet_token: Token, operand: Expr) -> GtOp: # LET OFF SOME STEAM BENNET
        return GtOp(operand)

    def or_op(self, _consider_that_a_divorce_token: Token, operand: Expr) -> OrOp: # CONSIDER THAT A DIVORCE
        return OrOp(operand)

    def and_op(self, _knock_knock_token: Token, operand: Expr) -> AndOp: # KNOCK KNOCK
        return AndOp(operand)

    # If
    def if_cmd(self, _because_token: Token, condition: Expr, true_block: StatementBlock, _bullshit_token: Token, else_block: StatementBlock, _you_have_no_respect_token: Token) -> If:
        return If(condition, true_block, else_block)

    # While
    def while_cmd(self, _stick_around_token: Token, condition: Expr, body: StatementBlock, _chill_token: Token) -> While:
        return While(condition, body)

    # Bloco
    def statement_block(self, *stmts: Union[VarDef, AssignmentBlock, Print, If, While, Method, CallMethod, Return]) -> StatementBlock:
        return StatementBlock(list(stmts))

    # Método
    def method_decl(self, _listen_token: Token, method_name_node: Var, *flexible_elements) -> Method:
        method_name_str = method_name_node.name
        
        parameters_vars: List[str] = []
        has_return_type_flag: bool = False 
        body: Optional[StatementBlock] = None
        _hasta_token = flexible_elements[-1] 
        
        elements_before_hasta = flexible_elements[:-1]

        for item in elements_before_hasta:
            if isinstance(item, Var):
                parameters_vars.append(item.name)
            elif isinstance(item, Token) and item.type == 'GIVE_THESE_PEOPLE_AIR':
                has_return_type_flag = True
            elif isinstance(item, StatementBlock):
                body = item

        if body is None:
            raise ArnoldCError(f"Corpo do método (statement_block) não encontrado para o método '{method_name_str}'.")

        returns_value_flag = has_return_type_flag 

        return Method(name=method_name_str, params=parameters_vars, body=body, returns_value=returns_value_flag)


    def method_parameters(self, _i_need_your_clothes_token: Token, param_var: Var) -> Var:
        return param_var

    # Chamada de Método
    def params(self, *expressions: Expr) -> List[Expr]:
        return list(expressions)

    def call_stmt(self, _get_mars_token: Token, result_var_node: Var, _do_it_now_token: Token, method_name_node: Var, params_list: Optional[List[Expr]] = None) -> CallMethod:
        result_var_name = result_var_node.name
        method_name_str = method_name_node.name 

        method_arguments = params_list if params_list is not None else []

        return CallMethod(result_var=result_var_name, method_name=method_name_str, arguments=method_arguments)
        
    def return_stmt(self, _ill_be_back_token: Token, value_expr: Expr) -> Return:
        return Return(value=value_expr)

