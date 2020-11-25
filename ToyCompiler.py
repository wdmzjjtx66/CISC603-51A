import sys

# ----------------------------------------------------------------------
#                          Part I - Lexer
# ----------------------------------------------------------------------

# Tokens
# Tokens that are used to identify and indicate type of characters in the
# input. END means we are at end of the input, no more left for our
# analysis
PLUS, MINUS, MUL, DIV = 'PLUS', 'MINUS', 'MUL', 'DIV'
L_PAR, R_PAR, INTEGER, END = '(', ')', 'INTEGER', 'END'


class Token(object):
    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        # print class in string format if needed in testing
        # e.g Token(INTEGER, 6), Token(PLUS, '+'), Token(L_PAR, '(')
        return 'Token({type}, {content})'.format(type=self.type, content=self.content)

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        # here text means input strings e.g. "3 - (5 * (4 // 2 + 100) + - 16)"
        self.text = text
        # position is a marker on the index of the input text we are currently processing
        self.position = 0
        # curr_char is the character that position point to in the text
        self.curr_char = self.text[self.position]

    def forward(self):
        # each time we call this method, we advance the index and character pointed to
        self.position += 1
        if self.position > len(self.text) - 1:
            # we have already reach the end of the file
            self.curr_char = None
        else:
            # update the current character
            self.curr_char = self.text[self.position]

    def get_integer(self):
        # get an integer from input text, could be multi-digits
        temp = 0
        while self.curr_char and self.curr_char.isdigit():
            temp = temp * 10 + int(self.curr_char)
            self.forward()
        return temp

    def skip_whitespace(self):
        # we need to skip whitespace in the input string
        while self.curr_char and self.curr_char.isspace():
            self.forward()

    def raise_error(self):
        raise Exception('Input character is invalid')

    def get_next_token(self):
        # this part is the implementation of tokenizer or lexer analysis
        # we just break down input text into tokens one by one
        while self.curr_char:

            if self.curr_char.isspace():
                self.skip_whitespace()
                continue

            if self.curr_char == '+':
                self.forward()
                return Token(PLUS, '+')

            if self.curr_char == '-':
                self.forward()
                return Token(MINUS, '-')

            if self.curr_char == '*':
                self.forward()
                return Token(MUL, '*')

            if self.curr_char == '/':
                self.forward()
                return Token(DIV, '/')

            if self.curr_char.isdigit():
                return Token(INTEGER, self.get_integer())

            if self.curr_char == '(':
                self.forward()
                return Token(L_PAR, '(')

            if self.curr_char == ')':
                self.forward()
                return Token(R_PAR, ')')

            # if the input is not one of the token we recognize, raise an error
            self.raise_error()

        # done processing the input, point at end of the text
        return Token(END, None)


# ----------------------------------------------------------------------
#                          Part II - Parser
# ----------------------------------------------------------------------


# following part we implement abstract syntax tree, each node in the tree is
# either an operator or an integer, we will remove parenthesis by add the
# content within the parenthesis in their order of they should be processed.

class AST(object):
    # this is the class derived from the most basic system object - object
    # this class is the parent class for the following detailed implementation
    pass


class UnaryOperator(AST):
    # first inheritance of base class AST - for unary operators "+-"
    def __init__(self, operator, expression):
        # token should represent one of the unary operators e.g. Token(PLUS, '+')
        self.token = self.operator = operator
        # according to our syntax, an expression follows an unary operator
        self.expression = expression


class BinaryOperator(AST):
    # second derived child class of AST - for binary operator "+-*/"
    def __init__(self, left, operator, right):
        # there should be 2 child nodes for a binary operator - left and right
        self.left = left
        self.token = self.operator = operator
        self.right = right


class Numbers(AST):
    # second derived child class, members are integer tokens like Token(INTEGER, 2)
    def __init__(self, token):
        self.token = token
        self.content = token.content


# this is the implementation of second part of compiler - parse the tokens from
# lexer and put them into AST which could be processed by the tree traversed order
class Parser(object):
    def __init__(self, lexer):
        # use the lexer help break the input string into token, here we process
        # one token at a time
        self.lexer = lexer
        self.curr_token = self.lexer.get_next_token()

    def ignore(self, token_type):
        # when we are processing a token, we should jump to the
        # next one in order to get next part to process. And when
        # ignore we should check if we are ignoring the correct
        # token, otherwise raise an error
        if self.curr_token.type == token_type:
            self.curr_token = self.lexer.get_next_token()
        else:
            self.raise_error()

    def factor(self):
        # this method is to put together tokens into 'factor' in
        # our syntax analysis
        token = self.curr_token
        if token.type == PLUS:
            self.ignore(PLUS)
            node = UnaryOperator(token, self.factor())
            return node
        elif token.type == MINUS:
            self.ignore(MINUS)
            node = UnaryOperator(token, self.factor())
            return node
        elif token.type == INTEGER:
            # we should add integer tokens directly
            self.ignore(INTEGER)
            return Numbers(token)
        elif token.type == L_PAR:
            # all tokens between parenthesis should be treated as
            # expression, we shall remove parenthesis also because
            # we won't need them in AST
            self.ignore(L_PAR)
            node = self.expression()
            self.ignore(R_PAR)
            return node

    def term(self):
        # same as factor function above, term in our syntax is just
        # two parts on the side of a "*/" operator
        node = self.factor()

        while self.curr_token.type == MUL or self.curr_token.type == DIV:
            token = self.curr_token
            if token.type == MUL:
                self.ignore(MUL)
            elif token.type == DIV:
                self.ignore(DIV)

            # construct a BinaryOperator, and we process the factor
            # on the right side further using factor() function
            node = BinaryOperator(left=node, operator=token, right=self.factor())

        return node

    def expression(self):
        # in our syntax, expression is the most outside pact, so
        # we should start from here. expression can be separated
        # by "+-" into two terms.
        node = self.term()

        while self.curr_token.type == PLUS or self.curr_token.type == MINUS:
            token = self.curr_token
            if token.type == PLUS:
                self.ignore(PLUS)
            elif token.type == MINUS:
                self.ignore(MINUS)

            # same as term, left child node is current node, then
            # recursively build right node of expression
            node = BinaryOperator(left=node, operator=token, right=self.term())

        return node

    def raise_error(self):
        raise Exception('Found a syntax error of input text')

    def parse(self):
        # build AST recursively, and return the root node of it
        # for interpreter to work on
        root = self.expression()
        # when we reach the end of the input test but
        # not given us END token, there must be an error
        if self.curr_token.type != END:
            self.raise_error()
        return root


# ----------------------------------------------------------------------
#                          Part III - INTERPRETER
# ----------------------------------------------------------------------



class NodeVisitor(object):
    # class we use to iterate AST we built from parser

    def visit(self, node):
        # specify the method name we should use depends on
        # the node type, kind of inheritance idea here
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.visit_error)
        return visitor(node)

    def visit_error(self, node):
        # if there is no such method, we should raise an error
        raise Exception('No such a method called visit_{}'.format(type(node).__name__))


# the implementation of our interpreter class, which takes
# AST built in parser and evaluate the input based on syntax
class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinaryOperator(self, node):
        # we should output result based on the binary operator
        # type
        if node.operator.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.operator.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.operator.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.operator.type == DIV:
            try:
                return self.visit(node.left) // self.visit(node.right)
            except ZeroDivisionError:
                print("The denominator should not be zero")
                sys.exit(1)

    def visit_Numbers(self, node):
        # if the node is an integer, just output the integer
        return node.content

    def visit_UnaryOperator(self, node):
        # if it is a unary operator, just output the expression
        # with the prefix unary operator
        op = node.operator.type
        if op == PLUS:
            return +self.visit(node.expression)
        elif op == MINUS:
            return -self.visit(node.expression)

    def interpret(self):
        # recursive evaluate the input by traverse the AST tree
        # with various visit method inherited from the base class
        tree = self.parser.parse()
        if not tree:
            return ''
        return self.visit(tree)


# ----------------------------------------------------------------------
#                          Part IV - Main Function
# ----------------------------------------------------------------------


def main():
    while True:
        try:
            text = input('calculator> ')
        except EOFError:
            break
        if not text:
            continue

        # calling lexer to break input into tokens
        lexer = Lexer(text)

        # calling parser to construct AST
        parser = Parser(lexer)

        # calling interpreter to do calculation using
        # AST
        interpreter = Interpreter(parser)
        re = interpreter.interpret()
        print ('result is: {re}'.format(re=re))


if __name__ == '__main__':
    main()