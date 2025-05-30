
import json
import pandas as pd

strategies = [
   ('llm_rag', 'RAG'),
   ('llm_crag_strongest_pruned', 'SP'),
    ( 'llm_crag_strongest', 'S'),
    ('llm_crag_top5','S5'),
    ('llm_crag_top5_pruned','SP5')
]

def prepare_dataset(subject, model, target_perf_metric, target_metric, path_output):
    dict_ds = {'group': [], 'value':[]}

    for s in strategies:
        for rep in range(10):
            with open(f'./results/{model}/{subject}/{s[0]}/rep{rep}/metrics.json') as f_rep:
                met_rep = json.load(f_rep)
                
                dict_ds['group'].append(s[1])
                dict_ds['value'].append(met_rep[target_perf_metric][target_metric])
    pd.DataFrame.from_dict(dict_ds).to_csv(path_output, index=False)                
            

for sub in ['mubench', 'sockshop', 'teastore']:
  for mod in ['gemini', 'phi3.5']:
    for perf_met in ['RES_TIME', 'CPU', 'MEM']:
      if perf_met == 'MEM' and sub != 'sockshop':
          continue
      for met in ['precision', 'recall', 'f1']:
        prepare_dataset(sub, mod, perf_met, met, f'./statistical_analysis/datasets/{sub}_{mod}_{perf_met}_{met}.csv')