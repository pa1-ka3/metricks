import csv
import datetime
import os
import shutil
from .query_clickthrough_statistics import main_statistics as query_statistics_main
from .create_baseline import main as calculate_mrr_ndcg_metrics
from .files_selector import get_dirs_week_period, get_period_boundaries
from .sort_click_data_files import get_sorted_paths


def update_statistics_csv(statistics_file: str, metrics_file: str, output_csv: str, processing_data: str):

    with open(statistics_file, mode='r') as fs:
        reader = csv.DictReader(fs)
        statistics = {}
        for row in reader:
            statistics['CTR1'] = round(float(row['CTR1']), 3)
            statistics['CTR10'] = round(float(row['CTR10']), 3)
            statistics['CTR100'] = round(float(row['CTR100']), 3)
            statistics['Non-Click'] = round(float(row['Non-Click']), 3)

    with open(metrics_file, mode='r') as fm:
        reader1 = csv.DictReader(fm)
        metrics = {}
        for row in reader1:
            metrics['MRR10'] = round(float(row['MRR10']), 3)
            metrics['NDCG10'] = round(float(row['NDCG10']), 3)

    statistics['Data'] = processing_data
    try:
        statistics['MRR10'] = metrics['MRR10']
        statistics['NDCG10'] = metrics['NDCG10']
    except KeyError:
        statistics['MRR10'] = 0
        statistics['NDCG10'] = 0

    fields = ['Data', 'CTR1', 'CTR10', 'CTR100', 'Non-Click', 'MRR10', 'NDCG10']

    update_csv_row(output_csv, statistics, fields)

    backup_file = output_csv.replace('.csv', f'_backup_{get_previous_month_last_day()}.csv')
    shutil.copyfile(output_csv, backup_file)


def update_csv_row(csv_path, new_row, header):
    rows = []
    found = False

    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Data'] == new_row['Data']:
                    rows.append(new_row)   # replace by new row
                    found = True
                else:
                    rows.append(row)

    if not found:
        rows.append(new_row)

    # rewrite whole csv, here csv is list of rows, so we
    # can't use method "write_statistics(statistics: dict, output_file: str, fields: list)"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def get_previous_month():
    last_day_of_previous_month = get_last_day_prev_month()
    return last_day_of_previous_month.strftime("%Y-%m")


def get_previous_month_last_day():
    last_day_of_previous_month = get_last_day_prev_month()
    return last_day_of_previous_month.strftime("%Y-%m-%d")


def get_last_day_prev_month():
    today = datetime.datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
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
    day = datetime.datetime.today()
    period_start, period_end = get_period_boundaries(day)
    dirs = get_dirs_week_period(period_start, period_end, input_click_path_base)
    click_data_files = get_sorted_paths(dirs)

    output_path = r"d:\content-team\click-data\Work\0\events"
    query_stat = query_statistics_main(files=click_data_files, output_file=output_path)

    stat = {}
    stat['CTR1'] = query_stat['CTR@1']['click_through_rate']
    stat['CTR10'] = query_stat['CTR@10']['click_through_rate']
    stat['CTR100'] = query_stat['CTR@100']['click_through_rate']
    stat['Non-Click'] = query_stat['Non_Click_Rate']

    fields = ['CTR1', 'CTR10', 'CTR100', 'Non-Click']
    statistics_file = r"d:\content-team\click-data\Work\5\statistics.csv"
    write_statistics(stat, statistics_file, fields)
    
    metrics_raw = calculate_mrr_ndcg_metrics()
    metrics = {}
    metrics['MRR10'] = metrics_raw['researcher']['MRR10']
    metrics['NDCG10'] = metrics_raw['researcher']['NDCG10']
    fields = ['MRR10', 'NDCG10']

    metrics_file = r"d:\content-team\click-data\Work\5\metrics.csv"
    write_statistics(metrics, metrics_file, fields)
    
    output_csv = r"d:\content-team\click-data\Work\metrics\metrics_report.csv"
    update_statistics_csv(statistics_file,
                          metrics_file,
                          output_csv=output_csv,
                          processing_data=period_end.strftime("%Y-%m-%d"))

    target_path = r"c:\agent\data\metrics_report.csv"
    shutil.copyfile(output_csv, target_path)


    print("Process finished")