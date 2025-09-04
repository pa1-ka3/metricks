import argparse
from functools import reduce
from json import loads
import re
from .sort_click_data_files import get_sorted_files
#from diagram_holoviews import draw_diagram
from .collections_helpers import add_simple_dictionaries
from .accumulations import collect_search_counts_in_sessions
from .accumulations import collect_opened_links_in_searches
from .accumulations import collect_opened_links_by_searchnumbers_in_session
from .accumulations import collect_opened_documents_positions_distribution_in_searches



def analyse_logfile(path, event_names=None, analyser_function=None):

    if event_names is None:
        event_names = {}
    with open(path, 'r', encoding='utf-8') as log_file:
        event_names = reduce(
            lambda acc, line_in_log:  analyse_event(acc, line_in_log, analyser_function),  # Function to apply
            log_file,
            event_names
        )
    return event_names


def analyse_event(acc, line_text, analyser_function=None):
    """
    Analyzes the event description and extracts relevant information.

    Args:
        acc (dict): The accumulator dictionary to store collected information.

        line_text (str): The line of text from log containing the event description.

        analyser_function (function): A function to apply to the event description.
            This function do actual analysis of the event description.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    try:
        event_description = loads(line_text)
    except ValueError:
        print("Invalid JSON:", line_text)
        return acc

    if isinstance(event_description, dict) and \
            analyser_function is not None:
        return analyser_function(acc, event_description)
    else:
        print("Not a dictionary:", event_description)
        return acc


document_actions = ["query", "documentvieweropened", "documentviewed", "queryaction", "downloadpdf"]
test_subaccounts = ['9988776', '9999997', '9999998', '2323232', '2800000', '0707070', '1111111', '2222123',
                    '2222222', '3333333', '4444444']


def get_document_actions_grouped_by_queryid(acc, event_description):
    """
    Analyzes the event description and group extracts information
    primarily by session ID and then by query ID.

    Args:
        acc (dict): The accumulator dictionary to store session IDs and related events.

        event_description (dict): The event description dictionary from log file.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    if "payload" not in event_description:
        return acc
    payload = event_description["payload"]

    if payload.get("istestaccount"):
        return acc

    if "subaccountid" in payload:
        subaccount_id = payload["subaccountid"]
        if subaccount_id is None:
            return acc
        if subaccount_id.startswith(tuple(test_subaccounts)):
            return acc

    if "sessionid" not in payload:
        return acc
    session_id = payload["sessionid"]

    if "eventname" not in payload:
        return acc

    event_name = payload["eventname"]
    if event_name not in document_actions:
        return acc

    if "searchreference" in payload:
        # enrich event name with search reference
        search_reference = payload["searchreference"]
        if search_reference is None:
            search_reference = "None"
        event_name = event_name + ' ' + search_reference

    if event_name == "query qt":
        return acc

    if "queryid" not in payload:
        return acc
    # use already prepared event_name

    query_id = payload["queryid"]
    if query_id is None:
        query_id = "None"

    if session_id not in acc:
        acc[session_id] = {}
        acc[session_id][query_id] = []
        acc[session_id][query_id].append(event_name)
    else:
        if query_id not in acc[session_id]:
            acc[session_id][query_id] = []
            acc[session_id][query_id].append(event_name)
        else:
            acc[session_id][query_id].append(event_name)

    return acc


def save_events_file(events, output_path):
    # Print the event chains
    with open(output_path, "w", encoding='UTF-8') as outfile:
        for session, values in events.items():
            if isinstance(values, dict):
                sub_lines = ["{0} : {1}".format(queryid, event_descr) for queryid, event_descr in values.items()]
                whole_value = ',\n              '.join(sub_lines)
            else:
                # This is a list of events
                whole_value = ', '.join(values)

            line = f"{session} : {whole_value}"
            print(line)
            outfile.write(line + "\n")
    # Print the event chains


def summarize_events(events, analyser_function=None):

    events_stat = {}
    events_stat = reduce(
        lambda acc, session:  analyser_function(acc, session),  # Function to apply
        events.items(),
        events_stat
    )
    return events_stat


def dump_sammary(outputFile):

    with open(outputFile, "a") as outfile:
        separator = '-' * 80
        outfile.write(separator + "\n")
        print(separator)
        summary_header1 = "Search counts in sessions:\n"
        print(summary_header1)
        outfile.write(summary_header1)
        for count in sorted(search_counts.keys()):
            out_line = f"Searches in session: {count}, Count: {search_counts[count]}"
            print(out_line)
            outfile.write(out_line + "\n")

        outfile.write(separator + "\n")
        print(separator)
        summary_header2 = "Opened links in searches:\n"
        print(summary_header2)
        outfile.write(summary_header2)
        for count in sorted(opened_links_cumulative.keys()):
            out_line = f"Opened documents in one search: {count},  Count: {opened_links_cumulative[count]}"
            print(out_line)
            outfile.write(out_line + "\n")

        outfile.write(separator + "\n")
        print(separator)
        summary_header3 = "Opened links by search numbers in session:\n"
        print(summary_header3)
        outfile.write(summary_header3)
        for count in sorted(opened_links.keys()):
            out_line = f"Searches: {count}, Value: {format_opened_links_distribution(opened_links[count])}"
            print(out_line)
            outfile.write(out_line + "\n")

        outfile.write(separator + "\n")
        print(separator)
        summary_header4 = "Opened links distribution in searches:\n"
        print(summary_header4)
        outfile.write(summary_header4)
        for count in sorted(opened_links_distribution.keys()):
            out_line = f"Searches: {count}, Value: {format_opened_links_distribution(opened_links_distribution[count])}"
            print(out_line)
            outfile.write(out_line + "\n")


def format_opened_links_distribution(opened_links_distribution):
    """
    Formats the opened links distribution for better readability.

    Args:
        opened_links_distribution (dict): The dictionary containing the opened links distribution.

    Returns:
        string: A formatted string representing sorted dictionary where positions as keys and counts as values.
    """
    if not isinstance(opened_links_distribution, dict):
        return str(opened_links_distribution)

    formatted_distribution = []
    for sorted_dict_key in (sorted(opened_links_distribution.keys(), key=lambda item: sort_key(item)) ):
        output = f"{sorted_dict_key}: {opened_links_distribution[sorted_dict_key]}"
        formatted_distribution.append(output)

    result = ", ".join(formatted_distribution)
    return result


def sort_key(k):
    # Priority case: key is integer
    if isinstance(k, int):
        return (0, k)

    # Priority second case : key is digits
    if k.isdigit():
        return (1, int(k))

    # Second order case: key in format (X-Y) or (X-...)
    match = re.match(r'^\((\d+)-', k)
    if match:
        return (2, int(match.group(1)))

    # Else - all other lines
    return (3, k)


def dump_cumulative_sammary(outputFile, statistics):

    with open(outputFile, "a") as outfile:
        separator = '-' * 80
        outfile.write(separator + "\n")
        print(separator)
        summary_header1 = "Click links distribution:\n"
        print(summary_header1)
        outfile.write(summary_header1)

        #  calculate Totall
        total = sum(val for statistics_key, val in statistics.items()
                    if isinstance(val, int) and statistics_key != "downloadpdf")

        cumulative_percent = 0
        for position in sorted(statistics.keys(), key=lambda item: sort_key(item) ):
            if position == "downloadpdf":
                continue
            percent = statistics[position] / total
            cumulative_percent += percent
            out_line = f"Result number: {position}, " \
                       f"Number Of Clicks: {statistics[position]}, " \
                       f"Percent Of Total: {percent * 100:.2f}%, " \
                       f"Cumulative Percent: {cumulative_percent * 100:.2f}%"
            print(out_line)
            outfile.write(out_line + "\n")

        if 'downloadpdf' in statistics:
            out_line = f"Number of downloadpdf: {statistics['downloadpdf']} "
            print(out_line)
            outfile.write(out_line + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clickPath", help="points to click-data location")
    parser.add_argument("--outputFile", help="points to file with results")
    args = parser.parse_args()

    if args.clickPath is None:
        exit("No clickPath provided")
    clickPath = args.clickPath

    if args.outputFile is None:
        exit("No outputFile provided")
    outputFile = args.outputFile

    files = get_sorted_files(clickPath)

    collected_events = {}   # accumulator for statistics
    for file in files:
        events = analyse_logfile(file, collected_events, get_document_actions_grouped_by_queryid)

    save_events_file(collected_events, outputFile)

    search_counts = summarize_events(events, collect_search_counts_in_sessions)
    opened_links_cumulative = summarize_events(events, collect_opened_links_in_searches)
    # Collect opened links in searches
    opened_links = summarize_events(events, collect_opened_links_by_searchnumbers_in_session)
    # Collect opened links distribution in searches
    opened_links_distribution = summarize_events(events, collect_opened_documents_positions_distribution_in_searches)

    opened_links_distribution_cumulative = {}
    for key, description in opened_links_distribution.items():
        add_simple_dictionaries(opened_links_distribution_cumulative, description)

    dump_cumulative_sammary(outputFile, opened_links_distribution_cumulative)

    '''opened_links_distribution_cumulative = {}
    for key, description in opened_links.items():
        add_simple_dictionaries(opened_links_distribution_cumulative, description)
    dump_cumulative_sammary(outputFile, opened_links_distribution_cumulative)
    '''

    dump_sammary(outputFile)

    # draw_diagram(search_counts, opened_links, opened_links_cumulative, opened_links_distribution)



