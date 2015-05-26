# -*- coding: cp1252 -*-
import sys
import json
from compiler.ast import flatten
EXPECTED_ARGS_LEN = 3
assignment = {}
symbols = []
operators = ['and', 'or', 'not']

"""
To print error messages
"""
def print_error_msg(msg):
    print "ERROR : ",msg, "\n"
    exit

"""
To find the pure symbol from given CNF
"""
def find_pure_symbol(cnf_sentence):
    if not cnf_sentence: return None, None
    
    for s in symbols:
        found_pos, found_neg = False, False
        if isinstance(cnf_sentence, list):
            op = cnf_sentence[0]
            if "and" == op:
                clauses = cnf_sentence[1:]
                for c in clauses:
                    if isinstance(c, list) and c[0] == "not":
                       if not found_neg and s == c[1]: found_neg = True
                    elif isinstance(c, list):
                        if not found_pos and s in c: found_pos = True
                        if not found_neg and ["not",s] in c: found_neg = True
                    else:
                        if not found_pos and s == c: found_pos = True
            elif "or" == op:
                if not found_pos and s in cnf_sentence: found_pos = True
                if not found_neg and ["not",s] in cnf_sentence: found_neg = True
            elif "not" == op:
                if not found_neg and ["not",s] == cnf_sentence: found_neg = True
        elif isinstance(cnf_sentence, str):
            if not found_pos and s == cnf_sentence: found_pos = True   
        if found_pos != found_neg: return s, found_pos
    return None, None


"""
To find the unit clause from given CNF
"""
def find_unit_clause(cnf_sentence):
    if not cnf_sentence: return None, None

    for s in symbols:
        if isinstance(cnf_sentence, list):
            if "not" == cnf_sentence[0] and s == cnf_sentence[1]: return s, False
            elif "and" == cnf_sentence[0]: # or cannot occur here
                clauses = cnf_sentence[1:]
                for clause in clauses:
                    if isinstance(clause, str) and clause == s:
                        return clause, True
                    elif isinstance(clause, list) and clause[0] == "not" and clause[1] == s:
                        return clause[1], False
        elif isinstance(cnf_sentence, str) and s == cnf_sentence: return cnf_sentence, True
    return None, None

"""
To check whether the given clause is satisfiable based on the truth assignments so far
"""
def is_true(clause):
    if isinstance(clause, str):
        if clause in assignment: return assignment[clause]
        else: return None
        
    #list
    op = clause[0]
    literals = clause[1:]

    if "and" == op:
        result = True
        for literal in literals:
            p = is_true(literal)
            if p == False: return False
            if p == None: result = None
        return result
    elif "or" == op:
        result = False
        for literal in literals:
            p = is_true(literal)
            if p == True: return True
            if p == None: result = None
        return result
    elif "not" == op:
        p = is_true(clause[1])
        if p == None: return None
        else: return not p        

"""
To check whether the given CNF is satisfiable based on truth assignments
"""
def is_satisfiable(cnf_sentence):
    if not cnf_sentence: return None
    
    if isinstance(cnf_sentence, list):
        if cnf_sentence[0] == "and":
            clauses = cnf_sentence[1:]
            for c in clauses:
                val = is_true(c)
                if val == False or val == None: return val
            return True
        else: #or
            return is_true(cnf_sentence)
    else: #str
        return is_true(cnf_sentence)

"""
DPLL implementation to solve SAT problem
"""
def DPLL(cnf):
    """for key, value in assignment.items():
        print key, value"""
    #print "Satisfiability check:", is_satisfiable(cnf)
    if is_satisfiable(cnf):
        return True
    elif symbols:
        p, value = find_pure_symbol(cnf)
        #print p, value
        if p:
            symbols.remove(p)
            assignment[p] = value
            return DPLL(cnf)
        else:
            p, value = find_unit_clause(cnf)
            #print "Unit Clause:", p, value
            if p:
                symbols.remove(p)
                assignment[p] = value
                return DPLL(cnf)
            else:
                sym = symbols.pop()
                assignment[sym] = True
                if not DPLL(cnf):
                    assignment[sym] = False
                    return DPLL(cnf)
                else: return True
    return False

"""
To find all the possible symbols/literals from given CNF
"""
def find_symbols(cnf):
    if not cnf: return
    if isinstance(cnf, list):
        op = cnf[0]
        if "and" == op:
            for clause in cnf[1:]:
                find_symbols(clause)
        elif "or" == op:
            for literal in cnf[1:]:
                find_symbols(literal)
        elif "not" == op:
            if cnf[1] not in symbols: symbols.append(cnf[1])
    elif isinstance(cnf, str):
        if cnf not in symbols: symbols.append(cnf)
    else:
        print_error_msg("Invalid CNF format")
    return

"""
To parse the given CNF file
"""
def parse_file(input_file):
    num_sentences = int(input_file.readline())
    while(num_sentences > 0):
        line = input_file.readline()
        print "Input CNF:", eval(line)
        assignment.clear()
        del symbols[:]
        find_symbols(eval(line))
        print "Symbols:", symbols
        result = DPLL(eval(line))

        truth_assignments = []
        truth_assignments.append(str(result).lower())
        if result:
            for key,value in assignment.items():
                temp =str(key)+"="+str(value).lower()
                truth_assignments.append(temp)
            for sym in symbols:
                temp = str(sym)+"=false"
                truth_assignments.append(temp)
        
        json.dump(truth_assignments, cnf_file)
        cnf_file.write("\n")
        
        print "Truth Assignment", truth_assignments
        print "\n"
        
        num_sentences = num_sentences - 1

cnf_file = open('CNF_satisfiability.txt', 'w+')

"""
Validates the input
"""
if EXPECTED_ARGS_LEN == len(sys.argv):
    if '-i' != sys.argv[1]:
        print "Malformed command. Usage : python DPLL.py –i inputfilename"
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
    print "Malformed command. Usage : python DPLL.py -i inputfilename"
    exit
    
