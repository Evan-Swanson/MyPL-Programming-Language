#!/usr/bin/python3
#
# Author:
# Assignment: 7
# Description:
# Simple script to execute the MyPL interpreter.
#----------------------------------------------------------------------
import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_parser as parser
import mypl_ast as ast
import mypl_type_checker as type_checker
import mypl_interpreter as interpreter
import sys

def main(filename):
    try:
        file_stream = open(filename, 'r')
        hw7(file_stream)
        file_stream.close()
    except FileNotFoundError:
        sys.exit('invalid filename %s' % filename)
    except error.MyPLError as e:
        file_stream.close()
        sys.exit(e)

def hw7(file_stream):
    the_lexer = lexer.Lexer(file_stream)
    the_parser = parser.Parser(the_lexer)
    stmt_list = the_parser.parse()
    the_type_checker = type_checker.TypeChecker()
    stmt_list.accept(the_type_checker)
    the_interpreter = interpreter.Interpreter()
    the_interpreter.run(stmt_list)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: %s file' % sys.argv[0])
    main(sys.argv[1])
