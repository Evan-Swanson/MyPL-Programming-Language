import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table

class TypeChecker(ast.Visitor):
    #A MyPL type checker visitor implementation where struct types
    #take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    #take the form: fun_id -> [[t1, t2, ..., tn,], return_type]'''

    def __init__(self):
        # initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', token.INTTYPE)
        # load in built-in function types
        self.sym_table.add_id('print')
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
        #... put remaining built-in function types here ...
        #Functions: [[params], reutrnType]
        self.sym_table.add_id('length')
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('get')
        self.sym_table.set_info('get', [[token.INTTYPE, token.STRINGTYPE], token.STRINGTYPE])
        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', [[], token.STRINGTYPE])
        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', [[token.INTTYPE], token.FLOATTYPE])
        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', [[token.INTTYPE], token.STRINGTYPE])
        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', [[token.FLOATTYPE], token.STRINGTYPE])
        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', [[], token.INTTYPE])
        self.sym_table.add_id('stoi')
        self.sym_table.set_info('stoi', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('stof')
        self.sym_table.set_info('stof', [[token.STRINGTYPE], token.FLOATTYPE])
        self.sym_table.add_id('readf')
        self.sym_table.set_info('readf', [[], token.FLOATTYPE])
    
    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)

    def visit_stmt_list(self, stmt_list):
        pass
        #disable for this assignment

        # add new block (scope)
        #self.sym_table.push_environment()
        #for stmt in stmt_list.stmts:
        #    stmt.accept(self)
        # remove new block
        #self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
    #... you need to define this one ...
        var_decl.var_expr.accept(self)
        rhs_type = self.current_type
        var_id = var_decl.var_id
        curr_env = self.sym_table.get_env_id()
        #check that variable isnt already defined
        if self.sym_table.id_exists_in_env(var_id.lexeme, curr_env):
            msg = 'variable already defined in current environemnt'
            self.__error(msg, var_id)
        if rhs_type == token.NIL:
            if var_decl.var_type != None:
                self.sym_table.add_id(var_decl.var_id.lexeme)
                if var_decl.var_type.tokentype  == token.ID: # a stuct
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.lexeme)
                else:
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.tokentype)
            else:
                msg = "invalid declaration, can't infer type"
                self.__error(msg, var_decl.var_id)
        else:
            self.sym_table.add_id(var_decl.var_id.lexeme)
            self.sym_table.set_info(var_decl.var_id.lexeme,rhs_type)
            if var_decl.var_type != None:
                if var_decl.var_type.tokentype == token.ID: #a struct
                    if rhs_type != var_decl.var_type.lexeme:
                        msg = 'mismatch type in variable declaration'
                        self.__error(msg, var_decl.var_type)

                else:    
                    if rhs_type != var_decl.var_type.tokentype:
                        msg = 'mismatch type in variable declaration'
                        self.__error(msg, var_decl.var_type)


    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])

    #... finish remaining visit calls ...
    def visit_struct_decl_stmt(self, struct_decl):
        structDic = {}
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        self.sym_table.push_environment() #dont overide variables 
        for var in struct_decl.var_decls:
            var.accept(self)
            structDic[var.var_id.lexeme] = self.sym_table.get_info(var.var_id.lexeme)
        self.sym_table.pop_environment()
        self.sym_table.set_info(struct_decl.struct_id.lexeme, structDic)

    #Functions: [[params], reutrnType]
    def visit_fun_decl_stmt(self, fun_decl):
        params = []
        paramNames = []
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        for param in fun_decl.params:
            param.accept(self)
            if param.param_name.lexeme in paramNames:
                msg = 'matching function parameter names'
                self.__error(msg, param.param_name)
            paramNames.append(param.param_name.lexeme)
            params.append(self.current_type)
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [params, fun_decl.return_type.tokentype])
        self.sym_table.push_environment()
        self.sym_table.add_id('return') #here
        if fun_decl.return_type.tokentype != 'ID':
            self.sym_table.set_info('return', fun_decl.return_type.tokentype)
        else:
            self.sym_table.set_info('return', fun_decl.return_type.lexeme)
        for param in fun_decl.params:   #add parameters to new environment
            self.sym_table.add_id(param.param_name.lexeme)
            self.sym_table.set_info(param.param_name.lexeme, param.param_type.tokentype)
        fun_decl.stmt_list.accept(self)
        self.sym_table.pop_environment()
        

    def visit_return_stmt(self, return_stmt):
        return_stmt.return_expr.accept(self)
        if self.current_type != self.sym_table.get_info('return') and self.current_type != token.NIL:
            msg = 'invalid return statement'
            self.__error(msg, return_stmt.return_token)
        

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)
        if self.current_type != token.BOOLTYPE:
            msg = 'invalid bool statment'
            self.__error(msg, while_stmt.bool_expr.bool_rel)
        while_stmt.stmt_list.accept(self)

    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)
        if self.current_type != token.BOOLTYPE:
            msg = 'invalid bool statment'
            self.__error(msg, while_stmt.first_expr)
        if_stmt.if_part.stmt_list.accept(self)
        for basicIf in if_stmt.elseifs:
            basicIf.bool_expr.accept(self)
            if self.current_type != token.BOOLTYPE:
                msg = 'invalid bool statment'
                self.__error(msg, while_stmt.first_expr)
            basicIf.stmt_list.accept(self)
        if if_stmt.has_else:
            if_stmt.else_stmts.accept(self)


    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        firstOp = self.current_type
        complex_expr.rest.accept(self)
        temp = [token.STRINGTYPE, token.INTTYPE, token.FLOATTYPE]

        if not(firstOp in temp):
            msg = 'invalid operator types'
            self.__error(msg, complex_expr.math_rel)

        if firstOp != self.current_type:
            msg = 'operator mismatch of types'
            self.__error(msg, complex_expr.math_rel)

        if firstOp == 'STRINGTYPE':
            if complex_expr.math_rel.tokentype != token.PLUS:
                msg = 'operator type error'
                self.__error(msg, complex_expr.math_rel)

        if complex_expr.math_rel.tokentype == token.MODULO:
            if firstOp != token.INTTYPE:
                msg = 'modulo operator requires ints'
                self.__error(msg, complex_expr.math_rel)

            
    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        firstExpr = self.current_type
        #some dont have second expr
        bool_expr.second_expr.accept(self)
        secondExpr = self.current_type

        temp = [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE, token.STRUCTTYPE, token.NIL]
        temp2 = [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]

        #need to add struct check
        if bool_expr.bool_rel != None:
            if firstExpr == secondExpr and (firstExpr in temp or self.sym_table.id_exists(firstExpr)):
                if bool_expr.bool_rel.tokentype == token.EQUAL or bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                    self.current_type = token.BOOLTYPE
                elif firstExpr in temp2:
                    self.current_type = token.BOOLTYPE
                else:
                    msg = 'invalid boolean comparison'
                    self.__error(msg, bool_expr.bool_rel)

            elif firstExpr == token.NIL and (secondExpr in temp or self.sym_table.id_exists(secondExpr)) and secondExpr != token.NIL:
                if bool_expr.bool_rel.tokentype == token.EQUAL or bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                    self.current_type = token.BOOLTYPE
                else:
                    msg = 'invalid boolean comparison with nil value'
                    self.__error(msg, bool_expr.bool_rel)
            elif (firstExpr in temp or self.sym_table.id_exists(firstExpr)) and secondExpr == token.NIL and firstExpr != token.NIL:
                if bool_expr.bool_rel.tokentype == token.EQUAL or bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                    self.current_type = token.BOOLTYPE
                else:
                    msg = 'invalid boolean comparison with nil value'
                    self.__error(msg, bool_expr.bool_rel)

            else :
                msg = 'invalid boolean comparison'
                self.__error(msg, bool_expr.bool_rel)
        
        if bool_expr.bool_connector != None:
            bool_expr.rest.accept(self)
            if self.current_type != token.BOOLTYPE:
                msg = 'invalid boolean conncetor operation'
                self.__error(msg, bool_expr.bool_rel)



    def visit_lvalue(self, lval):
        currentDict = {}
        if not self.sym_table.id_exists(lval.path[0].lexeme):
            msg = 'variable not defined'
            self.__error(msg, lval.path[0])
        if len(lval.path) == 1:
                self.current_type = self.sym_table.get_info(lval.path[0].lexeme)
        else:
            for token in lval.path:
                if token == lval.path[-1]:
                    self.current_type = currentDict[token.lexeme]
                elif token == lval.path[0]:
                    if self.sym_table.id_exists(token.lexeme):
                        currentDict = self.sym_table.get_info(self.sym_table.get_info(token.lexeme))
                    else:
                        msg = 'invalid variable path'
                        self.__error(msg, token)
                else:
                    if token.lexeme in currentDict:
                        currentDict = self.sym_table.get_info(currentDict[token.lexeme])
                    else:
                        msg = 'invalid variable path'
                        self.__error(msg, token)

    def visit_fun_param(self, fun_param):
        self.current_type = fun_param.param_type.tokentype
        if self.current_type == 'ID':
            self.current_type = fun_param.param_type.lexeme

    def visit_simple_rvalue(self, simple_rvalue):
        self.current_type = simple_rvalue.val.tokentype
        if self.current_type == 'INTVAL':
            self.current_type = 'INTTYPE'
        elif self.current_type == 'STRINGVAL':
            self.current_type = 'STRINGTYPE'
        elif self.current_type == 'FLOATVAL':
            self.current_type = 'FLOATTYPE'
        elif self.current_type == 'BOOLVAL':
            self.current_type = 'BOOLTYPE'
        

    def visit_new_rvalue(self, new_rvalue):
        if not self.sym_table.id_exists(new_rvalue.struct_type.lexeme):
            msg = 'struct not defined'
            self.__error(msg, new_rvalue.struct_type)

        self.current_type = new_rvalue.struct_type.lexeme

    def visit_call_rvalue(self, call_rvalue):
        if not self.sym_table.id_exists(call_rvalue.fun.lexeme):
            msg = 'function not defined'
            self.__error(msg, call_rvalue.fun)
        paramList = self.sym_table.get_info(call_rvalue.fun.lexeme)[0]
        if len(paramList) != len(call_rvalue.args):
            msg = 'mismatch parameter list length'
            self.__error(msg, call_rvalue.fun)
        for arg in range(len(call_rvalue.args)):
            call_rvalue.args[arg].accept(self)
            if paramList[arg] != self.current_type and self.current_type != token.NIL:
                msg = 'mismatch parameter type'
                self.__error(msg, call_rvalue.fun)
        self.current_type = self.sym_table.get_info(call_rvalue.fun.lexeme)[1]
        
            

    def visit_id_rvalue(self, id_rvalue):
        currentDict = {}
        if not self.sym_table.id_exists(id_rvalue.path[0].lexeme):
            msg = 'variable not defined'
            self.__error(msg, id_rvalue.path[0])

        if len(id_rvalue.path) == 1:
                self.current_type = self.sym_table.get_info(id_rvalue.path[0].lexeme)

        else:
            for token in id_rvalue.path:
                if token == id_rvalue.path[-1]:
                    self.current_type = currentDict[token.lexeme]
                elif token == id_rvalue.path[0]:
                    if self.sym_table.id_exists(token.lexeme):
                        currentDict = self.sym_table.get_info(self.sym_table.get_info(token.lexeme))
                    else:
                        msg = 'invalid variable path'
                        self.__error(msg, token)
                else:
                    if token.lexeme in currentDict:
                        currentDict = self.sym_table.get_info(currentDict[token.lexeme])
                    else:
                        msg = 'invalid variable path'
                        self.__error(msg, token)