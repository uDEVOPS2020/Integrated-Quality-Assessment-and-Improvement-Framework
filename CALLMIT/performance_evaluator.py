
import pandas as pd
import numpy as np
import utility
import json
import os


def get_config_from_dataset(path_conf, ser, met, df_experiments):

    if os.path.isfile(path_conf):
        with open(path_conf, 'r') as f_c:
            config = json.load(f_c)
            df_config = df_experiments[(df_experiments['NUSER'] == config['NUSER']) &
                                       (df_experiments['LOAD'] == config['LOAD']) &
                                       (df_experiments['SR'] == config['SR'])]

            if len(df_config) == 0:
                print("MANCA: ({},{},{})".format(config['NUSER'], config['LOAD'],
                                                 config['SR']))
            return config, df_config[met + "_" + ser].mean()
    else:
        return None, None


def calc_metrics(df, services, path_configs):
    metrics = ['RES_TIME', 'CPU', 'MEM']

    metrics_dict = {}

    def check_anomaly():
        users = list(set(df['NUSER']))
        users.sort(reverse=True)
        for nuser in users:
            for l in list(set(df['LOAD'])):
                for sr in list(set(df['SR'])):
                    val_ = df[(df['NUSER'] == nuser) & (df['LOAD'] == l) & (
                        df['SR'] == sr)][met + "_" + ser].mean()
                    if val_ > ths:
                        return True
        return False

    for met in metrics:
        true_positive = 0
        true_negative = 0
        false_negative = 0
        false_positive = 0

        for ser in services:
            path_conf = os.path.join(path_configs, f'{met}_{ser}.json')
            ths = utility.calculate_threshold(df, f'{met}_{ser}')
            config, value_config = get_config_from_dataset(
                path_conf, ser, met, df)
            if config is not None:
                if value_config > ths:
                    true_positive += 1
                else:
                    false_positive += 1
            else:
                if check_anomaly():
                    false_negative += 1
                else:
                    true_negative += 1

        precision = 0.0
        recall = 0.0

        if true_positive > 0:
            precision = true_positive / (true_positive + false_positive)

            if false_negative > 0:
                recall = true_positive / (true_positive + false_negative)
            else:
                recall = 1.0

        if precision == 0 and recall == 0:
            f1 = 0.
        else:
            f1 = 2*(precision*recall)/(precision+recall)
        metrics_dict[met] = {"precision": precision, "recall": recall, 'f1': f1,
                             "true_positive": true_positive, "true_negative": true_negative,
                             "false_positive": false_positive, "false_negative": false_negative}

    return metrics_dict


def calc_mean_metrics(path, reps, df):

    path_mean_metrics = os.path.join(path, 'avg_metrics.json')
    services = utility.get_services(df)

    metrics = ['RES_TIME', 'CPU', 'MEM']
    mean_metrics = {}
    metrics_reps = {}

    for met in metrics:
        metrics_reps[met] = {
            'precision': [0.] * len(reps),
            'recall': [0.] * len(reps),
            'f1': [0.] * len(reps),
            'true_positive': [0.] * len(reps),
            'true_negative': [0.] * len(reps),
            'false_positive': [0.] * len(reps),
            'false_negative': [0.] * len(reps)
        }
        mean_metrics[met] = {}

    for k, rep in enumerate(reps):
        path_rep = os.path.join(path, f'rep{rep}')

        met_rep = calc_metrics(df, services, os.path.join(path_rep, 'triples'))

        for met in metrics:
            for key, val in met_rep[met].items():
                metrics_reps[met][key][k] = val

        with open(os.path.join(path_rep, 'metrics.json'), 'w') as f_metric_rep:
            json.dump(met_rep, f_metric_rep)

    for met in metrics:
        for key, val in metrics_reps[met].items():
            mean_metrics[met][key + '_mean'] = round(np.mean(val), 3)
            mean_metrics[met][key + '_std'] = round(np.std(val), 3)

    with open(path_mean_metrics, 'w') as f_metrics:
        json.dump(mean_metrics, f_metrics)