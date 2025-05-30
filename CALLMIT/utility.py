import json
from langchain_core.messages import AIMessage
import lingam
import numpy as np
import networkx as nx
import pandas as pd
import os
from enum import Enum
from pydantic import BaseModel, Field

METRICS = ['RES_TIME', 'CPU', 'MEM']


class CAUSAL_PATHS(Enum):
    NONE = 1
    STRONGEST_PRUNED = 2
    STRONGEST = 3
    TOP5 = 4
    TOP5_PRUNED = 5


class Triple(BaseModel):
    NUSER: int = Field(description="the user size")
    LOAD: str = Field(description="the operational profile")
    SR: int = Field(description="the spawn rate")


def split_dataset(path, name, users):
    df = pd.read_csv(os.path.join(path, name+'_df.csv'))
    df[df['NUSER'].isin(users)].to_csv(
        os.path.join(path, name+'_df_rag.csv'), index=False)


def get_services(df):
    services = set()
    columns = df.columns.tolist()
    columns.remove('NUSER')
    columns.remove('LOAD')
    columns.remove('SR')
    for c in columns:
        if c.startswith('REQ/s'):
            services.add(c.replace('REQ/s_', ''))

    services_list = list(services)
    services_list.sort()
    return services_list


def calculate_threshold(df, target):
    df_1 = df[df['NUSER'] == 1][target]
    return df_1.mean() + 3 * df_1.std()


def threshold_matrix(mat, th=0.):
    if th == 0.:
        return mat
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            if abs(mat[i][j]) < th:
                mat[i][j] = 0
    return mat


def draw_prior_knowledge_mat(mat, cols, path):
    G = nx.DiGraph()
    for c in range(len(cols)):
        if all(x == 0 for x in mat[c]):
            G.add_node(cols[c], color='red')
        else:
            G.add_node(cols[c], color='black')
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            if mat[i][j] == 1:
                G.add_edge(cols[j], cols[i])
    save_dot(G, path)


def adjmat2dot_map(adj_mat, map):
    dag = nx.from_numpy_array(
        adj_mat, create_using=nx.DiGraph, edge_attr='weight')
    nx.relabel_nodes(dag, map, copy=False)
    return dag


def adjmat2dot(adj_mat, cols):
    return adjmat2dot_map(adj_mat, {i: cols[i] for i in range(len(cols))})


def save_dot(G, path):
    A = nx.drawing.nx_agraph.to_agraph(G)
    A.write(path + ".dot")
    A.draw(path + ".pdf", prog='dot')


def create_causal_graph(df, prior_knowledge, path_dot, th):
    X = df.to_numpy(dtype=np.float64)
    model = lingam.DirectLiNGAM(prior_knowledge=prior_knowledge)
    model.fit(X)
    adj_mat = threshold_matrix(np.transpose(model.adjacency_matrix_), th)
    causal_graph = adjmat2dot(adj_mat, df.columns)
    save_dot(causal_graph, path_dot)


def load_causal_graph(path):
    G = nx.DiGraph(nx.nx_pydot.read_dot(path))

    # Convert edge weights to float
    for u, v, data in G.edges(data=True):
        data['weight'] = float(data['weight'].replace('"', ''))

    return G


def get_prior_knowledge_mat(columns, services):

    maps = {i: columns[i] for i in range(0, len(columns))}
    inv_maps = {v: k for k, v in maps.items()}

    # 0: does not have a directed path to
    # 1: has a directed path to
    # -1 : No prior knowledge is available to know if either of the two cases above (0 or 1) is true.

    mat = np.zeros([len(columns), len(columns)], dtype=int) - 1
    treatments = ['NUSER', 'LOAD', 'SR']

    # impedisco archi entranti nei trattamenti
    for treat in treatments:
        for i in range(len(columns)):
            mat[inv_maps[treat]][i] = 0

    # le REQ/s dipendono da i trattamenti
    for ser in services:
        if "REQ/s_" + ser in columns:
            for treat in treatments:
                mat[inv_maps["REQ/s_" + ser]][inv_maps[treat]] = 1
    return mat


def get_strongest_path(G, source, target):
    all_paths = list(nx.all_simple_paths(G, source, target))

    # Find the longest path based on weights
    if len(all_paths) > 0:
        def path_weight(path):
            return sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))

        longest_path = max(all_paths, key=path_weight)
        return [longest_path]
    else:
        None


def get_TOP5_strongest_path(G, source, target):
    all_paths = list(nx.all_simple_paths(G, source, target))

    # Find the longest path based on weights
    if len(all_paths) > 0:
        if len(all_paths) <= 5:
            return all_paths

        def path_weight(path):
            return sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))

        longest_path = sorted(
            all_paths, key=lambda p: path_weight(p), reverse=True)

        return longest_path[:5]
    else:
        None


def get_all_path(G, source, target):
    paths = list(nx.all_simple_paths(G, source, target))

    # Find the longest path based on weights
    if len(paths) > 0:
        return paths
    else:
        None


def define_prompt_template(threshold, target_met_ser, load_labels, sr_labels, user_size_max, user_size_min,
                           cpaths=None):

    prompt = "<|system|>\n"
    prompt += "Use the following constraints:\n"
    prompt += "- NUSER has to be less than {}\n".format(user_size_max+1)
    prompt += "- NUSER has to be greater than {}\n".format(user_size_min)

    prompt += "- LOAD has to be '{}'".format(load_labels[0])
    for i in range(1, len(load_labels)):
        prompt += " or '{}'".format(load_labels[i])

    prompt += "\n- SR has to be '{}'".format(sr_labels[0])
    for i in range(1, len(sr_labels)):
        prompt += " or {}".format(sr_labels[i])

    if cpaths is not None:
        prompt += "\nUse the following causal paths:\n"
        for cp in cpaths:
            prompt += f'{cp[0]}'
            for v in range(1, len(cp)):
                prompt += f' -> {cp[v]}'
            prompt += '\n'

    prompt += "\nUse the following context to help:\n"
    prompt += "{context}<|end|>\n"
    prompt += "<|user|>\n"
    prompt += "{question}\n"
    prompt += "<|assistant|>\n"

    question = "Generate one JSON structure (NUSER, LOAD, SR) which leads {} to exceed {}<|end|>\n".format(
        target_met_ser, threshold)
    question += "\nProvide the results in JSON format, matching the structure of the triple:\n"
    question += "- NUSER: the user size\n"
    question += "- LOAD: the operational profile\n"
    question += "- SR: the spawn rate\n"

    return prompt, question