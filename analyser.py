import argparse
from functools import reduce
from json import loads
from sort_click_data_files import get_sorted_files
from diagram_holoviews import draw_diagram
from collections_helpers import merge_counts_dictionaries, add_simple_dictionaries


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


def get_eventnames(acc, event_description):

    if "payload" not in event_description:
        return acc
    payload = event_description["payload"]

    if "eventname" not in payload:
        return acc

    event_name = payload["eventname"]

    if event_name not in acc:
        acc[event_name] = set()

    if "searchreference" in payload:
        search_reference = payload["searchreference"]
        acc[event_name].add(search_reference)

    return acc


document_actions = ["query", "documentvieweropened", "documentviewed", "queryaction", "downloadpdf"]


def get_document_actions(acc, event_description):
    """
    Analyzes the event description and extracts relevant information.

    Args:
        acc (dict): The accumulator dictionary to store session IDs and event names.

        event_description (dict): The event description dictionary.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    if "payload" not in event_description:
        return acc
    payload = event_description["payload"]
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

    if session_id not in acc:
        acc[session_id] = []
        acc[session_id].append(event_name)
    else:
        acc[session_id].append(event_name)
    return acc


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

    if "istestaccount" in payload and payload["istestaccount"]:
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
        search_reference = payload["searchreference"]
        if search_reference is None:
            search_reference = "None"
        event_name = event_name + ' ' + search_reference
    else:
        event_name = payload["eventname"]

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


def save_events_file(events, outputFile):
    # Print the event chains
    with open(outputFile, "w", encoding='UTF-8') as outfile:
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


def collect_search_counts_in_sessions(counts, session_description):
    """
    Collects search counts in sessions.
    searches_count is the number of searches in the session and also downloadpdf from direct link or qta search

    Args:
        session_description (dict): The session description dictionary.
        counts (dict): The dictionary to store search counts.

    Returns:
        dict: A dictionary containing the search counts.
    """
    if isinstance(session_description, tuple):
        session_events = session_description[1]
        searches_count = len(session_events)
        if searches_count in counts:
            counts[searches_count] += 1
        else:
            counts[searches_count] = 1
    return counts


def collect_opened_links_in_searches(counts, session_description):
    """
    Collects opened links in searches.

    Args:
        session_description (dict): The session description dictionary.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary containing the opened links counts.

    Code definitions:
        session_description is a tuple with session_id and collection of searches named as session_events
    """
    if isinstance(session_description, tuple):
        session_events = session_description[1]

        for queryid, events in session_events.items():
            document_events = set()  # analyze for every search
            for event in events:
                if "documentvieweropened" in event \
                        or "documentviewed" in event \
                        or "downloadpdf" in event:
                    name = event.replace("documentvieweropened", "").\
                        replace("documentviewed", "").\
                        replace("downloadpdf", "")
                    document_events.add(name)
            count = len(document_events)
            if count in counts:
                counts[count] += 1
            else:
                counts[count] = 1
    return counts


def collect_opened_links_by_searchnumbers_in_searches(counts, session_description):
    """
    Collects opened links in searches according to number of searches.

    Args:
        session_description (dict): The session description dictionary.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary containing the opened links counts.
    """
    if isinstance(session_description, tuple):
        session_events = session_description[1]
        searches_count = len(session_events)

        for queryid, events in session_events.items():
            document_events = set()
            pdfdownload_count = 0
            for event in events:

                if "documentvieweropened" in event \
                        or "documentviewed" in event:
                    name = event.replace("documentvieweropened", "").\
                        replace("documentviewed", "").\
                        replace("downloadpdf", "")
                    if len(name) > 0:
                        document_events.add(name)
                if "downloadpdf" in event:  # calculate all downloadpdf events in the session
                    pdfdownload_count += 1
            document_events_count = len(document_events) #+ pdfdownload_count
            if searches_count in counts:
                if document_events_count in counts[searches_count]:
                    counts[searches_count][document_events_count] += 1
                else:
                    counts[searches_count][document_events_count] = 1
            else:
                counts[searches_count] = {}
                counts[searches_count][document_events_count] = 1
    return counts


def position_distribution(document_events_stat, document_events):
    """
    Calculates the position distribution of opened documents.

    Args:
        document_events_stat (dict): The dictionary to store opened links counts.
        document_events (set): A set of opened documents.

    Returns:
        dict: A dictionary containing the position distribution.
    """
    for position_description in document_events:
        position_key = "0"  # default position key means nothing was opened/viewed/downloaded
        segments = position_description.split("-")
        if len(segments) == 3:
            if not isinstance(segments[1], str):
                print(f"Invalid position description: {position_description}")
                continue
            if not segments[1].isdigit():
                print(f"Invalid position description: {position_description}")
                continue
            i = int(segments[1])
            if i < 11:
                # position_key = segments[0] + "-" + segments[1]
                position_key = str(segments[1])
            elif i < 21:
                # position_key = segments[0] + "-(11-20)"
                position_key = "(11-20)"
            elif i < 101:
                # position_key = segments[0] + "-(21-100)"
                position_key = "(21-100)"
            else:
                # position_key = segments[0] + "-(101-...)"
                position_key = "(101-...)"

        if position_key in document_events_stat:
            document_events_stat[position_key] += 1
        else:
            document_events_stat[position_key] = 1
    return document_events_stat


def collect_opened_documents_positions_distribution_in_searches(counts, session_description):
    """
    Collects opened links distribution in searches according to number of searches.

    Args:
        session_description (dict): The session description dictionary.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary containing the opened links counts.
    """
    if isinstance(session_description, tuple):
        session_events = session_description[1]

        for queryid, events in session_events.items():
            document_events = set()
            document_events_stat = {}
            for event in events:
                name = event
                if "documentvieweropened" in event \
                        or "documentviewed" in event:
                    name = event.replace("documentvieweropened", "").\
                        replace("documentviewed", "")
                document_events.add(name)
                if "downloadpdf" in event:  # calculate all downloadpdf events in the session
                    if "downloadpdf" not in document_events_stat:
                        document_events_stat["downloadpdf"] = 1
                    else:
                        document_events_stat["downloadpdf"] += 1
            document_events_stat = position_distribution(document_events_stat, document_events)
            document_events_count = len(session_events.items())
            counts = merge_counts_dictionaries(counts, document_events_count, document_events_stat)
    return counts


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
            out_line = f"Searches: {count}, Value: {opened_links[count]}"
            print(out_line)
            outfile.write(out_line + "\n")

        outfile.write(separator + "\n")
        print(separator)
        summary_header4 = "Opened links distribution in searches:\n"
        print(summary_header4)
        outfile.write(summary_header4)
        for count in sorted(opened_links_distribution.keys()):
            out_line = f"Searches: {count}, Value: {opened_links_distribution[count]}"
            print(out_line)
            outfile.write(out_line + "\n")


def dump_cumulative_sammary(outputFile, statistics):

    with open(outputFile, "a") as outfile:
        separator = '-' * 80
        outfile.write(separator + "\n")
        print(separator)
        summary_header1 = "Сliсk links distribution:\n"
        print(summary_header1)
        outfile.write(summary_header1)

        #  calculate Totall
        total = sum(val for statistics_key, val in statistics.items()
                    if isinstance(val, int) and statistics_key != "downloadpdf")

        cumulative_percent = 0
        for position in sorted(statistics.keys()):
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

    events = {}   # accumulator for statistics
    for file in files:
        events = analyse_logfile(file, events, get_document_actions_grouped_by_queryid)

    save_events_file(events, outputFile)

    search_counts = summarize_events(events, collect_search_counts_in_sessions)
    opened_links_cumulative = summarize_events(events, collect_opened_links_in_searches)
    # Collect opened links in searches
    opened_links = summarize_events(events, collect_opened_links_by_searchnumbers_in_searches)
    # Collect opened links distribution in searches
    opened_links_distribution = summarize_events(events, collect_opened_documents_positions_distribution_in_searches)

    opened_links_distribution_cumulative = {}
    for key, description in opened_links_distribution.items():
        add_simple_dictionaries(opened_links_distribution_cumulative, description)

    dump_cumulative_sammary(outputFile, opened_links_distribution_cumulative)
    dump_sammary(outputFile)

    draw_diagram(search_counts, opened_links, opened_links_cumulative, opened_links_distribution)



