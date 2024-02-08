import re


# handle comments

class Parser:

    def __init__(self, input_string):
        self.tokens = []
        self.tokenize(input_string)
        self.current_token = None
        self.index = -1
        self.next_token()
        self.result = "["
        self.inside = False

    def next_token(self):
        self.index += 1
        if not self.index >= len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, expected_token, expected_token_alternative=None):
        if self.current_token == expected_token:
            self.next_token()

        elif self.current_token == expected_token_alternative:
            self.next_token()

        else:
            raise SyntaxError(f"Expected {expected_token}, got {self.current_token}")

    def parse_program(self):
        while self.current_token:
            self.parse_expression()
        self.result += ']'

    def parse_expression(self):
        if self.current_token == "[":
            self.parse_list()
        elif self.current_token == "{":
            self.parse_tuple()
        elif self.current_token == "%{":
            self.parse_dictionary()
        elif self.current_token in ["true", "false"]:
            self.parse_boolean()
        elif len(list(filter(None, re.findall(":[a-zA-Z_][a-zA-Z0-9_]*", self.current_token)))) != 0:
            self.parse_atom()
        elif len(list(filter(None, re.findall("[0-9_]*", self.current_token)))) != 0:
            self.parse_number()
        elif self.current_token == "#":
            while self.current_token != '\n':
                self.next_token()
            self.match('\n')
        elif self.current_token == '\n':
            self.next_token()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def parse_list(self):
        self.inside = True
        self.match("[")
        self.result += '{ "%k": "list", "%v": ['
        if self.current_token != "]":
            self.parse_expression()
            while self.current_token == ",":
                self.result += ','
                self.match(",")
                self.parse_expression()
        self.result += '] }'
        self.inside = False
        self.match("]")

    def parse_tuple(self):
        self.inside = True
        self.match("{")
        self.result += '{ "%k": "tuple", "%v": ['
        if self.current_token != "}":
            self.parse_expression()
            while self.current_token == ",":
                self.result += ','
                self.match(",")
                self.parse_expression()
        self.result += '] }'
        self.inside = False
        self.match("}")

    def parse_dictionary(self):
        self.inside = True
        self.match("%{")
        self.result += '{ "%k": "map", "%v": ['
        if self.current_token != "}":
            self.parse_key_pair()
            while self.current_token == ",":
                self.result += ','
                self.match(",")
                self.parse_key_pair()
        self.result += '] }'
        self.inside = False
        self.match("}")

    def parse_key_pair(self):
        self.result += '['
        self.parse_expression()
        self.result += ','
        self.match(":", "=>")
        self.parse_expression()
        self.result += ']'

    def parse_boolean(self):
        self.result += '{ "%k": "bool", "%v": ' + self.current_token + ' }'
        if not self.inside:
            self.result += ','
        self.match(self.current_token)

    def parse_atom(self):
        # handle special cases. what about just charaters, are they not allowed eg: a, b etc
        if not re.search("truefalse", self.current_token):
            if self.current_token[0] != ':':
                self.result += '{ "%k": "atom", "%v": "' + ':' + self.current_token + '" }'
            else:
                self.result += '{ "%k": "atom", "%v": "' + self.current_token + '" }'

            if not self.inside:
                self.result += ','
            self.match(self.current_token)

    def parse_number(self):
        if not re.search("[0-9_]*_$", self.current_token):
            self.result += '{ "%k": "int", "%v": ' + self.current_token + ' }'
            self.match(self.current_token)

            if not self.inside:
                self.result += ','

        else:
            raise SyntaxError(f"Bad integer value:  {self.current_token}")

    def tokenize(self, string):
        pattern = "%{|{|[0-9_]*|:[a-zA-Z_][a-zA-Z0-9_]*|}|,|\[|\]|true|false|[a-zA-Z_][a-zA-Z0-9_]*|=>|:|\\n"
        self.tokens = list(filter(None, re.findall(pattern, string)))


p = Parser("123_456_789\n1_2_3")
p.parse_program()
print(p.result)
