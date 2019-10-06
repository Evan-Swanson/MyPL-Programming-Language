import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def parse(self):
    #succeeds if program is syntactically well-formed
        stmt_list_node = ast.StmtList()
        self.__advance()
        self.__stmts(stmt_list_node)
        self.__eat(token.EOS, 'expecting end of file')
        return stmt_list_node

    def __advance(self):
        self.current_token = self.lexer.next_token()

    def __eat(self, tokentype, error_msg):
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error(error_msg)

    def __error(self, error_msg):
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(s, l, c)

    # Beginning of recursive descent functions------

    def __stmts(self, stmt_list_node):
    #<stmts> ::= <stmt> <stmts> | e
        if self.current_token.tokentype != token.EOS:
            self.__stmt(stmt_list_node)
            self.__stmts(stmt_list_node)

    def __stmt(self, stmt_list_node):
    #<stmt> ::= <sdecl> | <fdecl> | <bstmt>
        if self.current_token.tokentype == token.STRUCTTYPE:
            self.__sdecl(stmt_list_node)
        elif self.current_token.tokentype == token.FUN:
            self.__fdecl(stmt_list_node)
        else:
            self.__bstmt(stmt_list_node)

    def __bstmts(self, stmt_list_node):  #return a StmtList?
        bstmtlist = [token.VAR, token.SET, token.IF, token.WHILE, token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.RETURN, token.ID, token.LPAREN]
        if self.current_token.tokentype in bstmtlist:
            self.__bstmt(stmt_list_node)
            self.__bstmts(stmt_list_node)
    
    def __bstmt(self, stmt_list_node):
        if self.current_token.tokentype == token.VAR:
            self.__vdecl(stmt_list_node.stmts)
        elif self.current_token.tokentype == token.SET:
            self.__assign(stmt_list_node)
        elif self.current_token.tokentype == token.IF:
            self.__cond(stmt_list_node)
        elif self.current_token.tokentype == token.WHILE:
            self.__while(stmt_list_node)
        elif self.current_token.tokentype == token.RETURN:
            self.__exit(stmt_list_node)
        else:
            exprStmtNode = ast.ExprStmt()
            exprStmtNode.expr = self.__expr()
            stmt_list_node.stmts.append(exprStmtNode)
            self.__eat(token.SEMICOLON, 'expecting semicolon')
    
    def __sdecl(self, stmt_list_node):
        structNode = ast.StructDeclStmt()
        self.__eat(token.STRUCTTYPE, 'expecting struct type')
        structNode.struct_id = self.current_token
        self.__eat(token.ID, 'expecting identifier')
        self.__vdecls(structNode.var_decls)
        self.__eat(token.END, 'expecting end')
        stmt_list_node.stmts.append(structNode)

    def __vdecls(self, stmt_list_node):     #Return a VarDeclStmt?
        if self.current_token.tokentype == token.VAR:
            self.__vdecl(stmt_list_node)
            self.__vdecls(stmt_list_node)
    
    def __fdecl(self, stmt_list_node):
        functionNode = ast.FunDeclStmt()
        self.__eat(token.FUN, 'expecting fun')
        typelist = [token.ID, token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
        functionNode.return_type = self.current_token
        if self.current_token.tokentype in typelist:
            self.__type()
        else:
            self.__eat(token.NIL, 'expecting nil')
        functionNode.fun_name = self.current_token
        self.__eat(token.ID, "expecting id")
        self.__eat(token.LPAREN, "expecting (")
        self.__params(functionNode)
        self.__eat(token.RPAREN, 'expecting )')
        self.__bstmts(functionNode.stmt_list)
        self.__eat(token.END, 'expecting end')
        stmt_list_node.stmts.append(functionNode)

    def __params(self, functionNode):
        if self.current_token.tokentype == token.ID:
            funParamNode = ast.FunParam()
            funParamNode.param_name = self.current_token
            self.__eat(token.ID, 'expecting id')
            self.__eat(token.COLON, 'expecting colon')
            funParamNode.param_type = self.current_token
            self.__type()
            functionNode.params.append(funParamNode)
            while self.current_token.tokentype == token.COMMA:
                self.__eat(token.COMMA, 'expecting ,')
                funParamNode = ast.FunParam()
                funParamNode.param_name = self.current_token
                self.__eat(token.ID, 'expecting id')
                self.__eat(token.COLON, 'expecting :')
                funParamNode.param_type = self.current_token
                self.__type()
                functionNode.params.append(funParamNode)

    def __type(self): 
        if self.current_token.tokentype == token.ID:
            self.__advance()
        elif self.current_token.tokentype == token.INTTYPE:
            self.__advance()
        elif self.current_token.tokentype == token.FLOATTYPE:
            self.__advance()
        elif self.current_token.tokentype == token.BOOLTYPE:
            self.__advance()
        else:
            self.__eat(token.STRINGTYPE, 'expecting type')

    def __exit(self, stmt_list_node):
        returnNode = ast.ReturnStmt()
        returnNode.return_token = self.current_token
        self.__eat(token.RETURN, 'expecting return')
        listofexpr = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID]
        if self.current_token.tokentype in listofexpr:
            returnNode.return_expr = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting ;')
        stmt_list_node.stmts.append(returnNode)


    def __vdecl(self, listToAppendTo):     
        varDeclNode = ast.VarDeclStmt()
        self.__eat(token.VAR, 'expecting var')
        varDeclNode.var_id = self.current_token
        self.__eat(token.ID, 'expecting id')
        self.__tdecl(varDeclNode)
        self.__eat(token.ASSIGN, 'expecting =') 
        varDeclNode.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting ;')
        listToAppendTo.append(varDeclNode)

    def __tdecl(self, varDeclNode):
        if self.current_token.tokentype == token.COLON:
            self.__advance()
            varDeclNode.var_type = self.current_token
            self.__type()
    
    def __assign(self, stmt_list_node):
        assignNode = ast.AssignStmt()
        self.__eat(token.SET, 'expecting set')
        self.__lvalue(assignNode)
        self.__eat(token.ASSIGN, 'expecting =')
        assignNode.rhs = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting ;')
        stmt_list_node.stmts.append(assignNode)

    def __lvalue(self, assignNode):
        lvalueNode = ast.LValue()
        lvalueNode.path.append(self.current_token)
        self.__eat(token.ID, 'expecting id')
        while self.current_token.tokentype == token.DOT:
            self.__advance()
            lvalueNode.path.append(self.current_token)
            self.__eat(token.ID, 'expecting id')
        assignNode.lhs = lvalueNode

    def __cond(self, stmt_list_node):
        condNode = ast.IfStmt()
        basicIfNode = ast.BasicIf()
        self.__eat(token.IF, 'expecting if')
        basicIfNode.bool_expr.first_expr = ast.Expr()
        self.__bexpr(basicIfNode.bool_expr) #might need to declare before pass
        self.__eat(token.THEN, 'expecting then')
        self.__bstmts(basicIfNode.stmt_list) #same here
        condNode.if_part = basicIfNode
        self.__condt(condNode)
        self.__eat(token.END, 'expecting end')
        stmt_list_node.stmts.append(condNode)


    def __condt(self, condNode):
        if self.current_token.tokentype == token.ELIF:
            basicIfNode = ast.BasicIf()
            self.__eat(token.ELIF, 'expecting elif')
            self.__bexpr(basicIfNode.bool_expr) #here
            self.__eat(token.THEN, 'expecting then')
            self.__bstmts(basicIfNode.stmt_list)
            condNode.elseifs.append(basicIfNode)
            self.__condt(condNode)
        elif self.current_token.tokentype == token.ELSE:
            condNode.has_else = True
            self.__advance()
            self.__bstmts(condNode.else_stmts) #here

    def __while(self, stmt_list_node):
        whileNode = ast.WhileStmt()
        self.__eat(token.WHILE, 'expecting while')
        self.__bexpr(whileNode.bool_expr)
        self.__eat(token.DO, 'expecting do')
        self.__bstmts(whileNode.stmt_list)
        self.__eat(token.END, 'expecting end')
        stmt_list_node.stmts.append(whileNode)
    
    def __expr(self):  #return an Expr
        exprNode = ast.SimpleExpr()
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            exprNode = self.__expr()
            self.__eat(token.RPAREN, 'expecting )')
        else:
            self.__rvalue(exprNode)

        mathrels = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO]
        if self.current_token.tokentype in mathrels:
            tempExpr = exprNode
            exprNode = ast.ComplexExpr()
            exprNode.first_operand = tempExpr
            exprNode.math_rel = self.current_token
            self.__advance()
            exprNode.rest = self.__expr()
        #print(exprNode.path[0])
        return exprNode

    def __mathrels(self):
        if self.current_token.tokentype == token.PLUS:
             self.__advance
        elif self.current_token.tokentype == token.MINUS:
             self.__advance
        elif self.current_token.tokentype == token.DIVIDE:
             self.__advance
        elif self.current_token.tokentype == token.MULTIPLY:
             self.__advance
        else:
            self.__eat(token.MODULO, 'expecting mathrelation')
    
    def __rvalue(self, exprNode):
        if self.current_token.tokentype == token.STRINGVAL:
            exprNode.term = ast.SimpleRValue()
            exprNode.term.val = self.current_token
            self.__advance()
        elif self.current_token.tokentype == token.INTVAL:
            exprNode.term = ast.SimpleRValue()
            exprNode.term.val = self.current_token
            self.__advance()
        elif self.current_token.tokentype == token.BOOLVAL:
            exprNode.term = ast.SimpleRValue()
            exprNode.term.val = self.current_token
            self.__advance()
        elif self.current_token.tokentype == token.FLOATVAL:
            exprNode.term = ast.SimpleRValue()
            exprNode.term.val = self.current_token
            self.__advance()
        elif self.current_token.tokentype == token.NIL:
            exprNode.term = ast.SimpleRValue()
            exprNode.term.val = self.current_token
            self.__advance()
        elif self.current_token.tokentype == token.NEW:
            self.__advance()
            exprNode.term = ast.NewRValue()
            exprNode.term.struct_type = self.current_token
            self.__eat(token.ID, 'expecting id')
        else:
            self.__idrval(exprNode)
    
    def __idrval(self, exprNode):
        temp = self.current_token
        self.__eat(token.ID, 'expecting id')
        if self.current_token.tokentype == token.LPAREN:
            exprNode.term = ast.CallRValue()
            exprNode.term.fun = temp
            self.__eat(token.LPAREN, 'expecting (') 
            self.__exprlist(exprNode.term)
            self.__eat(token.RPAREN, 'expecting )')

        else:
            exprNode.term = ast.IDRvalue()
            exprNode.term.path.append(temp)
            while self.current_token.tokentype == token.DOT:  
                self.__advance()
                exprNode.term.path.append(self.current_token)
                self.__eat(token.ID, 'expecting id')

    def __exprlist(self, valNode):  #append to args
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NIL, token.NEW, token.ID, token.LPAREN]
        if self.current_token.tokentype in types:
            valNode.args.append(self.__expr())
            while self.current_token.tokentype == token.COMMA:
                self.__advance()
                valNode.args.append(self.__expr())
    
    def __bexpr(self, boolNode): 
            if self.current_token.tokentype == token.NOT:
                boolNode.negated = True
                self.__advance()
                self.__bexpr(boolNode)
                self.__bexprt(boolNode)
            elif self.current_token.tokentype == token.LPAREN:
                self.__advance()
                boolNode.first_expr = ast.BoolExpr()
                self.__bexpr(boolNode.first_expr)
                self.__eat(token.RPAREN, 'expecting )')
                self.__bconnct(boolNode)
            else:
                boolNode.first_expr = self.__expr()
                self.__bexprt(boolNode)

    def __bexprt(self, boolNode):  
        boolrels = [token.EQUAL, token.LESS_THAN, token.GREATER_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrels:
            boolNode.bool_rel = self.current_token
            self.__boolrel()
            boolNode.second_expr = self.__expr()
            self.__bconnct(boolNode)
        else:
            self.__bconnct(boolNode)

    def __bconnct(self, boolNode):
        if self.current_token.tokentype == token.AND:
            boolNode.bool_connector = self.current_token
            self.__advance()
            boolNode.rest = ast.BoolExpr()
            self.__bexpr(boolNode.rest)
          #  if boolNode.rest.first_expr != None:
          #      boolNode.first_expr = boolNode.rest
                
        elif self.current_token.tokentype == token.OR:
            boolNode.bool_connector = self.current_token
            self.__advance()
            boolNode.rest = ast.BoolExpr()
            self.__bexpr(boolNode.rest)
          #  if boolNode.rest.first_expr != None:
          #      boolNode.first_expr = boolNode.rest
    
    def __boolrel(self):
        if self.current_token.tokentype == token.EQUAL:
            self.__advance()
        elif self.current_token.tokentype == token.LESS_THAN:
            self.__advance()
        elif self.current_token.tokentype == token.GREATER_THAN:
            self.__advance()
        elif self.current_token.tokentype == token.LESS_THAN_EQUAL:
            self.__advance()
        elif self.current_token.tokentype == token.GREATER_THAN_EQUAL:
            self.__advance()
        else:
            self.__eat(token.NOT_EQUAL, 'expecting boolrelation')
        