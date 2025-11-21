'''
Module to extract and save queries from click data log files.
Produce:
1. queries dump in format (unique queries)
session_id: user_id : query1
                      query2

2. queries counts in format
query:    count

3. queries counts by user in format
{query:  "***",  user_id: 1111,  count: 10}

'''


import argparse
import json
import sys
from .sort_click_data_files import get_sorted_files
from .analyser import analyse_logfile, test_subaccounts, document_actions
from .query_grouping import save_events_file
from collections import defaultdict


def get_document_queries(acc, event_description):
    """
    Get queries
    In sessions extracts only unique queries per user

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
    if event_name not in document_actions:
        return acc

    search_reference = payload.get("searchreference", "None")

    if "queryid" not in payload:
        return acc
    # use already prepared event_name

    #query_id = payload["queryid"]
    #if query_id is None:
    #    query_id = "None"

    accaunt_user_id = "{0}_{1}".format(subaccount_id, user_id)

    query_text = payload.get("query", None)
    if query_text is None or query_text == "":
        return acc

    #event_data = (event_name, search_reference, query_text)
    event_data = query_text.lower().strip()

    if session_id not in acc:
        acc[session_id] = {}
        acc[session_id][accaunt_user_id] = set()  # use set to have only unique queries
        acc[session_id][accaunt_user_id].add(event_data)
    else:
        if accaunt_user_id not in acc[session_id]:
            acc[session_id][accaunt_user_id] = set()
            acc[session_id][accaunt_user_id].add(event_data)
        else:
            acc[session_id][accaunt_user_id].add(event_data)

    return acc

"""
ToDo: in session queries should be grouped (only unique queries per session)
"""


def save_all_queries(events, outputFile):
    queries_all = defaultdict(int)
    for session_id, queries in events.items():
        for acc_user_id, query_texts in queries.items():
            for query_text in query_texts:
                queries_all[query_text.strip().lower()] += 1

    with open(outputFile, 'w', encoding="utf-8") as outFile:
        for query, count in sorted(queries_all.items()):
            try:
                out_str = json.dumps({"query": query, "count": count}, ensure_ascii=False) + "\n"
                outFile.write(out_str)
            except Exception as e:
                print(f"Error writing query: {query}\n", file=sys.stderr)


def save_queries_only(events, outputFile):
    queries_set = set()
    for session_id, queries in events.items():
        for acc_user_id, query_texts in queries.items():
            for query_text in query_texts:
                queries_set.add(query_text.strip().lower())
    with open(outputFile, 'w', encoding="utf-8") as outFile:
        for query in sorted(queries_set):
            try:
                out_str = json.dumps(query, ensure_ascii=False) + "\n"
                outFile.write(out_str)
            except Exception as e:
                print(f"Error writing query: {query}\n", file=sys.stderr)
    return queries_set


def save_queries_by_user(events, outputFile):
    queries_all = defaultdict(lambda: defaultdict(int))
    for session_id, queries in events.items():
        for acc_user_id, query_texts in queries.items():
            for query_text in query_texts:
                queries_all[query_text.strip().lower()][acc_user_id] += 1

    with open(outputFile, 'w', encoding="utf-8") as outFile:
        sums_per_query = get_summs_per_query(queries_all)
        sums_per_query_sorted = dict(sorted(sums_per_query.items(), key=lambda item: item[1], reverse=True))
        for query, count in sums_per_query_sorted.items():
            query_stat = queries_all[query]

            for user_id, user_count in query_stat.items():
                try:
                    out_str2 = json.dumps({"query": query, "user_id": user_id, "count": user_count}, ensure_ascii=False) + "\n"
                    outFile.write(out_str2)
                except Exception as e:
                    print(f"Error writing query: {query}\n", file=sys.stderr)

            #out_str3 = json.dumps({"query": query, "count": count}, ensure_ascii=False) + "\n"
            #print(out_str3)
            #outFile.write(out_str3)


def get_summs_per_query(queries_all):
    summ_per_query = {}
    for query, users_counts in queries_all.items():
        summ_per_query[query] = sum(users_counts.values())
    return summ_per_query


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

    save_events_file(events, outputFile+'.txt')
    save_all_queries(events, outputFile+'_all_queries.txt')
    queries = save_queries_only(events, outputFile+'_queries.txt')
    save_queries_by_user(events, outputFile+'_queries_by_user.txt')
    '''
    normalized_queries = normalize_query(queries)
    dump_normalized_queries(normalized_queries, outputFile+'_normalized_queries.txt')
    clustered_queries1 = clustering1(normalized_queries)
    clustered_queries2 = clustering2(normalized_queries)
    print(clustered_queries2)
    '''
    print("Done")





