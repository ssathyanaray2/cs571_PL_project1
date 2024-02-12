import json
import re
import sys


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
        elif re.match("\d+(_\d+)*", self.current_token):
            return self.parse_number()
        elif re.match(":[a-zA-Z_][a-zA-Z0-9_]*", self.current_token) or re.match("[a-zA-Z_][a-zA-Z0-9_]*",
                                                                                 self.current_token):
            return self.parse_atom()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def parse_list(self):
        value = []
        self.match("[")
        if self.current_token != "]":
            value.append(self.parse_expression())
            while self.current_token == ",":
                self.match(",")
                value.append(self.parse_expression())
        self.match("]")
        return {"%k": "list", "%v": value}

    def parse_tuple(self):
        value = []
        self.match("{")
        if self.current_token != "}":
            value.append(self.parse_expression())
            while self.current_token == ",":
                self.match(",")
                value.append(self.parse_expression())
        self.match("}")
        return {"%k": "tuple", "%v": value}

    def parse_dictionary(self):
        value = []
        self.match("%{")
        if self.current_token != "}":
            value.append(self.parse_key_pair())
            while self.current_token == ",":
                self.match(",")
                value.append(self.parse_key_pair())
        self.match("}")
        return {"%k": "map", "%v": value}

    def parse_key_pair(self):
        key = self.parse_expression()
        if self.current_token == '=>' :
            self.match("=>")
        value = self.parse_expression()
        return [key, value]

    def parse_boolean(self):
        b = self.current_token
        self.match(self.current_token)
        if b=='false':
            b = False 
        else:
            b = True
        return {"%k": "bool", "%v": b}

    def parse_atom(self):
        # handle special cases. what about just charaters, are they not allowed eg: a, b etc
        atom = self.current_token
        self.match(self.current_token)
        if atom[-1] != ':':
            return {"%k": "atom", "%v": atom}
        else:
            return {"%k": "atom", "%v": ':'+atom[:-1]}

    def parse_number(self):
        number = self.current_token
        self.match(self.current_token)
        if not re.search("[0-9_]*_$", number):
            string = number.replace('_', '')
            return {"%k": "int", "%v": int(number)}
        else:
            raise SyntaxError(f"Bad integer value:  {number}")

    def tokenize(self, string):
        
        pattern = "%{|{|[0-9_]*|:[a-zA-Z_][a-zA-Z0-9_]*|}|,|\[|\]|true|false|[a-zA-Z_][a-zA-Z0-9_]*:|=>|\\n"
        self.tokens = list(filter(None, re.findall(pattern, string)))

    def remove_comments_whitespace(self, input_string):
        input_string = re.sub('#.*$', '', input_string, flags=re.MULTILINE)
        input_string = input_string.replace('\n', ' ')
        return (input_string)


def main():
    input_string = sys.stdin.read()
    p = Parser(input_string)
    # p = Parser("false\n\ntrue\n\ntrue false")
    json_output = json.dumps(p.parse_program(), indent=2)
    print(json_output)
    return json_output


if __name__ == "__main__":
    main()
