import argparse
import math
import statistics
from .analyser import analyse_logfile, test_subaccounts
from .analyser import summarize_events
from .analyser import dump_cumulative_sammary
from .accumulations import preprocess_events
from .accumulations import collect_opened_documents_positions_distribution_in_searches_v2
from .accumulations import select_topmost_click_in_searches, calculate_click_through, collect_first_click
from .accumulations import select_events_with_not_opened, filter_extra_actions_only
from .collections_helpers import add_simple_dictionaries
from .constants import document_query, document_actions, doc_extra_actions
from .sort_click_data_files import get_sorted_files


session_id_filter = "sessionid"


def save_events_file(events, outputFile, events_min_count=0):
    # Print the event chains
    with open(outputFile, "w", encoding='utf-8') as outfile:
        for session in sorted(events.keys()):
            values = events[session]
            if isinstance(values, dict):
                sub_lines = ["{0} : {1}".format(queryid, format_event_descr(values[queryid]))
                             for queryid in sorted(values.keys()) if len(values) > events_min_count]
                whole_value = ',\n              '.join(sub_lines)
            else:
                # This is a list of events
                whole_value = ',\n'.join(values)
            if len(whole_value) == 0:
                continue
            save_line(outfile, session, whole_value)
    # Print the event chains


def save_line(outfile, session, whole_value):
    line = f"{session} : {whole_value}"
    print(line.encode("utf-8"))
    outfile.write(line + "\n")


def is_first_search_active(input_values):
    """
    Check if the first searches in the session is active (dowloadpdf, documentvieweropened, documentviewed).
    Actually I can't exclude the last search, because data structure is dictionary,
    so I check every search and count the number of active searches.
    If there are active searches more than 1, then I assume that the first searches is active.

    Args:
        input_values (dict): The dictionary containing events.

    Returns:
        bool: True if the first search is active, False otherwise.
    """
    if not isinstance(input_values, dict):
        return False
    if len(input_values) == 0:
        return False

    values = filter_out_qta(input_values)

    if len(values) == 1:
        return True  # we filtered out qta, so only one search left, then skip it

    active_search_count = 0
    for search in values.values():
        active_search = False
        for item in search:
            if 'downloadpdf' in item or 'documentvieweropened' in item or 'documentviewed' in item:
                active_search = True
                break
        if active_search:
            active_search_count += 1
        if active_search_count > 1:
            return True

    return False


def filter_out_qta(input_values):
    """
    Filter out queries with 'qt' in the event description.

    Args:
        input_values (dict): The dictionary containing events.

    Returns:
        dict: A filtered dictionary without 'qt' events.
    """
    if not isinstance(input_values, dict):
        return input_values
    result = {k: v for k, v in input_values.items() if not any('qt' in item for item in v)}
    return result


def format_event_descr(event_descr):
    if isinstance(event_descr, list):
        sub_lines = ["{0}".format(event) for event in event_descr]
        whole_value = ',\n                            '.join(sub_lines)
        return whole_value
    return str(event_descr)


def save_suspicious_queries(events, outputFile):
        # Print the event chains
    with open(outputFile, "w", encoding='utf-8') as outfile:
        for session, values in events.items():
            if isinstance(values, dict):
                if len(values.items()) == 1:
                    continue
                if len(values.items()) > 7:
                    continue
                if is_first_search_active(values):
                    continue
                sub_lines = ["{0} : {1}".format(queryid, format_event_descr(event_descr)) for queryid, event_descr in values.items()] # if  len(event_descr) < 10]
                whole_value = ',\n              '.join(sub_lines)
            else:
                # This is a list of events
                whole_value = ',\n'.join(values)
            if len(whole_value) == 0:
                continue
            save_line(outfile, session, whole_value)


def clear_last_query_id(events):
    for session_id in events.keys():
        if isinstance(events[session_id], dict):
            events[session_id].pop("last_query_id", None)
    return events


def get_document_queries(acc, event_description):
    """
    Get queries

    Args:
        acc (dict): The accumulator dictionary to store session IDs and related events.

        event_description (dict): The event description dictionary from log file.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    if "payload" not in event_description:
        return acc
    payload = event_description["payload"]

    if "sessionid" not in payload:
        return acc
    session_id = payload["sessionid"]

    if payload.get("istestaccount"):
        return acc

    subaccount_id = ""
    if "subaccountid" in payload:
        subaccount_id = payload["subaccountid"]
        if subaccount_id is None:
            return acc
        if subaccount_id.startswith(tuple(test_subaccounts)):
            return acc

    user_id = payload.get("userid", None)

    if 'user_id_filter' in globals() and user_id_filter is not None:
        if user_id is None or user_id != user_id_filter:
            return acc

    if "eventname" not in payload:
        return acc

    event_name = payload["eventname"]
    if not ((event_name in document_actions) or (event_name in doc_extra_actions) or (event_name in document_query)):
        return acc

    search_reference = payload.get("searchreference", "None")

    if "queryid" not in payload:
        try:
            query_id = acc[session_id]["last_query_id"]
        except KeyError:
            return acc
    else:
        query_id = payload["queryid"]
        if query_id is None:
            query_id = "None"

        query_id = "{0} {1} {2}".format(query_id, subaccount_id, user_id)

    query_text = payload.get("query", "None")
    if event_name == "query" and search_reference == "qt":
        query_text = payload.get('keywordsformatted', 'None')
        #return acc

    event_data = (event_name, search_reference, query_text)

    if session_id not in acc:
        acc[session_id] = {}
        acc[session_id][query_id] = []
        acc[session_id][query_id].append(event_data)
    else:
        if query_id not in acc[session_id]:
            acc[session_id][query_id] = []
            acc[session_id][query_id].append(event_data)
        else:
            acc[session_id][query_id].append(event_data)
    acc[session_id]["last_query_id"] = query_id  # to help store events without 'search query id'

    return acc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clickPath", help="points to click-data location")
    parser.add_argument("--outputFile", help="points to file with results")
    parser.add_argument("--sessionid", help="sessionid to filter events by session ID, default is 'sessionid'")
    parser.add_argument("--userid", help="filter sessions only for this userID")
    args = parser.parse_args()

    if args.clickPath is None:
        exit("No clickPath provided")
    clickPath = args.clickPath

    if args.outputFile is None:
        exit("No outputFile provided")
    outputFile = args.outputFile

    if args.sessionid is not None:
        session_id_filter = args.sessionid

    if args.userid is not None:
        user_id_filter = int(args.userid)

    files = get_sorted_files(clickPath)

    events = {}   # accumulator for raw statistics
    for file in files:
        events = analyse_logfile(file, events, get_document_queries)

    events = clear_last_query_id(events)
    #events = flatten_sets_to_lists(events)
    save_events_file(events, outputFile+'.txt')



    # Distribute "qta" events to the nearest "re" searches
    preprocessed_events = summarize_events(events, preprocess_events)
    save_events_file(preprocessed_events, outputFile + 'prepr.txt')
    save_events_file(preprocessed_events, outputFile + 'prepr_massive_events.txt', events_min_count=5)

    # find sessions with doc_extra_actions but no document_actions
    extra_events = summarize_events(preprocessed_events, filter_extra_actions_only)
    save_events_file(extra_events, outputFile + '_extra_events.txt')

    # Collect opened links distribution in searches
    #  {searches_count: {opened_links_count: count}}
    opened_links_distribution = summarize_events(preprocessed_events,
                                                 collect_opened_documents_positions_distribution_in_searches_v2)

    opened_links_distribution_cumulative = {}
    for key, description in opened_links_distribution.items():
        add_simple_dictionaries(opened_links_distribution_cumulative, description)

    dump_cumulative_sammary(outputFile, opened_links_distribution_cumulative)

    events_with_not_opened = summarize_events(events, select_events_with_not_opened)
    save_events_file(events_with_not_opened, outputFile + 'not_found.txt')

    # CTR (Click-Through Rate), CTR@K, Non-Click Rate
    topmost_clicks = summarize_events(preprocessed_events, select_topmost_click_in_searches)
    save_events_file(topmost_clicks, outputFile + '_topmost_clicks.txt')
    CTR_at_0 = calculate_click_through(topmost_clicks, 0)
    output_strings = []
    out_str = "CTR@0: {0}\n".format(CTR_at_0)
    print(out_str)
    output_strings.append(out_str)

    CTR_at_1 = calculate_click_through(topmost_clicks, 1)
    out_str = "CTR@1: {0}\n".format(CTR_at_1)
    print(out_str)
    output_strings.append(out_str)

    CTR_at_10 = calculate_click_through(topmost_clicks, 10)
    out_str = "CTR@10: {0}\n".format(CTR_at_10)
    print(out_str)
    output_strings.append(out_str)

    CTR_at_100 = calculate_click_through(topmost_clicks, 100)
    out_str = "CTR@100: {0}\n".format(CTR_at_100)
    print(out_str)
    output_strings.append(out_str)

    CTR = calculate_click_through(topmost_clicks, 9998)
    out_str = "CTR: {0}\n".format(CTR)
    print(out_str)
    output_strings.append(out_str)

    Non_Click_Rate = 1.0 - CTR['click_through_rate']
    out_str = "Non_Click_Rate: {0}\n".format(Non_Click_Rate)
    print(out_str)
    output_strings.append(out_str)

    total_searches = sum([len(value) for value in topmost_clicks.values()])
    out_str = "Total searches: {0}\n".format(total_searches)
    print(out_str)
    output_strings.append(out_str)

    # Average First Click Rank (Average position of the first click)
    average_first_click = summarize_events(preprocessed_events, collect_first_click)
    median_value = statistics.median(average_first_click.values())
    average_value = statistics.mean(average_first_click.values())
    average_logarithmic = statistics.mean([math.log(x) for x in average_first_click.values()])
    powered_average = math.exp(average_logarithmic)
    out_str = "median - {0}, average - {1}, logarithmic average {2}\n".format(median_value,
                                                                              average_value,
                                                                              powered_average)
    print(out_str)
    output_strings.append(out_str)

    with open(outputFile + '_summary.txt', 'w', encoding='utf-8') as outFile:
        for line in output_strings:
            outFile.write(line)



