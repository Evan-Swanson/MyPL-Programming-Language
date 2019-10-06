#Evan Swanson 3/36/2019
#mypl_interpreter.py

import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as sym_tbl

class ReturnException(Exception): pass

class Interpreter(ast.Visitor):
    """A MyPL interpret visitor implementation"""
    def __init__(self):
        # initialize the symbol table (for ids -> values)
        self.sym_table = sym_tbl.SymbolTable()
        # holds the type of last expression type
        self.current_value = None
        # the heap {oid:struct_obj}
        self.heap = {}


    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)

    # starts the interpreter (handles return from global scope)
    def run(self, stmt_list):
        try:
            stmt_list.accept(self)
        except ReturnException:
            pass

    def visit_stmt_list(self, stmt_list):
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        exp_value = self.current_value
        var_name = var_decl.var_id.lexeme
        self.sym_table.add_id(var_decl.var_id.lexeme)
        self.sym_table.set_info(var_decl.var_id.lexeme, exp_value)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        #lvalue takes care of setting value
        assign_stmt.lhs.accept(self)


    def visit_struct_decl_stmt(self, struct_decl):
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        currentID = self.sym_table.get_env_id()
        self.sym_table.set_info(struct_decl.struct_id.lexeme, [currentID, struct_decl])


    def visit_fun_decl_stmt(self, fun_decl):
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        currentEnv = self.sym_table.get_env_id()
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [currentEnv, fun_decl])


    def visit_return_stmt(self, return_stmt):
        #set current value to return expression
        return_stmt.return_expr.accept(self)
        raise ReturnException()

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)
        while(self.current_value):
            while_stmt.stmt_list.accept(self)
            while_stmt.bool_expr.accept(self)

    def visit_if_stmt(self, if_stmt):
        foundBlock = False
        if_stmt.if_part.bool_expr.accept(self)

        if self.current_value:
            if_stmt.if_part.stmt_list.accept(self)
            foundBlock = True
        else:
            #elseifs
            for ifs in if_stmt.elseifs:
                ifs.bool_expr.accept(self)
                if self.current_value:
                    ifs.stmt_list.accept(self)
                    foundBlock = True
                    break
        if if_stmt.has_else and not foundBlock:
            if_stmt.else_stmts.accept(self)
        

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        first = self.current_value
        complex_expr.rest.accept(self)
        rest = self.current_value
        if complex_expr.math_rel.tokentype == token.PLUS:
            self.current_value = first + rest
        elif complex_expr.math_rel.tokentype == token.MINUS:
            self.current_value = first - rest
        elif complex_expr.math_rel.tokentype == token.MULTIPLY:
            self.current_value = first * rest
        elif complex_expr.math_rel.tokentype == token.DIVIDE:
            #integer division
            if type(1) == type(first):
                self.current_value = first // rest
            else:
                self.current_value = first / rest
        elif complex_expr.math_rel.tokentype == token.MODULO:
            self.current_value = first % rest

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        first = self.current_value
        if bool_expr.bool_rel != None:
            bool_expr.second_expr.accept(self)
            second = self.current_value
            if bool_expr.bool_rel.tokentype == token.EQUAL:
                self.current_value = (first == second)
            elif bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                if first != second:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN:
                if first > second:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN:
                if first < second:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN_EQUAL:
                if first >= second:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN_EQUAL:
                if first <= second:
                    self.current_value = True
                else:
                    self.current_value = False

        if bool_expr.bool_connector != None:
            first_rest_val = self.current_value
            bool_expr.rest.accept(self)
            second_rest_val = self.current_value
            if bool_expr.bool_connector.tokentype == token.AND:
                self.current_value = first_rest_val and second_rest_val
            else:
                self.current_value = first_rest_val or second_rest_val

        if bool_expr.negated == True:
            self.current_value = not self.current_value


    def visit_lvalue(self, lval):
        currentDict = {}
        identifier = lval.path[0].lexeme
        if len(lval.path) == 1:
            self.sym_table.set_info(identifier, self.current_value)
        else:
            for token in lval.path:
                if token == lval.path[-1]:
                     currentDict[token.lexeme] = self.current_value
                elif token == lval.path[0]:
                        currentDict = self.heap[self.sym_table.get_info(token.lexeme)]
                else:
                        currentDict = self.heap[currentDict[token.lexeme]]


    def visit_fun_param(self, fun_param): pass

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_value = int(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_value = float(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_value = True
            if simple_rvalue.val.lexeme == 'false':
                self.current_value = False
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_value = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_value = None

    def visit_new_rvalue(self, new_rvalue):
        struct_info = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
        curr_env = self.sym_table.get_env_id()
        self.sym_table.set_env_id(struct_info[0])
        struct_obj = {}
        self.sym_table.push_environment()
        for x in struct_info[1].var_decls:
            x.var_expr.accept(self)
            struct_obj[x.var_id.lexeme] = self.current_value
        self.sym_table.pop_environment()
        self.sym_table.set_env_id(curr_env)
        oid = id(struct_obj)
        self.heap[oid] = struct_obj
        self.current_value = oid


    def visit_call_rvalue(self, call_rvalue):
        # handle built in functions first
        built_ins = ['print', 'length', 'get', 'readi', 'reads',
        'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof']
        if call_rvalue.fun.lexeme in built_ins:
            self.__built_in_fun_helper(call_rvalue)
        else:
            args = {}
            #get function info
            fun_info = self.sym_table.get_info(call_rvalue.fun.lexeme)
            #store env
            currentEnv = self.sym_table.get_env_id()
            #compute and store arg values
            for x in range(len(fun_info[1].params)):
                call_rvalue.args[x].accept(self)
                args[fun_info[1].params[x].param_name.lexeme] = self.current_value
            #go to function decl env
            self.sym_table.set_env_id(fun_info[0])
            #add a new env for function to run in
            self.sym_table.push_environment()
            #initialize parameters
            for name, value in args.items():
                self.sym_table.add_id(name)
                self.sym_table.set_info(name, value)
            #visit functin body and catch return statement
            try:
                fun_info[1].stmt_list.accept(self)
            except ReturnException:
                pass
            #remove the new environment
            self.sym_table.pop_environment()
            #return to caller's env
            self.sym_table.set_env_id(currentEnv)


    def visit_id_rvalue(self, id_rvalue):
        currentDict = {}
        if len(id_rvalue.path) > 1:
            for token in id_rvalue.path:
                if token == id_rvalue.path[-1]:
                    self.current_value = currentDict[token.lexeme]
                elif token == id_rvalue.path[0]:
                    currentDict = self.heap[self.sym_table.get_info(token.lexeme)]
                else:
                    currentDict = self.heap[currentDict[token.lexeme]]
        else:
            self.current_value = self.sym_table.get_info(id_rvalue.path[0].lexeme)

    def __built_in_fun_helper(self, call_rvalue):
        fun_name = call_rvalue.fun.lexeme
        arg_vals = []
        #... evaluate each call argument and store in arg_vals ...
        for arg in call_rvalue.args:
            arg.accept(self)
            arg_vals.append(self.current_value)

        # check for nil values
        for i, arg in enumerate(arg_vals):
            if arg is None:
                #... report a nil value error ...
                msg = 'nil value in function call'
                self.__error(msg, call_rvalue.fun)
                
        # perform each function
        if fun_name == 'print':
            arg_vals[0] = arg_vals[0].replace(r'\n','\n')
            print(arg_vals[0], end='')
        elif fun_name == 'length':
            self.current_value = len(arg_vals[0])
        elif fun_name == 'get':
            if 0 <= arg_vals[0] < len(arg_vals[1]):
                self.current_value = arg_vals[1][arg_vals[0]]
            else:
                #... report index out of range error ...
                msg = 'index out of range'
                self.__error(msg, call_rvalue.fun)
        elif fun_name == 'reads':
            self.current_value = input()
        elif fun_name == 'readi':
            try:
                self.current_value = int(input())
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'readf':
            try:
                self.current_value = float(input())
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)
        elif fun_name == 'itof':
            try:
                self.current_value = float(arg_vals[0])
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'itos':
            try:
                self.current_value = str(arg_vals[0])
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'ftos':
            try:
                float(arg_vals[0])
                self.current_value = str(arg_vals[0])
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)
        elif fun_name == 'stoi':
            try:
                self.current_value = int(arg_vals[0])
            except ValueError:
                self.__error('bad string value', call_rvalue.fun)
        elif fun_name == 'stof':
            try:
                self.current_value = float(arg_vals[0])
            except ValueError:
                self.__error('bad string value', call_rvalue.fun)
        #... etc ...
