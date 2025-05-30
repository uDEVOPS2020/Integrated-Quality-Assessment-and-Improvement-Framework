
import json
import math
import time
import pandas as pd
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.llms import HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.document_loaders import CSVLoader
import utility
import gc
import torch
from utility import CAUSAL_PATHS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage


def __main__(causal_path_type, APP, google_api_key, RANGE_REP=range(10), MAX_RETRY=5):

    if not os.path.exists('results'):
        os.mkdir('results')

    base_path = os.path.join("results", 'gemini')
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    if causal_path_type == CAUSAL_PATHS.NONE:
        path_results = os.path.join(base_path, APP, 'llm_rag')
    elif causal_path_type == CAUSAL_PATHS.STRONGEST_PRUNED:
        path_results = os.path.join(
            base_path, APP, 'llm_crag_strongest_pruned')
        causal_path_fun = utility.get_strongest_path
        CG_TH = 0.3
    elif causal_path_type == CAUSAL_PATHS.STRONGEST:
        path_results = os.path.join(base_path, APP, 'llm_crag_strongest')
        causal_path_fun = utility.get_strongest_path
        CG_TH = 0
    elif causal_path_type == CAUSAL_PATHS.TOP5:
        path_results = os.path.join(base_path, APP, 'llm_crag_top5')
        causal_path_fun = utility.get_TOP5_strongest_path
        CG_TH = 0
    elif causal_path_type == CAUSAL_PATHS.TOP5_PRUNED:
        path_results = os.path.join(base_path, APP, 'llm_crag_top5_pruned')
        causal_path_fun = utility.get_TOP5_strongest_path
        CG_TH = 0.3
    else:
        raise

    if not os.path.exists(path_results):
        os.makedirs(path_results)

    path_dataset = os.path.join('data', f'{APP}_df.csv')
    path_dataset_rag = os.path.join('data', f'{APP}_df_rag.csv')
    embeddings_model = GPT4AllEmbeddings()

    df = pd.read_csv(path_dataset)
    df_rag = pd.read_csv(path_dataset_rag)
    user_size_min = min(df_rag['NUSER'])
    user_size_max = max(df_rag['NUSER'])
    load_labels = list(set(df['LOAD']))
    sr_labels = list(set(df['SR']))

    services = utility.get_services(df)
    prior_knowledge = utility.get_prior_knowledge_mat(df.columns, services)
    df_rag_encoded = df_rag.copy()
    df_rag_encoded["LOAD"] = df_rag_encoded["LOAD"].astype('category')
    df_rag_encoded["LOAD"] = df_rag_encoded["LOAD"].cat.codes

    for rep in RANGE_REP:
        path_results_rep = os.path.join(path_results, 'rep{}'.format(rep))

        if os.path.exists(path_results_rep):
            print("Path already exists")
            quit()

        os.mkdir(path_results_rep)

        path_triples = os.path.join(path_results_rep, 'triples')
        os.mkdir(path_triples)

        loader = CSVLoader(file_path=path_dataset_rag)
        documents = loader.load()

        vector_store = FAISS.from_documents(documents, embeddings_model)

        vector_store.save_local(os.path.join(
            path_results_rep, "faiss_vectorstore"))
        vector_store = FAISS.load_local(os.path.join(
            path_results_rep, "faiss_vectorstore"), embeddings_model, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4})

        llm = ChatGoogleGenerativeAI(google_api_key=google_api_key,
                                     model="gemini-1.5-flash-latest",
                                     temperature=0, max_tokens=50, max_retries=2,)

        if causal_path_type is not CAUSAL_PATHS.NONE:
            path_cg = os.path.join(path_results_rep, 'causal_graph')
            causal_graph = utility.create_causal_graph(
                df_rag_encoded, prior_knowledge, path_cg, CG_TH)
            causal_graph = utility.load_causal_graph(path_cg + '.dot')

        for metric in utility.METRICS:
            for service in services:
                target_met_ser = '{}_{}'.format(metric, service)

                if target_met_ser not in df.columns:
                    print(target_met_ser)
                    continue

                threshold = utility.calculate_threshold(df, target_met_ser)

                if causal_path_type == CAUSAL_PATHS.NONE:
                    prompt_template, question = utility.define_prompt_template(
                        threshold, target_met_ser, load_labels, sr_labels, user_size_max, user_size_min)
                else:
                    causal_paths = []
                    for treat in ['NUSER', 'LOAD', 'SR']:
                        p = causal_path_fun(
                            causal_graph, treat, target_met_ser)
                        if p is not None:
                            for pi in p:
                                causal_paths.append(pi)

                    prompt_template, question = utility.define_prompt_template(
                        threshold, target_met_ser, load_labels, sr_labels, user_size_max, user_size_min, causal_paths)

                prompt = PromptTemplate(
                    input_variables=["context"],
                    template=prompt_template
                )

                with open(os.path.join(path_results_rep, f'prompt_{target_met_ser}.txt'), 'w') as f_prompt:
                    f_prompt.write('==========System Prompt==========\n\n')
                    f_prompt.write(prompt_template)
                    f_prompt.write('\n\n==========Human==========\n\n')
                    f_prompt.write(question)

                rag_chain = {"context": retriever, 'question': RunnablePassthrough(
                )} | prompt | llm | JsonOutputParser(
                    pydantic_object=utility.Triple)

                generated = False
                for _ in range(MAX_RETRY):
                    try:
                        triple = rag_chain.invoke(question)
                        print(triple)
                    except Exception as e:
                        print(f"Parsing error: {e}")
                        print('PARSER FAILED {}. RETRY'.format(target_met_ser))
                        continue

                    if triple['NUSER'] >= user_size_min and triple['NUSER'] <= user_size_max and triple['LOAD'] in load_labels and triple['SR'] in sr_labels:
                        generated = True
                        break
                    print('FAILED TO GENERATE {}. RETRY'.format(target_met_ser))
                if generated:
                    with open(os.path.join(path_triples, '{}.json'.format(target_met_ser)), 'w') as f_triple:
                        json.dump(triple, f_triple)
                else:
                    print('IMPOSSIBLE TO GENERATE {}'.format(target_met_ser))
                del rag_chain

        del vector_store
        del retriever
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()




google_api_key = ''

for app in ['mubench', 'teastore', 'sockshop']:
    __main__(CAUSAL_PATHS.NONE, app,google_api_key,  RANGE_REP=range(10), MAX_RETRY=5)
    __main__(CAUSAL_PATHS.STRONGEST, app,google_api_key,  RANGE_REP=range(10), MAX_RETRY=5)
    __main__(CAUSAL_PATHS.STRONGEST_PRUNED, app,google_api_key,  RANGE_REP=range(10), MAX_RETRY=5)
    __main__(CAUSAL_PATHS.TOP5, app,google_api_key,  RANGE_REP=range(10), MAX_RETRY=5)
    __main__(CAUSAL_PATHS.TOP5_PRUNED, app,google_api_key,  RANGE_REP=range(10), MAX_RETRY=5)