import mypl_token as token
import mypl_error as error

class Lexer(object):
    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream

    def __peek(self):
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol

    def __read(self):
        return self.input_stream.read(1)

    def next_token(self):
        symbol = self.__read()

        #check EOF
        if symbol == '':
            return token.Token('EOS', symbol, self.line, self.column)

        self.column += 1
        #check space and skip over
        if symbol == ' ':
            return self.next_token()
        
        #newline resets column and updates line
        if symbol == '\n':
            self.column = 0
            self.line += 1
            return self.next_token()

        #skip over comments and increment line at the end
        if symbol == '#':
            while self.__peek() != '\n':
                symbol += self.__read()
            self.__read()
            self.line += 1
            self.column = 0
            
            return self.next_token()

        
        
        
        #checking 1 or 2 symbol characters
        if symbol == '+':
            return token.Token('PLUS', symbol , self.line, self.column)
        elif symbol == '=':
            if self.__peek() == '=':
                symbol += self.__read()
                self.column += 1
                return token.Token('EQUAL', symbol , self.line, self.column - 1)
            return token.Token('ASSIGN', symbol , self.line, self.column)
        elif symbol == ',':
            return token.Token('COMMA', symbol , self.line, self.column)
        elif symbol == ':':
            return token.Token('COLON', symbol , self.line, self.column)
        elif symbol == '/':
            return token.Token('DIVIDE', symbol , self.line, self.column)
        elif symbol == '.':
            return token.Token('DOT', symbol , self.line, self.column)
        elif symbol == '>':
            if self.__peek() == '=':
                symbol += self.__read()
                self.column += 1
                return token.Token('GREATER_THAN_EQUAL', symbol , self.line, self.column - 1)
            return token.Token('GREATER_THAN', symbol , self.line, self.column)
        elif symbol == '<':
            if self.__peek() == '=':
                symbol += self.__read()
                self.column += 1
                return token.Token('LESS_THAN_EQUAL', symbol , self.line, self.column - 1)
            return token.Token('LESS_THAN', symbol , self.line, self.column)
        elif symbol == '(':
            return token.Token('LPAREN', symbol , self.line, self.column)
        elif symbol == ')':
            return token.Token('RPAREN', symbol , self.line, self.column)
        elif symbol == '-':
            return token.Token('MINUS', symbol , self.line, self.column)
        elif symbol == '%':
            return token.Token('MODULO', symbol , self.line, self.column)
        elif symbol == '*':
            return token.Token('MULTIPLY', symbol , self.line, self.column)
        elif symbol == ';':
            return token.Token('SEMICOLON', symbol , self.line, self.column)
        
        elif symbol == '!':
            if self.__peek() == '=':
                symbol += self.__read()
                self.column += 1
                return token.Token('NOT_EQUAL', symbol , self.line, self.column -1)
            else:
                raise error.MyPLError("Unexpected symbol '!'", self.line, self.column)

        #check constants
        #---------------

        #check leading 0
        if symbol == '0':
            if self.__peek().isnumeric():
                raise error.MyPLError("unexpected symbol '" + self.__peek() + "' ", self.line, self.column)

        #get int/float value
        if symbol.isnumeric():
            while self.__peek().isnumeric():
                symbol += self.__read()
                self.column += 1
            #check if poorly formed due to letters
            if self.__peek().isalpha():
                raise error.MyPLError("unexpected symbol '" + self.__peek() + "' ", self.line, self.column - (len(symbol) -1))
            #check if floating point
            if self.__peek() == '.':
                symbol += self.__read()
                self.column += 1
                if not self.__peek().isnumeric():
                    raise error.MyPLError('Missingn digit in float value', self.line, self.column - (len(symbol) -1))
                while self.__peek().isnumeric():
                    symbol += self.__read()
                    self.column += 1
                #check letters in float
                if self.__peek().isalpha():
                    raise error.MyPLError("unexpected symbol '" + self.__peek() + "' ", self.line, self.column - (len(symbol) -1))
                return token.Token('FLOATVAL', symbol, self.line, self.column - (len(symbol) -1))
            else:
                return token.Token('INTVAL', symbol, self.line, self.column - (len(symbol) - 1))

        #check if string value
        if symbol == '"':
            while self.__peek() != '"':
                if self.__peek() == '\n':
                    raise error.MyPLError('Newline in middle of string', self.line, self.column - (len(symbol) - 1))
                symbol += self.__read()
                self.column += 1
                if self.__peek() == '':
                    raise error.MyPLError('Missing " in string', self.line, self.column - (len(symbol) -1))
            #read the ending "
            self.__read()
            self.column += 1
            return token.Token('STRINGVAL', symbol[1:], self.line, self.column - (len(symbol)))

        #get a string of alphabet characters
        while self.__peek().isalpha() or self.__peek() == '_' or self.__peek().isnumeric():
            symbol += self.__read()
            self.column += 1

        #check specical words
        if symbol == 'bool':
            return token.Token('BOOLTYPE', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'int':
            return token.Token('INTTYPE', symbol, self.line, self.column - (len(symbol) - 1))
        elif symbol == 'float':
            return token.Token('FLOATTYPE', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'string':
            return token.Token('STRINGTYPE', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'struct':
            return token.Token('STRUCTTYPE', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'and':
            return token.Token('AND', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'or':
            return token.Token('OR', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'not':
            return token.Token('NOT', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'while':
            return token.Token('WHILE', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'do':
            return token.Token('DO', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'if':
            return token.Token('IF', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'then':
            return token.Token('THEN', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'else':
            return token.Token('ELSE', symbol, self.line, self.column - (len(symbol) - 1)) 
        elif symbol == 'elif':
            return token.Token('ELIF', symbol, self.line, self.column - (len(symbol) - 1))  
        elif symbol == 'end':
            return token.Token('END', symbol, self.line, self.column - (len(symbol) - 1))  
        elif symbol == 'fun':
            return token.Token('FUN', symbol, self.line, self.column - (len(symbol) - 1))  
        elif symbol == 'var':
            return token.Token('VAR', symbol, self.line, self.column - (len(symbol) - 1))  
        elif symbol == 'set':
            return token.Token('SET', symbol, self.line, self.column - (len(symbol) - 1))   
        elif symbol == 'return':
            return token.Token('RETURN', symbol, self.line, self.column - (len(symbol) - 1))  
        elif symbol == 'new':
            return token.Token('NEW', symbol, self.line, self.column - (len(symbol) - 1))    
        elif symbol == 'nil':
            return token.Token('NIL', symbol, self.line, self.column - (len(symbol) - 1))        
        #BOOL values  
        elif symbol == 'true':
            return token.Token('BOOLVAL', symbol, self.line, self.column - (len(symbol) - 1))          
        elif symbol == 'false':
            return token.Token('BOOLVAL', symbol, self.line, self.column - (len(symbol) - 1))      

        #identifiers
        if symbol[0].isalpha():
            return token.Token('ID', symbol, self.line, self.column - (len(symbol) -1))
        elif symbol[0] == '_':
            raise error.MyPLError('Poorly formed identifier', self.line, self.column - (len(symbol) -1))

    
        #unexpected char error
        raise error.MyPLError("Unexpected character(s): '" + symbol + "'", self.line, self.column - (len(symbol) -1))
