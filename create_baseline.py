import os
import sys
import glob
import shutil
import subprocess
import datetime
import argparse
import smtplib
from email.mime.text import MIMEText


class BaseConfig:
    log_file: str

    class Scripts:
        python2: str
        python3: str
        scripts_folder: str
        skipRunTests = False

    class WorkFolders:
        run_query_folder: str
        run_query_folder_bf: str

    class InputPaths:
        in_adataset_folder: str
        filter_adataset = "adataset.*.*.json"

    class OutputPaths:
        out_queries_folder: str
        baseline_folder: str



class ConfigDenver(BaseConfig):
    log_file = r"d:\content-team\update-automation-2\Click-Data-Elastic-7\create_baseline_metrics_test.log"

    class Scripts:
        python2 = r"c:\Python27\python.exe"
        python3 = r"c:\Users\svc_goldfire_stage\AppData\Local\Programs\Python\Python312\python.exe"
        scripts_folder = r"d:\content-team\update-automation-2\Click-Data-Elastic-7"
        skipRunTests = False

    class WorkFolders:
        run_query_folder = r"d:\gf-goldfire.test.art.runner_metrik1\search-quality"
        run_query_folder_bf = r"d:\gf-goldfire.test.art.runner.bf\search-quality"

    class InputPaths:
        in_adataset_folder = r"\\fsxnetapp01.ihsglobal.local\goldfire-arch-prod\ewb-click-data\search-quality\popular-docs"
        filter_adataset = "adataset.*.*.json"

    class OutputPaths:
        out_queries_folder = r"\\fsxnetapp01.ihsglobal.local\goldfire-arch-prod\ewb-click-data\search-metrics-test-quality\queries"
        baseline_folder = r"\\fsxnetapp01.ihsglobal.local\goldfire-arch-prod\ewb-click-data\search-metrics-test\dataset"


class ConfigDev(BaseConfig):
    log_file = r"c:\Data\ClickData_results\create_baseline_metrics_test.log"

    class Scripts:
        python2 = r"c:\Python27\python.exe"
        python3 = r"c:\Projects\Content.Scripts\patents_clickdata\gf-content.scripts.patent\gfrscripts\click-data\venv\Scripts\python.exe"
        scripts_folder = r"C:\Projects\Content.Scripts\patents_clickdata\gf-content.scripts.patent\gfrscripts\click-data\click_analyzer\MRR_EWB"
        skipRunTests = False

    class WorkFolders:
        run_query_folder = r"d:\gf-goldfire.test.art.runner_metrik1\search-quality"
        run_query_folder_bf = r"d:\gf-goldfire.test.art.runner.bf\search-quality"

    class InputPaths:
        in_adataset_folder = r"c:\Data\ClickData_queries\popular-docs"
        filter_adataset = "adataset.*.*.json"

    class OutputPaths:
        out_queries_folder = r"\\fsxnetapp01.ihsglobal.local\goldfire-arch-prod\ewb-click-data\search-metrics-test-quality\queries"
        baseline_folder = r"c:\Data\ClickData_results\baseline"


def write_info(msg, log_file):
    message = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(message)
    with open(log_file, "a", encoding="ascii") as f:
        f.write(message + "\n")


def copy_result(src, dst, log_file):
    if os.path.exists(src):
        shutil.copyfile(src, dst)
    else:
        message = f"Something is wrong with query execution, there is no required out_file '{src}', Exit"
        write_info(message, log_file)
        # send_email(message)
        sys.exit(1)


def send_email(message):
    # Adjust SMTP settings as needed
    smtp_server = "vwc-2igdfap46.ihsglobal.local"
    from_addr = "goldfire.diagnostics@accuris.tech"
    to_addr = ["alexander.korsuk@accuristech.com"]
    subject = message
    body = message

    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addr)

    try:
        with smtplib.SMTP(smtp_server) as server:
            server.sendmail(from_addr, to_addr, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")


def run_subprocess(args, log_file):
    write_info(f"Running: {' '.join(args)}", log_file)
    subprocess.run(args, check=True)


def main():
    config = ConfigDev

    if not os.path.exists(config.log_file):
        open(config.log_file, "w").close()

    write_info("start", config.log_file)
    run_date_format = "%Y-%m-%d_%H-%M-%S"
    run_date = datetime.datetime.now().strftime(run_date_format)

    # Find last adataset file
    adataset_files = sorted(
        glob.glob(os.path.join(config.InputPaths.in_adataset_folder, config.InputPaths.filter_adataset)),
        reverse=True
    )
    if not adataset_files:
        write_info("No adataset files found", config.log_file)
        sys.exit(1)
    last_adataset = adataset_files[0]
    last_adataset_name = os.path.basename(last_adataset)
    period_from = last_adataset_name.split(".")[1]
    period_to = last_adataset_name.split(".")[2]
    write_info(f"(last adataset: '{last_adataset}' )", config.log_file)

    # 01 - get queries from adataset 
    out_queries_file = os.path.join(config.OutputPaths.out_queries_folder, f"queries.{period_from}.{period_to}.txt")
    script_get_queries = os.path.join(config.Scripts.scripts_folder, "get_queries.py")
    #run_subprocess([config.Scripts.python3, script_get_queries, last_adataset, out_queries_file], config.log_file)
    write_info(f"(out file '{out_queries_file}')", config.log_file)

    # 02 - run queries
    dataset_queries_folder = r"c:\Data\ClickData_queries\dataset"
    executed_qta = os.path.join(dataset_queries_folder, f"qta.{period_from}.{period_to}.{run_date}.jsonl")
    executed_researcher = os.path.join(dataset_queries_folder, f"researcher.{period_from}.{period_to}.{run_date}.jsonl")
    executed_researcher_bf = os.path.join(dataset_queries_folder, f"researcherbf.{period_from}.{period_to}.{run_date}.jsonl")

    #in_run_query_file = os.path.join(config.WorkFolders.run_query_folder, "queries.txt")
    #out_qta_run_file = os.path.join(config.WorkFolders.run_query_folder, "qta.out.jsonl")
    out_qta_run_file = r"c:\Data\ClickData_queries\TestResults\qta.out.jsonl"
    #out_researcher_run_file = os.path.join(config.WorkFolders.run_query_folder, "researcher.out.jsonl")
    out_researcher_run_file = r"c:\Data\ClickData_queries\TestResults\researcher.out.jsonl"
    #script_run_queries = os.path.join(config.WorkFolders.run_query_folder, "run-QueryStatisticTests.bat")

    #in_run_query_file_bf = os.path.join(config.WorkFolders.run_query_folder_bf, "queries.txt")
    #out_researcher_run_file_bf = os.path.join(config.WorkFolders.run_query_folder_bf, "researcher.out.jsonl")
    out_researcher_run_file_bf = r"c:\Data\ClickData_queries\TestResults_bf\researcher.out.jsonl"
    #script_run_queries_bf = os.path.join(config.WorkFolders.run_query_folder_bf, "run-QueryStatisticTests.bat")

    if not config.Scripts.skipRunTests:
        # Clean up work folders
        '''
        for folder in [config.WorkFolders.run_query_folder, config.WorkFolders.run_query_folder_bf]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)
        '''

        # Copy queries for tests
        #shutil.copyfile(out_queries_file, in_run_query_file)
        #shutil.copyfile(out_queries_file, in_run_query_file_bf)

        # Run tests
        #run_subprocess([script_run_queries], config.log_file)
        #run_subprocess([script_run_queries_bf], config.log_file)

        # Save query execution result
        copy_result(out_researcher_run_file, executed_researcher, config.log_file)
        copy_result(out_qta_run_file, executed_qta, config.log_file)
        copy_result(out_researcher_run_file_bf, executed_researcher_bf, config.log_file)

    write_info(f"(out files '{executed_researcher}', '{executed_qta}', '{executed_researcher_bf}')", config.log_file)

    # 03 - combine results
    baseline_researcher = os.path.join(config.OutputPaths.baseline_folder,
                                       f"baseline.researcher.{period_from}.{period_to}.{run_date}.jsonl.bz2")
    baseline_qta = os.path.join(config.OutputPaths.baseline_folder,
                                f"baseline.qta.{period_from}.{period_to}.{run_date}.jsonl.bz2")
    baseline_researcher_bf = os.path.join(config.OutputPaths.baseline_folder,
                                          f"baseline.researcherbf.{period_from}.{period_to}.{run_date}.jsonl.bz2")

    script_get_documents = os.path.join(config.Scripts.scripts_folder, "get_documents.py")
    combine_types = {
        executed_researcher: baseline_researcher,
        executed_qta: baseline_qta,
        executed_researcher_bf: baseline_researcher_bf
    }
    for src, dst in combine_types.items():
        run_subprocess([config.Scripts.python3, script_get_documents, last_adataset, src, dst], config.log_file)
    write_info(f"(out files '{baseline_researcher}' and '{baseline_qta}')", config.log_file)

    # 04 - create baseline
    script_create_baseline_html = os.path.join(config.Scripts.scripts_folder, "create_baseline_html.py")
    baseline_types = {
        "researcher": baseline_researcher,
        "qta": baseline_qta,
        "dataset": last_adataset + ".bz2",
        "researcherbf": baseline_researcher_bf
    }
    for name, path in baseline_types.items():
        out_html = os.path.join(config.OutputPaths.baseline_folder, f"{name}.{period_from}.{period_to}.{run_date}")
        run_subprocess([config.Scripts.python3, script_create_baseline_html, path, out_html], config.log_file)

    # 05 - insert baseline to elasticsearch
    """
    os.chdir(config.Scripts.scripts_folder)
    run_date_time = datetime.datetime.strptime(run_date, run_date_format).strftime("%Y-%m-%d.%H:%M:%S")
    script_insert_baseline_to_elk = os.path.join(config.Scripts.scripts_folder, "baseline_to_es5.py")
    for source_type in ["dataset", "researcher", "qta", "researcherbf"]:
        json_file = os.path.join(config.OutputPaths.baseline_folder, f"{source_type}.{period_from}.{period_to}.{run_date}.json")
        run_subprocess([config.Scripts.python2, script_insert_baseline_to_elk, json_file, source_type, period_from, period_to, run_date_time], config.log_file)
    """
    write_info("end", config.log_file)


if __name__ == "__main__":
    main()