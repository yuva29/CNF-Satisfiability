# -*- coding: cp1252 -*-
import sys
import json
EXPECTED_ARGS_LEN = 3
UNARY_LEN = 2
BINARY_LEN = 3
operators = ["and", "or", "not", "implies", "iff"]

"""
To print error messages
"""
def print_error_msg(msg):
    print "ERROR : ",msg, "\n"
    return "exit"
    #sys.exit(0)

"""
To remove bicondition from the given sentence
"""
def remove_bicondition(sentence):
    result = []
    if not sentence: return print_error_msg("Invalid sentence format")
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op: #Unary operator
            if len(sentence) != UNARY_LEN: return print_error_msg("Invalid sentence format")
            expr1 = remove_bicondition(sentence[1])
            if expr1 == "exit": return "exit"
            result = [op, expr1]
        elif op in operators: #Binary operator
            if "iff" == op:
                if len(sentence) != BINARY_LEN: return print_error_msg("Invalid sentence format")
                expr1 = remove_bicondition(sentence[1])
                if expr1 == "exit": return "exit"
                expr2 = remove_bicondition(sentence[2])
                if expr2 == "exit": return "exit"
                result = ["and", ["implies", expr1, expr2], ["implies", expr2, expr1]]
            else:
                result.append(op)
                for temp in sentence[1:]:
                    temp_expr = remove_bicondition(temp)
                    if temp_expr == "exit": return "exit"
                    result.append(temp_expr)
        else:
            return print_error_msg("Invalid sentence format")
    elif isinstance(sentence, str): ## Error
        if sentence in operators: return print_error_msg("Invalid sentence format")
        result = sentence
    else:
        return print_error_msg("Invalid sentence format")
    return result

"""
To remove implications from the given sentence
"""
def remove_implications(sentence):
    result = []
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op: #Unary operator
            expr1 = remove_implications(sentence[1])
            result = [op, expr1]
        else: #Binary operator
            if "implies" == op:
                if len(sentence) != BINARY_LEN: return print_error_msg("Invalid sentence format")
                expr1 = remove_implications(sentence[1])
                expr2 = remove_implications(sentence[2])                
                result = ["or",["not", expr1], expr2]
            else:
                result.append(op)
                for temp in sentence[1:]:
                    temp_expr = remove_implications(temp)
                    result.append(temp_expr)   
    elif isinstance(sentence, str): ## Error
        result = sentence
    else:
        return print_error_msg("Invalid sentence format")
    return result

"""
To move negations inward in the given sentence
"""
def move_not_inward(sentence):
    result = []
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op: #Unary operator
            inner_sentence = sentence[1] #could be a symbol or sentence
            if isinstance(inner_sentence, str): # ["not", P]
                result = [op, inner_sentence]
            else:
                inner_op = inner_sentence[0]
                if "not" == inner_op:
                    expr1 = move_not_inward(inner_sentence[1])
                    result = expr1 # not, not gets cancelled
                else:
                    if "and" == inner_op:
                        result.append("or")
                    elif "or" == inner_op:
                        result.append("and")
                    for temp in inner_sentence[1:]:
                        temp_expr = move_not_inward([op, temp])
                        result.append(temp_expr)
        else: #Binary operator
            result.append(op)
            for temp in sentence[1:]:
                temp_expr = move_not_inward(temp)
                result.append(temp_expr)                       
    elif isinstance(sentence, str):
        result = sentence
    else:
        return print_error_msg("Invalid sentence format")
    return result

"""
To distribute OR over the sentence
"""
def distribute_or(sentence1, sentence2):
    result = []
    if isinstance(sentence1, list) and sentence1[0] == "and" :
        result.append("and")
        for temp in sentence1[1:]:
            temp_expr = distribute_or(temp, sentence2)
            result.append(temp_expr)
    elif isinstance(sentence2, list) and sentence2[0] == "and" :
        result.append("and")
        for temp in sentence2[1:]:
            temp_expr = distribute_or(sentence1, temp)
            result.append(temp_expr)
    else:
        result = ["or", sentence1, sentence2]
    return result

"""
To apply associativity over the given sentence
"""
def distribute_or_over_and(sentence):
    result = []
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op:
            result = ["not", sentence[1]]
        elif "and" == op:
            result.append("and")
            for temp in sentence[1:]:
                temp_expr = distribute_or_over_and(temp)
                result.append(temp_expr)
        elif "or" == op: #actual distribution happens here
            temp1 = sentence[1]
            for temp2 in sentence[2:]:
                temp1 = distribute_or(temp1, temp2)
            result = temp1
        else:
            return print_error_msg("Invalid sentence format")
    elif isinstance(sentence, str):
        result = sentence
    else:
        return print_error_msg("Invalid sentence format")
    return result

"""
To remove duplicates from the given sentence
"""
def remove_duplicates(sentence):
    result = []
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op: #Unary operator
            expr1 = remove_duplicates(sentence[1])
            result = [op, expr1]
        else: #Binary operator
            result.append(op)
            for temp in sentence[1:]:
                temp_expr = remove_duplicates(temp)
                temp_sentence = sentence
                temp_sentence.remove(temp)
                if temp_expr not in result:
                    result.append(temp_expr)
            if len(result) == 2 and result[0] == op:
                result = result[1]
    elif isinstance(sentence, str): 
        result = sentence
    else: ## Error
        return print_error_msg("Invalid sentence format")
    return result

"""
To sort the literals in the alphabetical order. Helps to remove duplicates
"""
def sort_literals(sentence):
    result = []
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op: #Unary operator
            expr1 = sort_literals(sentence[1])
            result = [op, expr1]
        else: #Binary operator
            is_literals_string = 1
            result.append(op)
            for temp in sentence[1:]:
                temp_expr = sort_literals(temp)
                result.append(temp_expr)
                if not isinstance(temp_expr, str): is_literals_string = 0
            if 1 == is_literals_string:
                literals = sorted(sentence[1:])
                result = []
                result.append(op)
                for temp in literals:
                    result.append(temp)
    elif isinstance(sentence, str): 
        result = sentence
    else: ## Error
        return print_error_msg("Invalid sentence format")
    return result

"""
To flatten the given sentence. Combines nearby 'and's and 'or's together
"""
def flatten_or_and(sentence):
    result = []
    if isinstance(sentence, list):
        op = sentence[0]
        if "not" == op: #Unary operator
            result.append(op)
            expr1 = flatten_or_and(sentence[1])
            result.append(expr1)
        else: #Binary operator
            #result.append(op)
            result = flatten_or_and(sentence[1])
            #if isinstance(result, list) and "not" == result[0]:
                #result = [result]
            for temp in sentence[2:]:
                temp_expr = []
                temp_expr = flatten_or_and(temp)
                #print "Result:", result, "Temp expr:", temp_expr
                if result != temp:
                    if isinstance(result,list) and isinstance(temp_expr,list) and ((result[0] == temp_expr[0] and result[0] == op) or "not" == temp_expr[0]):
                        if temp_expr not in result:
                            if "not" != temp_expr[0]:
                                for exprs in temp_expr[1:]:
                                    result.append(exprs)
                            else:
                                result = [result, temp_expr]
                    elif isinstance(result, list) and result[0] == op:
                        if temp_expr not in result:
                            result.append(temp_expr)
                    elif isinstance(temp_expr, list) and temp_expr[0] == op:
                        temp_expr.append(result)
                        result = temp_expr
                    else:
                        result= [result, temp_expr]
                    if op != result[0]: result.insert(0,op)

                    temp = []
                    temp.append(op)
                    for x in result[1:]:
                        if isinstance(x, list) and x[0] == op:
                            for y in x[1:]:
                                temp.append(y)
                        else:
                            temp.append(x)
                    result = temp
            
    elif isinstance(sentence, str): 
        result = sentence
    else: ## Error
        return print_error_msg("Invalid sentence format")
    return result

"""
To convert the given input sentence to CNF 
"""
def convert_to_cnf(line):
    try:
        sentence = eval(line)
    except:
        if isinstance(line, str) and len(line) == 1: return line
        print_error_msg("Invalid sentence format")
        return "Invalid"

    sentence = remove_bicondition(sentence)
    if sentence == "exit": return "Invalid"
    
    print "After removing bicondition :", sentence, "\n"
    sentence = remove_implications(sentence)
    if sentence == "exit": return "Invalid"

    print "After removing implications :", sentence, "\n"
    sentence = move_not_inward(sentence)
    if sentence == "exit": return "Invalid"
    
    print "After moving negations :", sentence , "\n"   
    # since it the sentences are in propositional logic form,
    # variable standardization, skolemization and dropping universal quantifier is not required
    sentence = distribute_or_over_and(sentence)
    if sentence == "exit": return "Invalid"
    
    print "After distributing OR over AND :", sentence, "\n"
    sentence = sort_literals(sentence)
    if sentence == "exit": return "Invalid"
    
    print "After sorting literals :", sentence, "\n"
    sentence = flatten_or_and(sentence)
    if sentence == "exit": return "Invalid"
    
    print "After flattening :", sentence, "\n"
    sentence = remove_duplicates(sentence)
    if sentence == "exit": return "Invalid"
    
    print "After removing duplicates :", sentence, "\n"
    print "\n"
    return sentence

"""
To parse the input file
"""
def parse_file(input_file):
    num_sentences = int(input_file.readline())
    while(num_sentences > 0):
        line = input_file.readline()
        cnf = convert_to_cnf(line)
        json.dump(cnf, cnf_file)
        cnf_file.write("\n")
        num_sentences = num_sentences-1
    return cnf

cnf_file = open('sentences_CNF.txt', 'w+')

"""
Command line argument validation
"""
if EXPECTED_ARGS_LEN == len(sys.argv):
    if '-i' != sys.argv[1]:
        print "Malformed command. Usage : python CNFconverter.py –i inputfilename"
    else:
        try:
            """ READ THE INPUT FILE """
            file_handler = open(sys.argv[2],'r')
            parse_file(file_handler)

        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
else:
    print "Malformed command. Usage : python CNFconverter.py -i inputfilename"
    exit
