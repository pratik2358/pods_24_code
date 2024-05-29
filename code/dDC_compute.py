import numpy as np
from fractions import Fraction
import pandas as pd
from math import comb
import copy
import itertools


class Node:
    """Definition of a simple node to be used in a dD circuit"""
    id_counter = 0
    def __init__(self, gate = None, node_type = 'leaf', children=None, value=None, evaluated=False):
        self.gate = gate
        self.id = Node.id_counter
        Node.id_counter += 1
        self.node_type = node_type
        self.children = children if children is not None else []
        self.value = value
        self.evaluated = evaluated

    def delete_children(self, numbers):
        if len(numbers) == 1:
            removed = self.children.pop(numbers[0])
        else:
            for i in range(2):
                removed = self.children.pop(0)
    def reset(self):
        Node.id_counter = 0

def parse(exp, exps, nodes):
    Node().reset()
    if Node.id_counter in nodes:
        Node.id_counter = max(nodes)+1
    if exp in exps:
        if exps[exp].id not in nodes:
            nodes.append(exps[exp].id)
        return exps[exp]
    else:
        if isinstance(exp, str):
            if Node.id_counter in nodes:
                Node.id_counter = max(nodes)+1
                nodes.append(copy.deepcopy(Node.id_counter))
                exps[exp] = Node(exp, 'leaf')
            else:
                nodes.append(copy.deepcopy(Node.id_counter))
                exps[exp] = Node(exp, 'leaf')
        elif isinstance(exp, tuple):
            operation, *operands = exp
            if Node.id_counter in nodes:
                Node.id_counter = max(nodes)+1
                nodes.append(copy.deepcopy(Node.id_counter))
                exps[exp] = Node(exp, operation)
            else:
                nodes.append(copy.deepcopy(Node.id_counter))
                exps[exp] = Node(exp, operation)
            for operand in operands:
                if operand not in exps:
                    if Node.id_counter in nodes:
                        Node.id_counter = max(nodes)+1
                        nodes.append(copy.deepcopy(Node.id_counter))
                        exps[operand] = parse(operand, exps, nodes)
                    else:
                        nodes.append(copy.deepcopy(Node.id_counter))
                        exps[operand] = parse(operand, exps, nodes)
                    exps[exp].children.append(exps[operand])
                else:
                    exps[exp].children.append(exps[operand])
        return exps[exp]
    
def compute(node_input, v_v_pair = {}):
    node = copy.deepcopy(node_input)
    if node.node_type == 'leaf':
        if not node.evaluated:
            node.value = v_v_pair[node.gate]
            node.node_type = 'constant'
            node.evaluated = True
            node.gate = None
        else:
            pass
    elif node.node_type == 'NOT':
        if not node.evaluated:
            if not node.children[0].evaluated:
                node.children[0] = compute(node.children[0], v_v_pair)
            node.value = bool(1 - node.children[0].value)
            node.node_type = 'constant'
            node.evaluated = True
            node.gate = None
        else:
            pass
    elif node.node_type == 'OR':
        if not node.evaluated:
            if not node.children[0].evaluated:
                node.children[0] = compute(node.children[0], v_v_pair)
            if not node.children[1].evaluated:
                node.children[1] = compute(node.children[1], v_v_pair)
            if node.children[0].value or node.children[1].value:
                node.value = True
                node.node_type = 'constant'
                node.evaluated = True
                node.gate = None
            else:
                node.value = False
                node.node_type = 'constant'
                node.evaluated = True
                node.gate = None
    elif node.node_type == 'AND':
        if not node.evaluated:
            if not node.children[0].evaluated:
                node.children[0] = compute(node.children[0], v_v_pair)
            if not node.children[1].evaluated:
                node.children[1] = compute(node.children[1], v_v_pair)
            if node.children[0].value and node.children[1].value:
                node.value = True
                node.node_type = 'constant'
                node.evaluated = True
                node.gate = None
            else:
                node.value = False
                node.node_type = 'constant'
                node.evaluated = True
                node.gate = None
    return node
    
# def input_gates(node):
#     if node.node_type == 'leaf':
#         return node.gate
#     else:
#         var = []
#         for child in node.children:
#             var.extend(input_gates(child))
#         return list(set(var))

def input_gates(node):
    leaf_values = []

    if not node.children:
        leaf_values.append(node.gate)
    else:
        for child in node.children:
            leaf_values += input_gates(child)
            leaf_values = list(set(leaf_values))
    return leaf_values

    
def print_ddnnf(node):
    if node.node_type == 'leaf':
        return node.gate

    children = [print_ddnnf(child) for child in node.children]
    if node.node_type == 'AND':
        return "(" + " AND ".join(children) + ")"
    elif node.node_type == 'OR':
        return "(" + " OR ".join(children) + ")"
    elif node.node_type == 'NOT':
        return f"(NOT {children[0]}"
    
def print_all_nodes(node):
    """
    For circuit visualization
    node: Input circuit
    """
    if node.node_type == 'leaf':
        print(node.gate, node.id)
    else:
        print(node.gate, node.id)
        for child in node.children:
            print_all_nodes(child)

def delta(node_input, data, memories = {}):
    """
    Computes the delta_k^g mentioned in the algorithm.
    node: node (g) of which delta is to be computed
    data: Pandas dataframe that contains tuple names and probabilities
    memories: memo variable
    Output: All delta_k values for a node. A particular delta_k value can be found by indexing with k (A 1D list)
    """
    node = node_input
    if node.id in memories:
        return memories[node.id]
    else:
        if node.node_type == 'leaf':
            memories[node.id] = [1 - Fraction(data[data.t == node.gate].p.iloc[0]), Fraction(data[data.t == node.gate].p.iloc[0])]
        if node.node_type == 'constant':
            if node.value == True:
                memories[node.id] = [1]
            else:
                memories[node.id] = [1]
        elif node.node_type == 'NOT':
            if node.children[0].id in memories:
                memories[node.id] = memories[node.children[0].id]
            else:
                memories[node.children[0].id] = delta(node.children[0], data, memories)
                memories[node.id] = memories[node.children[0].id]
        
        elif node.node_type == 'OR':
            if node.children[0].id not in memories and node.children[1].id in memories:
                memories[node.children[0].id] = memories[node.children[1].id]
            elif node.children[1].id not in memories and node.children[0].id in memories:
                memories[node.children[1].id] = memories[node.children[0].id]
            elif node.children[0].id not in memories and node.children[1].id not in memories:
                memories[node.children[0].id] = delta(node.children[0], data, memories)
                memories[node.children[1].id] = memories[node.children[0].id]
            memories[node.id] = memories[node.children[0].id]

        elif node.node_type == 'AND':
            memories[node.id] = []
            vg1 = len(input_gates(node.children[0]))
            vg2 = len(input_gates(node.children[1]))
            if node.children[0].id not in memories:
                memories[node.children[0].id] = delta(node.children[0], data, memories)
            else:
                pass
            if node.children[1].id not in memories:
                memories[node.children[1].id] = delta(node.children[1], data, memories)
            else:
                pass
            arr = (len(input_gates(node))+1)*[0]
            for j in range(len(input_gates(node))+1):
                for i in range(min(j+1,vg1+1)):
                    if j-i<=vg2:
                        arr[j] += memories[node.children[0].id][i]*memories[node.children[1].id][j-i]
            memories[node.id] = arr
    return memories[node.id]

def alpha(node_input, data, alphas = {}):
    """
    Computes the alpha_k,l^g mentioned in the algorithm.
    node: node (g) of which delta is to be computed
    data: Pandas dataframe that contains tuple names and probabilities
    alphas: memo variable
    Output: All alpha_k_l values for a node. A particular alpha_k_l value can be found by indexing with k and l (A 2D list)
    """
    node = node_input
    if node.id in alphas:
        return alphas[node.id]
    else:

        if node.node_type == 'leaf':
            alphas[node.id] = [[0],[0,Fraction(data[data.t == node.gate].p.iloc[0])]]
        if node.node_type == 'constant':
            if node.value == True:
                alphas[node.id] = [[1]]
            else:
                alphas[node.id] = [[0]]
        if node.node_type == 'NOT':
            vg = len(input_gates(node))
            values = []
            if node.children[0].id not in alphas:
                alphas[node.children[0].id] = alpha(node.children[0], data, alphas)
            for i in range(vg+1):
                values.append([])
                for j in range(i+1):
                    values[i].append(comb(i,j)*delta(node, data, {})[i] - alphas[node.children[0].id][i][j])
            alphas[node.id] = values
        if node.node_type == 'OR':
            for child in node.children:
                if child.id not in alphas:
                    alphas[child.id] = alpha(child, data, alphas)
            # if node.children[0].id not in alphas:
            #     alphas[node.children[0].id] = alpha(node.children[0], data, alphas)
            # if node.children[1].id not in alphas:
            #     alphas[node.children[1].id] = alpha(node.children[1], data, alphas)
            values = []
            for i in range(len(alphas[node.children[0].id])):
                values.append([])
                for j in range(i+1):
                    values[i].append(sum([alphas[child.id][i][j] for child in node.children]))
                    # values[i].append(alphas[node.children[0].id][i][j] + alphas[node.children[1].id][i][j])
            alphas[node.id] = values
        if node.node_type == 'AND':
            if node.children[0].id not in alphas:
                alphas[node.children[0].id] = alpha(node.children[0], data, alphas)
            if node.children[1].id not in alphas:
                alphas[node.children[1].id] = alpha(node.children[1], data, alphas)
            vg1 = len(input_gates(node.children[0]))
            vg2 = len(input_gates(node.children[1]))
            vg = len(input_gates(node))
            values = []
            for m in range(vg+1):
                values.append([])
                for n in range(m+1):
                    v = 0
                    for i in range(max(0,m-vg2), min(m+1, vg1+1)):
                        for j in range(max(0,n-m+i), min(i+1,n+1)):
                            v += alphas[node.children[0].id][i][j]*alphas[node.children[1].id][m-i][n-j]
                    values[m].append(v)
            alphas[node.id] = values
        return alphas[node.id]
    
def conditioned_dD(node_input, fixed_var, values):
    """
    node_input: Input node for which the conditioned dD circuit is to be found
    fixed_var: List of variables that we want to have a certain value
    values: List of boolean values for each fixed variable (should be of same length as fixed_var)
    """
    node = copy.deepcopy(node_input)
    
    if len(fixed_var) != len(values):
        raise Exception("Length of values and fixed_var must be same")
    
    if node.node_type == 'leaf':
        if not node.evaluated:
            if node.gate in fixed_var:
                node.value = values[fixed_var.index(node.gate)]
                node.node_type = 'constant'
                node.evaluated = True
                node.gate = None
    
    elif node.node_type == 'NOT':
        if not node.evaluated:
            if not node.children[0].evaluated:
                node.children[0] = conditioned_dD(node.children[0], fixed_var, values)
            if node.children[0].value == True:
                node.children = []
                node.value = False
                node.gate = None
                node.evaluated = True
                node.node_type = 'constant'
            elif node.children[0].value == False:
                node.children = []
                node.value = True
                node.gate = None
                node.evaluated = True
                node.node_type = 'constant'
            elif node.children[0].value == None:
                node.evaluated = True
                node.node_type = 'NOT'
                node.gate = ("NOT", node.children[0].gate)

    elif node.node_type == 'OR':
        if not node.evaluated:
            if not node.children[0].evaluated:
                node.children[0] = conditioned_dD(node.children[0], fixed_var, values)
            if not node.children[1].evaluated:
                node.children[1] = conditioned_dD(node.children[1], fixed_var, values)
            
            if node.children[0].value == None and node.children[1].value == None:
                node.evaluated = True
                node.gate = ("OR", node.children[0].gate, node.children[1].gate)
            elif node.children[0].value == None and node.children[1].value == False:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == None and node.children[1].value == True:
                node = node.children[1]
                node.evaluated = True
            elif node.children[0].value == False and node.children[1].value == None:
                node = node.children[1]
                node.evaluated = True
            elif node.children[0].value == False and node.children[1].value == False:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == False and node.children[1].value == True:
                node = node.children[1]
                node.evaluated = True
            elif node.children[0].value == True and node.children[1].value == None:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == True and node.children[1].value == False:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == True and node.children[1].value == True:
                node = node.children[0]
                node.evaluated = True


    elif node.node_type == 'AND':
        if not node.evaluated:
            if not node.children[0].evaluated:
                node.children[0] = conditioned_dD(node.children[0], fixed_var, values)
            if not node.children[1].evaluated:
                node.children[1] = conditioned_dD(node.children[1], fixed_var, values)
            
            if node.children[0].value == None and node.children[1].value == None:
                node.evaluated = True
                node.gate = ("AND", node.children[0].gate, node.children[1].gate)
            elif node.children[0].value == None and node.children[1].value == False:
                node = node.children[1]
                node.evaluated = True
            elif node.children[0].value == None and node.children[1].value == True:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == False and node.children[1].value == None:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == False and node.children[1].value == False:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == False and node.children[1].value == True:
                node = node.children[0]
                node.evaluated = True
            elif node.children[0].value == True and node.children[1].value == None:
                node = node.children[1]
                node.evaluated = True
            elif node.children[0].value == True and node.children[1].value == False:
                node = node.children[1]
                node.evaluated = True
            elif node.children[0].value == True and node.children[1].value == True:
                node = node.children[0]
                node.evaluated = True

    return node

def parse_ddnnf(node, exps_dict, nodes = {}):
    """
    Used for parsing ddnnfs in python from provsql outputs
    """
    if node in nodes:
        return nodes[node]
    else:
        if exps_dict[node][0] == 'leaf':
            nodes[node] = Node(gate = exps_dict[node][1], node_type = 'leaf')

        elif exps_dict[node][0] == "NOT":
            if exps_dict[node][1] not in nodes:
                nodes[exps_dict[node][1]] = parse_ddnnf(exps_dict[node][1], exps_dict, nodes)
            nodes[node] = Node(gate = ("NOT",nodes[exps_dict[node][1]].gate), node_type = 'NOT', children = [nodes[exps_dict[node][1]]])
            
        elif exps_dict[node][0] in ["AND", "OR"]:
            for i in exps_dict[node][1:]:
                if i not in nodes:
                    nodes[i] = parse_ddnnf(i, exps_dict, nodes)
            nodes[node] = Node(gate = (exps_dict[node][0], *(nodes[i].gate for i in exps_dict[node][1:])), node_type = exps_dict[node][0], children = [nodes[i] for i in exps_dict[node][1:]])
        return nodes[node]
    
def text_to_node(path):
    """
    Text to node (Text input from output of provsql)
    Returns: The circuit and the leaf variables probabilities
    """
    with open(path) as f:
        lines = f.readlines()
    probs = {}
    node_dict = {}
    
    for line in lines:
        line = line.split(" ")
        line[-1] = line[-1].split("\n")
        line[-1] = "".join(line[-1])
        if line[1] in ["AND", "OR"]:
            node_dict[line[0]] = [line[1], line[2:]]
        elif line[1] == "NOT":
            node_dict[line[0]] = [line[1], [line[2]]]
        elif line[1] == "IN":
            node_dict[line[0]] = ['leaf', []]
            probs[line[0]] = float(line[-1])
    del lines
    for i in node_dict:
        if node_dict[i][0] in ["AND", "OR"] and len(node_dict[i][1])<2:
            node_dict[i] = node_dict[node_dict[i][1][0]]
    
    exps_dict = {}
    for node in node_dict:
        if node_dict[node][0] in ["AND", "OR"]:
            exps_dict[node] = [node_dict[node][0]]
            for i in node_dict[node][1]:
                exps_dict[node].append(i)
        elif node_dict[node][0] == "NOT":
            exps_dict[node] = [node_dict[node][0], node_dict[node][1][0]]
        elif node_dict[node][0] == "leaf":
            exps_dict[node] = ['leaf',node]

    del node_dict
    
    keys = list(exps_dict.keys())
    for i in keys:
        for j in keys:
            if i in exps_dict and j in exps_dict:
                if i != j and exps_dict[i] == exps_dict[j]:
                    for node in exps_dict:
                        if max(i,j) in exps_dict[node]:
                            exps_dict[node][exps_dict[node].index(max(i,j))] = min(i,j)

    for i in keys:
        for j in keys:
            if i in exps_dict and j in exps_dict:
                if i != j and exps_dict[i] == exps_dict[j]:
                    exps_dict.pop(max(i,j))

    for node in exps_dict:
        exps_dict[node] = tuple(exps_dict[node])
    root = list(exps_dict.keys())[0]
    ddnnf = parse_ddnnf(root, exps_dict, {})

    return ddnnf, probs

def EShap(node_input, x, data):
    node = copy.deepcopy(node_input)
    """
    node: Input node or the lineage of the query in dD circuit form for which shapley value is to be found
    x: The variable in the formula for which we find the shapley value (The fact of which the importance is to be found)
    data: Pandas dataframe that contains tuple names and probabilities
    """
    if x not in input_gates(node):
        raise Exception("Variable "+x+ " not present in formula")
    px = Fraction(data[data.t == x].p.iloc[0])

    if conditioned_dD(node, [x], [True]).gate != None:
        cond_t = parse(conditioned_dD(node, [x], [True]).gate,{},[])
    else:
        cond_t = conditioned_dD(node, [x], [True])
    if conditioned_dD(node, [x], [False]).gate != None:
        cond_f = parse(conditioned_dD(node, [x], [False]).gate,{},[])
    else:
        cond_f = conditioned_dD(node, [x], [False])
    alpha_t = alpha(cond_t, data,{})
    alpha_f = alpha(cond_f, data,{})

    m_t = len(alpha_t)
    n_t = max([len(alpha_t[i]) for i in range(len(alpha_t))])

    m_f = len(alpha_f)
    n_f = max([len(alpha_f[i]) for i in range(len(alpha_f))])

    array_t = np.zeros((max(m_t, m_f), max(n_t, n_f)))
    array_f = np.zeros((max(m_t, m_f), max(n_t, n_f)))

    for k in range(len(alpha_t)):
        for l in range(len(alpha_t[k])):
            array_t[k][l] = alpha_t[k][l]/((k+1)*comb(k,l))

    for k in range(len(alpha_f)):
        for l in range(len(alpha_f[k])):
            array_f[k][l] = alpha_f[k][l]/((k+1)*comb(k,l))

    eshap = np.sum(array_t - array_f)
    eshap *= px
    return eshap

def EShap_naive(node_input, x, data):
    node = copy.deepcopy(node_input)
    variables = input_gates(node)
    num_input_gates = len(variables)
    probs = [data[data.t == variables[i]].p.iloc[0] for i in range(num_input_gates)]
    eshap = 0
    for i in range(num_input_gates):
        for D in itertools.combinations(set(variables)-{x},i):
            D = set(D)
            P_D = np.product([probs[i] if variables[i] in D or variables[i] == x else 1-probs[i] for i in range(num_input_gates)])
            for j in range(len(D)+1):
                for E in itertools.combinations(D,j):
                    values_plus = [True if variables[i] in E or variables[i] == x else False for i in range(num_input_gates)]
                    values_minus = [True if variables[i] in E else False for i in range(num_input_gates)]
                    MC = compute(node, {variables[i]: values_plus[i] for i in range(num_input_gates)}).value - compute(node, {variables[i]: values_minus[i] for i in range(num_input_gates)}).value
                    eshap += P_D*(1/(i+1))*(1/comb(i , j))*MC
    return eshap
