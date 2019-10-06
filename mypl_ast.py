import mypl_token as token

class ASTNode(object):
    """The base class for the abstract syntax tree."""
    def accept(self, visitor): pass

class Stmt(ASTNode):
    """The base class for all statement nodes."""
    def accept(self, visitor): pass

class StmtList(ASTNode):
    """A statement list consists of a list of statements."""
    def __init__(self):
        self.stmts = [] # list of Stmt
    def accept(self, visitor):
        visitor.visit_stmt_list(self)

class Expr(ASTNode):
    """The base class for all expression nodes."""
    def accept(self, visitor): pass

class ExprStmt(Stmt):
    """A simple statement that is just an expression."""
    def __init__(self):
        self.expr = Expr() # Expr node
    def accept(self, visitor):
        visitor.visit_expr_stmt(self)

class VarDeclStmt(Stmt):
    """A variable declaration statement consists of a variable identifier,
    an (optional) type, and an initial value.
    """
    def __init__(self):
        self.var_id = None # Token (ID)
        self.var_type = None # Token (STRINGTYPE, ..., ID)
        self.var_expr = Expr() # Expr node
    def accept(self, visitor):
        visitor.visit_var_decl_stmt(self)

class AssignStmt(Stmt):
    """An assignment statement consists of an identifier and an expression.
    """
    def __init__(self):
        self.lhs = None # LValue node
        self.rhs = Expr() # Expr node
    def accept(self, visitor):
        visitor.visit_assign_stmt(self)

class StructDeclStmt(Stmt):
    """A struct declaration statement consists of an identifier, and a
    list of variable declarations.
    """
    def __init__(self):
        self.struct_id = None # Token (id)
        self.var_decls = [] # [VarDeclStmt]
    def accept(self, visitor):
        visitor.visit_struct_decl_stmt(self)

class FunDeclStmt(Stmt):
    """A function declaration statement consists of an identifer, a list
    of parameters (identifiers with types), a return type, and a list
    of function body statements."""
    def __init__(self):
        self.fun_name = None # Token (id)
        self.params = [] # List of FunParam
        self.return_type = None # Token
        self.stmt_list = StmtList() # StmtList
    def accept(self, visitor):
        visitor.visit_fun_decl_stmt(self)

class ReturnStmt(Stmt):
    """A return statement consist of a return expression and the
    corresponding return token (for printing line and column numbers).
    """
    def __init__(self):
        self.return_expr = Expr() # Expr
        self.return_token = None # to keep track of location (e.g., return;)
    def accept(self, visitor):
        visitor.visit_return_stmt(self)

class WhileStmt(Stmt):
    """A while statement consists of a condition (Boolean expression) and
    a statement list (the body of the while).
    """
    def __init__(self):
        self.bool_expr = BoolExpr() # a BoolExpr node
        self.stmt_list = StmtList()
    def accept(self, visitor):
        visitor.visit_while_stmt(self)

class IfStmt(Stmt):
    """An if stmt consists of a basic if part, a (possibly empty) list of
    else ifs, and an optional else part (represented as a statement
    list).
    """
    def __init__(self):
        self.if_part = BasicIf()
        self.elseifs = [] # list of BasicIf
        self.has_else = False
        self.else_stmts = StmtList()
    def accept(self, visitor):
        visitor.visit_if_stmt(self)

class SimpleExpr(Expr):
    """A simple expression consists of an RValue.
    """
    def __init__(self):
        self.term = None # RValue
    def accept(self, visitor):
        visitor.visit_simple_expr(self)

class ComplexExpr(Expr):
    """A complex expression consist of an expression, followed by a
    mathematical operator (+, -, *, etc.), followed by another
    (possibly complex) expression.
    """
    def __init__(self):
        self.first_operand = Expr() # Expr node
        self.math_rel = None # Token (+, -, *, etc.)
        self.rest = Expr() # Expr node
    def accept(self, visitor):
        visitor.visit_complex_expr(self)

class BoolExpr(ASTNode):
    """A boolean expression consists of an expression, a Boolean relation
    (==, <=, !=, etc.), another expression, and possibly an 'and' or
    'or' followed by additional boolean expressions. An entire boolean
    expression can also be negated. Note that only the first_expr is
    required.
    """
    def __init__(self):
        self.first_expr = Expr() # Expr node
        self.bool_rel = None # Token (==, <=, !=, etc.)
        self.second_expr = Expr() # Expr node
        self.bool_connector = None # Token (AND or OR)
        self.rest = None # BoolExpr node
        self.negated = False # Bool
    def accept(self, visitor):
        visitor.visit_bool_expr(self)

class LValue(ASTNode):
    """A lvalue consist of a simple id or a path expression.
    """
    def __init__(self):
        self.path = [] # [Token (ID)] ... one implies simple var
    def accept(self, visitor):
        visitor.visit_lvalue(self)

class FunParam(Stmt):
    """A function declaration parameter consists of a variable name (id)
    and a type."""
    def __init__(self):
        self.param_name = None # Token (id)
        self.param_type = None # Token (id)
    def accept(self, visitor):
        visitor.visit_fun_param(self)

class BasicIf(object):
    """A basic if holds a condition (Boolean expression) and a list of
    statements (the body of the if).
    """
    def __init__(self):
        self.bool_expr = BoolExpr() # BoolExpr node
        self.stmt_list = StmtList()

class RValue(ASTNode):
    """The base class for rvalue nodes."""
    def accept(self, visitor): pass

class SimpleRValue(RValue):
    """A simple rvalue consists of a single primitive value.
    """
    def __init__(self):
        self.val = None # Token
    def accept(self, visitor):
        visitor.visit_simple_rvalue(self)

class NewRValue(RValue):
    """A new rvalue consists of a struct name (id)
    """
    def __init__(self):
        self.struct_type = None # Token (id)
    def accept(self, visitor):
        visitor.visit_new_rvalue(self)

class CallRValue(RValue):
    """A function call rvalue consists of a function name (id) and a list
    of arguments (expressions)
    """
    def __init__(self):
        self.fun = None # Token (id)
        self.args = [] # list of Expr
    def accept(self, visitor):
        visitor.visit_call_rvalue(self)

class IDRvalue(RValue):
    """An identifier rvalue consists of a path of one or more identifiers.
    """
    def __init__(self):
        self.path = [] # List of Token (id)
    def accept(self, visitor):
        visitor.visit_id_rvalue(self)

class Visitor(object):
    """The base class for AST visitors.
    """
    def visit_stmt_list(self, stmt_list): pass
    def visit_expr_stmt(self, expr_stmt): pass
    def visit_var_decl_stmt(self, var_decl): pass
    def visit_assign_stmt(self, assign_stmt): pass
    def visit_struct_decl_stmt(self, struct_decl): pass
    def visit_fun_decl_stmt(self, fun_decl): pass
    def visit_return_stmt(self, return_stmt): pass
    def visit_while_stmt(self, while_stmt): pass
    def visit_if_stmt(self, if_stmt): pass
    def visit_simple_expr(self, simple_expr): pass
    def visit_complex_expr(self, complex_expr): pass
    def visit_bool_expr(self, bool_expr): pass
    def visit_lvalue(self, lval): pass
    def visit_fun_param(self, fun_param): pass
    def visit_simple_rvalue(self, simple_rvalue): pass
    def visit_new_rvalue(self, new_rvalue): pass
    def visit_call_rvalue(self, call_rvalue): pass
    def visit_id_rvalue(self, id_rvalue): pass