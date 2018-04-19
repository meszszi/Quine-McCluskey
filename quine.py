import string
import re
from collections import defaultdict

# Checks if given list of tokens represents syntactically correct logical expression
def check_syntax(expression_tokens):

    binary_operators = '&|^=>'
    brackets_counter = 0
    state = 2

    # State 1:
    #   - binary operator -> goes to state 2
    #   - closing bracket -> stays in state 1
    #   - other -> incorrect syntax

    # State 2:
    #   - variable -> goes to state 1
    #   - opening bracket or negation ('~') -> stays in state 2
    #   - other -> incorrect syntax


    for token in expression_tokens:

        if state == 1:

            if token in binary_operators:
                state = 2
                continue

            if token == ')':
                brackets_counter -= 1

                if brackets_counter < 0:
                    return False

                continue

            return False


        elif state == 2:

            if token == '(':
                brackets_counter += 1
                continue

            if token == '~':
                continue

            if token == ')' or token in binary_operators:
                return False

            state = 1


    return state == 1 and brackets_counter == 0



# Converts given string into postfix-syntax representation
def to_rpn(expression):

    # '0' and '1' are also treated as variables in this context
    variable_characters = string.ascii_letters + string.digits
    operator_characters = '&|^>=~()'

    # Splits expression into list of single entries (variables or operators)
    tokens = re.findall('[' + variable_characters + ']+|[' + operator_characters + ']', expression)

    if not check_syntax(tokens):
        return 'nie jest dobrze :C'

    # All considered operators except for '~' are left-to-right associative
    associativity = defaultdict(lambda: 'left')
    associativity['~'] = 'right'

    precedence = {'(': 6,
                  ')': 6,
                  '~': 5,
                  '&': 3,
                  '|': 2,
                  '^': 4,
                  '>': 1,
                  '=': 0}

    stack = []
    queue = []

    # Main loop converting expression to RPN format (with shutting-yard algorithm)
    for token in tokens:

        # Enqueues all variables
        if token not in operator_characters:
            queue.append(token)
            continue

        if token == '(':
            stack.append(token)
            continue

        if token == ')':

            while stack[-1] != '(':
                queue.append(stack.pop())

            stack.pop()
            continue

        # Other operator-related cases
        while (len(stack) > 0 and
               stack[-1] != '(' and (
               precedence[stack[-1]] > precedence[token] or
               (precedence[stack[-1]] == precedence[token] and associativity[stack[-1]] == 'left'))):

            queue.append(stack.pop())

        stack.append(token)


    while len(stack) > 0:
        queue.append(stack.pop())

    return queue



# Evaluates expression's value
def evaluate(rpn_expression, values):

    stack = []

    for token in rpn_expression:

        if token == '=':
            stack = stack[:-2] + [ stack[-2] == stack[-1] ]

        elif token == '>':
            stack = stack[:-2] + [ (not stack[-2]) or stack[-1] ]

        elif token == '&':
            stack = stack[:-2] + [ stack[-2] and stack[-1] ]

        elif token == '|':
            stack = stack[:-2] + [ stack[-2] or stack[-1] ]

        elif token == '^':
            stack = stack[:-2] + [ stack[-2] != stack[-1] ]

        elif token == '~':
            stack = stack[:-1] + [ not stack[-1] ]

        else:
            stack += [ values[token] ]


    return stack[0]



# Creates bitmask of a number
def get_bitmask(number, width):
    return bin(number)[2:].rjust(width, '0')



# Generates values dictionary for given variables set
def get_values(bitmask_number, variables):

    result = {}
    values = map(lambda x : x == '1', get_bitmask(bitmask_number, len(variables)))

    for variable, value in zip(variables, values):
        result[variable] = value

    return result



# Counts the number of '1' digits in binary representation of the number
def get_ones_number(bitmask_number):
    return bin(bitmask_number).count('1')



# Finds all value sets for wchich the expression evaluetes to True
def find_all_minterms(rpn_expression):

    variables = set([token for token in rpn_expression if token not in '&|^>=~'])
    upper_bound = 1 << len(variables)

    minterms = defaultdict(lambda: [])

    for bitmask_number in range(upper_bound):

        values = get_values(bitmask_number, variables)

        if evaluate(rpn_expression, values) == True:
            minterms[get_ones_number(bitmask_number)] += [values]

    return minterms
