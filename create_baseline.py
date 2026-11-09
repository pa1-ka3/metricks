import os
import sys
import glob
import shutil
import subprocess
import datetime
import smtplib
from email.mime.text import MIMEText
from .MRR_EWB.get_documents import get_combined_documents
from .MRR_EWB.create_baseline_html import calculate_metrics


def EnsureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
# end of EnsureDir


class BaseConfig:
    log_file: str

    class Scripts:
        python2: str
        python3: str
        scripts_folder: str
        skipRunTests = False

    class WorkFolders:
        # numerical suffixes indicate the order of usage
        run_query_folder: str
        run_query_folder_bf: str
        out_queries_folder_1: str
        out_tests_folder_2: str
        out_baseline_folder_3: str

    class InputPaths:
        in_adataset_folder: str
        filter_adataset = "adataset.*.*.json"

    class OutputPaths:
        baseline_folder: str

    class Tests:
        dll: str
        runsettings: str
        filter: str


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



def run_subprocess(args, log_file):
    write_info(f"Running: {' '.join(args)}", log_file)
    subprocess.run(args, check=True)


def main():
    config = ConfigDenver

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
    prepare_queries_file(config, last_adataset, period_from, period_to)

    # 02 - run queries in ART test environment
    executed_researcher = execute_tests(config)

    # 03 - combine results
    baseline_researcher = get_combined_results(config,
                                               executed_researcher,
                                               last_adataset,
                                               period_from,
                                               period_to,
                                               run_date)

    # 04 - create metrics result
    result = create_metrics(baseline_researcher,
                            config,
                            last_adataset,
                            period_from,
                            period_to,
                            run_date)

    write_info("end", config.log_file)
    return result


def create_metrics(baseline_researcher, config, last_adataset, period_from,
                   period_to, run_date):

    baseline_types = {
        "researcher": baseline_researcher,
        "dataset": last_adataset + ".bz2" 
    }
    results = {}
    for name, path in baseline_types.items():
        if path is None:
            continue
        out_html = os.path.join(config.OutputPaths.baseline_folder,
                                f"{name}.{period_from}.{period_to}.{run_date}")
        results[name] = calculate_metrics(path, out_html)

    return results


def get_combined_results(config, executed_researcher, last_adataset, period_from,
                         period_to, run_date):
    baseline_researcher = os.path.join(config.WorkFolders.out_baseline_folder_3,
                                       f"baseline.researcher.{period_from}.{period_to}.{run_date}.jsonl.bz2")

    combine_types = {
        executed_researcher: baseline_researcher
    }
    for src, dst in combine_types.items():
        get_combined_documents(last_adataset, src, dst)
    write_info(f"(out files '{baseline_researcher}' )",
               config.log_file)

    return baseline_researcher


def execute_tests(config):

    executed_researcher = os.path.join(config.WorkFolders.out_tests_folder_2, "researcher.out.jsonl")

    if not config.Scripts.skipRunTests:
        # Run tests
        EnsureDir(executed_researcher)
        run_subprocess([
            "dotnet", "test", config.Tests.dll,
            "--settings", config.Tests.runsettings,
            "--filter", f'TestCategory={config.Tests.filter}',
        ], config.log_file)

    write_info(f"(out files '{executed_researcher}' )",
               config.log_file)
    return executed_researcher


def prepare_queries_file(config, last_adataset, period_from, period_to):
    out_queries_file = os.path.join(config.WorkFolders.out_queries_folder_1,
                                    f"queries.{period_from}.{period_to}.txt")
    script_get_queries = os.path.join(config.Scripts.scripts_folder,
                                      "get_queries.py")
    EnsureDir(out_queries_file)
    run_subprocess([config.Scripts.python3, script_get_queries, last_adataset, out_queries_file],
                   config.log_file)
    write_info(f"(out file '{out_queries_file}')",
               config.log_file)
    shutil.copyfile(out_queries_file,
                    os.path.join(config.WorkFolders.out_queries_folder_1, "queries.txt"))
    return out_queries_file


def test_calculate_metrics(baseline_researcher, out_html):
    return calculate_metrics(baseline_researcher, out_html)


if __name__ == "__main__":
    result = main()

