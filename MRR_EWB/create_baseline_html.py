import os
import json
from dataset_tools import Metrics_v2, Report
from sys import argv


def ValidateByObjecIds(actual, predicted):
    return (
            actual['document'] == predicted['document']
    )


def calculate_metrics(in_file, out_file):

    out_file_html = f'{out_file}.html'
    out_file_json = f'{out_file}.json'

    cnt_limit = 100
    shortName = 'shortName'
    color_name = 'green'

    dash_style = 'solid'
    '''
    # https://docs.bokeh.org/en/latest/docs/user_guide/styling.html
    # 'solid'
    # 'dashed'
    # 'dotted'
    # 'dotdash'
    # 'dashdot'
    '''

    data = []
    stat, metrics = Metrics_v2.EvaluateByFile(in_file, ValidateByObjecIds, False, 2, cnt_limit)
    data.append((stat, metrics, shortName, '', color_name, dash_style, ''))

    Report.Generate(data, cnt_limit, out_file_html)

    with open(out_file_json, 'w', encoding="utf-8") as fl:
        fl.write(json.dumps(data[0][0:2]))

    # debug
    print('\n---stat---\n')
    print(stat)

    print('\n---metrics---\n')
    print(metrics)

    print('\n---data---\n')
    print(data)

    ret = {}
    ret["MRR10"] = metrics["MRR"][9]
    ret["NDCG10"] = metrics["NDCG"][9]
    return ret

