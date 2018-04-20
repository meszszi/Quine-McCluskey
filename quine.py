import string
import re
from collections import defaultdict
from itertools import combinations



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

        elif token == '1':
            stack += [True]

        elif token == '0':
            stack += [False]

        else:
            stack += [ values[token] ]


    return stack[0]



# Extracts all variables from expression and creates sorted list of them
def get_variables(rpn_expression):
    return sorted(set([token for token in rpn_expression if token not in '&|^>=~01']))



# Creates bitmask of a number
def get_bitmask(number, width):
    return bin(number)[2:].rjust(width, '0')



# Generates values dictionary for given variables set
def get_values(bitmask_number, variables):

    result = {}
    values = map(lambda x: x == '1', get_bitmask(bitmask_number, len(variables)))

    for variable, value in zip(variables, values):
        result[variable] = value

    return result



# Counts the number of '1' digits in binary representation of the number
def get_ones_number(bitmask_number):
    return bin(bitmask_number).count('1')



# Finds all value sets for wchich the expression evaluetes to True
def get_minterms(rpn_expression):

    variables = get_variables(rpn_expression)
    set_size = len(variables)
    upper_bound = 1 << set_size

    minterms = set()

    for bitmask_number in range(upper_bound):

        values = get_values(bitmask_number, variables)

        if evaluate(rpn_expression, values) == True:
            minterm_bitmask = 1 << bitmask_number
            minterms.add((minterm_bitmask, get_bitmask(bitmask_number, set_size)))

    return minterms, variables



# Merges two implicants (e.g. merge('100', '110') -> '1-0')
def merge_implicants(imp_a, imp_b):

    mask_a = imp_a[1]
    mask_b = imp_b[1]

    if len([_ for bit_a, bit_b in zip(mask_a, mask_b) if bit_a != bit_b]) != 1:
        return None

    result_mask = ""

    for bit_a, bit_b in zip(mask_a, mask_b):
        result_mask += bit_a if bit_a == bit_b else '-'

    return (imp_a[0] | imp_b[0]), result_mask



# Groups implicants until no other combination is possible
def get_prime_implicants(minterms):

    implicants = minterms
    prime_implicants = set()

    while True:

        used_implicants = set()
        new_implicants = set()

        for imp_a, imp_b in combinations(implicants, 2):

            merged = merge_implicants(imp_a, imp_b)

            if merged is not None:
                new_implicants.add(merged)
                used_implicants.add(imp_a[0])
                used_implicants.add(imp_b[0])

        for imp in implicants:
            if imp[0] not in used_implicants:
                prime_implicants.add(imp)

        implicants = new_implicants

        if len(implicants) == 0: # No other merge is possible
            break

    return prime_implicants



# Fids the smallest set of prime implicants that covers all minterms
def get_minterms_cover(minterms, prime_implicants):

    minterms_mask = 0
    for minterm, _ in minterms:
        minterms_mask |= minterm

    for i in range(1, len(minterms)+1):
        for primes_set in combinations(prime_implicants, i):

            primes_mask = 0
            for prime, _ in primes_set:
                primes_mask |= prime

            if primes_mask == minterms_mask:
                return primes_set

    return None



# Converts implicant into variables conjunction string
def implicant_to_string(implicant, variables):

    result = []
    for token, variable in zip(implicant[1], variables):
        if token == '1':
            result += [variable]
        elif token == '0':
            result += ['~' + variable]

    return ' & '.join(result)



# Converts set of implicants into logical expression string
def implicants_set_to_string(cover, variables):

    result = [implicant_to_string(implicant, variables) for implicant in cover]
    return ' | '.join(result)



# Simplifies logical expression with Quine-McCluskey algorithm
def simplify(expression):

    rpn_expression = to_rpn(expression)
    minterms, variables = get_minterms(rpn_expression)
    prime_implicants = get_prime_implicants(minterms)
    minterms_cover = get_minterms_cover(minterms, prime_implicants)
    return implicants_set_to_string(minterms_cover, variables)
