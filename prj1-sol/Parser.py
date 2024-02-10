import json
import re
import sys


# handle comments

class Parser:

    def __init__(self, input_string):
        self.tokens = []
        self.tokenize(self.remove_comments_whitespace(input_string))
        self.current_token = None
        self.index = -1
        self.next_token()
        self.result = []

    def next_token(self):
        self.index += 1
        if not self.index >= len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, expected_token, expected_token_alternative=''):
        if self.current_token == expected_token:
            self.next_token()

        elif self.current_token == expected_token_alternative:
            self.next_token()

        else:
            raise SyntaxError(f"Expected {expected_token}, got {self.current_token}")

    def parse_program(self):
        while self.current_token:
            aux = self.parse_expression()
            self.result.append(aux)

        return self.result

    def parse_expression(self):
        if self.current_token == "[":
            return self.parse_list()
        elif self.current_token == "{":
            return self.parse_tuple()
        elif self.current_token == "%{":
            return self.parse_dictionary()
        elif self.current_token in ["true", "false"]:
            return self.parse_boolean()
        elif len(list(filter(None, re.findall(":*[a-zA-Z_][a-zA-Z0-9_]*", self.current_token)))) != 0:
            return self.parse_atom()
        elif len(list(filter(None, re.findall("[0-9_]*", self.current_token)))) != 0:
            return self.parse_number()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def parse_list(self):
        value = []
        self.match("[")
        while self.current_token != "]":
            value.append(self.parse_expression())
            if self.current_token == ",":
                self.match(",")
        self.match("]")
        return {"%k": "list", "%v": value}

    def parse_tuple(self):
        value = []
        self.match("{")
        while self.current_token != "}":
            value.append(self.parse_expression())
            if self.current_token == ",":
                self.match(",")
        self.match("}")
        return {"%k": "tuple", "%v": value}

    def parse_dictionary(self):
        value = []
        self.match("%{")
        while self.current_token != "}":
            value.append(self.parse_key_pair())
            if self.current_token == ",":
                self.match(",")
        self.match("}")
        return {"%k": "map", "%v": value}

    def parse_key_pair(self):
        key = self.parse_expression()
        self.match(":", "=>")
        value = self.parse_expression()
        return [key,value]

    def parse_boolean(self):
        bool = self.current_token
        self.match(self.current_token)
        return {"%k": "bool", "%v": bool}

    def parse_atom(self):
        # handle special cases. what about just charaters, are they not allowed eg: a, b etc
        atom = self.current_token
        self.match(self.current_token)
        if not re.search("truefalse", atom):
            if atom[0] != ':':
                return {"%k": "atom", "%v": ':' + atom}
            else:
                return {"%k": "atom", "%v": atom}

    def parse_number(self):
        number = self.current_token
        self.match(self.current_token)
        if not re.search("[0-9_]*_$", number):
            string = number.replace('_', '')
            return {"%k": "int", "%v": int(number)}
        else:
            raise SyntaxError(f"Bad integer value:  {number}")

    def tokenize(self, string):
        pattern = "%{|{|[0-9_]*|:[a-zA-Z_][a-zA-Z0-9_]*|}|,|\[|\]|true|false|[a-zA-Z_][a-zA-Z0-9_]*|=>|:|\\n"
        self.tokens = list(filter(None, re.findall(pattern, string)))

    def remove_comments_whitespace(self, input_string):
        input_string = re.sub('#.*$', '', input_string, flags=re.MULTILINE)
        input_string = input_string.replace('\n', ' ')
        print(input_string)
        return (input_string)


# input_string = sys.stdin.read()
p = Parser("%{ [:a, 22] => { [1, 2, 3], :x },\n   x: [99, %{ a: 33 }]\n}\n\n{ [1, 2], {:a, 22}, %{ a: 99, :b => 11} }\n\n[ {1, 2}, %{[:x] => 33, b: 44}, :c, [], [:d, 55] ]")
# p = Parser("%{a:5}")
json_output = json.dumps(p.parse_program(), indent=2)
print(json_output)
