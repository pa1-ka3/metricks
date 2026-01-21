import csv
from datetime import datetime, timedelta
import os
import shutil
from .query_clickthrough_statistics import main as query_statistics_main
from .create_baseline import main as calculate_mrr_ndcg_metrics


def update_statistics_csv(statistics_file: str, metrics_file: str, output_csv: str):

    with open(statistics_file, mode='r') as fs:
        reader = csv.DictReader(fs)
        statistics = {}
        for row in reader:
            statistics['CTR1'] = float(row['CTR1'])
            statistics['CTR10'] = float(row['CTR10'])
            statistics['CTR100'] = float(row['CTR100'])
            statistics['Non-Click'] = float(row['Non-Click'])

    with open(metrics_file, mode='r') as fm:
        reader1 = csv.DictReader(fm)
        metrics = {}
        for row in reader1:
            metrics['MRR10'] = float(row['MRR10'])
            metrics['NDCG10'] = float(row['NDCG10'])

    statistics['Data'] = get_previous_month_last_day()
    try:
        statistics['MRR10'] = round(metrics['MRR10'], 3)
        statistics['NDCG10'] = round(metrics['NDCG10'], 3)
    except KeyError:
        statistics['MRR10'] = 0
        statistics['NDCG10'] = 0

    fields = ['Data', 'CTR1', 'CTR10', 'CTR100', 'Non-Click', 'MRR10', 'NDCG10']

    with open(output_csv, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(statistics)

    backup_file = output_csv.replace('.csv', f'_backup_{get_previous_month_last_day()}.csv')
    shutil.copyfile(output_csv, backup_file)


def get_previous_month():
    last_day_of_previous_month = get_last_day_prev_month()
    return last_day_of_previous_month.strftime("%Y-%m")


def get_previous_month_last_day():
    last_day_of_previous_month = get_last_day_prev_month()
    return last_day_of_previous_month.strftime("%Y-%m-%d")


def get_last_day_prev_month():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_previous_month


def clean_work_folders():
    work_folder_base = r"d:\content-team\click-data\Work"
    folders_list = ['0', '1', '2', '3', '4']

    for folder_name in folders_list:
        folder_path = os.path.join(work_folder_base, folder_name)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def write_statistics(statistics: dict, output_file: str, fields: list):
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow(statistics)


if __name__ == "__main__":

    clean_work_folders()

    input_click_path_base = r"\\fsxnetapp01.ihsglobal.local\goldfire-arch-prod\ewb-click-data\prod"
    prev_month = get_previous_month()
    input_click_path = input_click_path_base + '\\' + prev_month
    output_path = r"d:\content-team\click-data\Work\0\events"

    statistics_file = r"d:\content-team\click-data\Work\5\statistics.csv"
    metrics_file = r"d:\content-team\click-data\Work\5\metrics.csv"

    query_stat = query_statistics_main(click_path=input_click_path, output_file=output_path)

    stat = {}
    stat['CTR1'] = query_stat['CTR@1']
    stat['CTR10'] = query_stat['CTR@10']
    stat['CTR100'] = query_stat['CTR@100']
    stat['Non-Click'] = query_stat['Non-Click']

    fields = ['CTR1', 'CTR10', 'CTR100', 'Non-Click']
    write_statistics(stat, statistics_file, fields)
    
    metrics_raw = calculate_mrr_ndcg_metrics()
    metrics = {}
    metrics['MRR10'] = metrics_raw['researcher']['MRR10']
    metrics['NDCG10'] = metrics_raw['researcher']['NDCG10']
    fields = ['MRR10', 'NDCG10']
    
    write_statistics(metrics, metrics_file, fields)
    
    output_csv = r"d:\content-team\click-data\Work\metrics\metrics_report.csv"
    update_statistics_csv(statistics_file, metrics_file,
                          output_csv=output_csv)

    target_path = r"c:\agent\data\metrics_report.csv"
    shutil.copyfile(output_csv, target_path)


    print("Process finished")