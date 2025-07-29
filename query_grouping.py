import argparse
from sort_click_data_files import get_sorted_files
from analyser import analyse_logfile, test_subaccounts, document_actions
import json


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

    if "sessionid" not in payload:
        return acc
    session_id = payload["sessionid"]
    if session_id != session_id_filter:
        return acc

    if "istestaccount" in payload and payload["istestaccount"]:
        return acc

    if "subaccountid" in payload:
        subaccount_id = payload["subaccountid"]
        if subaccount_id is None:
            return acc
        if subaccount_id.startswith(tuple(test_subaccounts)):
            return acc

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

    query_text = payload.get("query", "None")

    if session_id not in acc:
        acc[session_id] = {}
        acc[session_id][query_id] = []
        acc[session_id][query_id].append(query_text)
    else:
        if query_id not in acc[session_id]:
            acc[session_id][query_id] = []
            acc[session_id][query_id].append(query_text)
        else:
            acc[session_id][query_id].append(query_text)

    return acc

def get_document_actions_with_queries(acc, event_description):
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

    if "sessionid" not in payload:
        return acc
    session_id = payload["sessionid"]


    if "istestaccount" in payload and payload["istestaccount"]:
        return acc

    subaccount_id = ""
    if "subaccountid" in payload:
        subaccount_id = payload["subaccountid"]
        if subaccount_id is None:
            return acc
        if subaccount_id.startswith(tuple(test_subaccounts)):
            return acc

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

    #geoip = get_geoip(event_description)
    query_id = "{0} {1}".format(query_id, subaccount_id)

    query_text = payload.get("query", "None")

    if session_id not in acc:
        acc[session_id] = {}
        acc[session_id][query_id] = []
        acc[session_id][query_id].append(query_text)
    else:
        if query_id not in acc[session_id]:
            acc[session_id][query_id] = []
            acc[session_id][query_id].append(query_text)
        else:
            acc[session_id][query_id].append(query_text)

    return acc


def get_geoip(event_description):
    """
    Extracts geoip information from the event description.

    Args:
        event_description (dict): The event description dictionary from log file.

    Returns:
        str: A string containing the geoip information.
    """
    if "geoip" not in event_description:
        return "NoGeoip"
    geoip_description = event_description["geoip"]

    plain_description = ""

    if "country_name" in geoip_description:
        plain_description += geoip_description["country_name"]

    space_evaluate = lambda description: ' ' if len(description) > 0 else ''

    if "city_name" in geoip_description:
        plain_description += space_evaluate(plain_description) + geoip_description["city_name"]

    if "region_name" in geoip_description:
        plain_description += space_evaluate(plain_description) + geoip_description["region_name"]

    return plain_description


session_id_filter = "sessionid"


def save_filtered_events_file(events, outputFile):
    # Print the event chains
    with open(outputFile, "w", encoding='utf-8') as outfile:
        for session, values in events.items():
            if isinstance(values, dict):
                #if len(values.items()) < 10:
                #    continue
                sub_lines = ["{0} : {1}".format(queryid, event_descr) for queryid, event_descr in values.items() if len(event_descr)> 10]
                whole_value = ',\n              '.join(sub_lines)
            else:
                # This is a list of events
                whole_value = ', '.join(values)
            if len(whole_value) == 0:
                continue
            save_line(outfile, session, whole_value)
        save_line(outfile, 20*'-', 20*'-')

        for session, values in events.items():
            if isinstance(values, dict):
                if len(values.items()) < 100:
                    continue
                sub_lines = ["{0} : {1}".format(queryid, event_descr) for queryid, event_descr in values.items()]
                whole_value = ',\n              '.join(sub_lines)
            else:
                # This is a list of events
                whole_value = ', '.join(values)
            if len(whole_value) == 0:
                continue
            save_line(outfile, session, whole_value)
    # Print the event chains


def save_line(outfile, session, whole_value):
    line = f"{session} : {whole_value}"
    print(line.encode("utf-8"))
    outfile.write(line + "\n")


def get_grouped_by_queryid_dump(acc, event_description):
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

    if "sessionid" not in payload:
        return acc
    session_id = payload["sessionid"]
    if session_id != session_id_filter:
        return acc

    if "istestaccount" in payload and payload["istestaccount"]:
        return acc

    if "subaccountid" in payload:
        subaccount_id = payload["subaccountid"]
        if subaccount_id is None:
            return acc
        if subaccount_id.startswith(tuple(test_subaccounts)):
            return acc

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

    print(json.dumps(payload, indent=4))
    #print(hash(frozenset(payload.items())))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clickPath", help="points to click-data location")
    parser.add_argument("--outputFile", help="points to file with results")
    parser.add_argument("--sessionid", help="sessionid to filter events by session ID, default is 'sessionid'")
    args = parser.parse_args()

    if args.clickPath is None:
        exit("No clickPath provided")
    clickPath = args.clickPath

    if args.outputFile is None:
        exit("No outputFile provided")
    outputFile = args.outputFile

    if args.sessionid is not None:
        session_id_filter = args.sessionid

    files = get_sorted_files(clickPath)

    events = {}   # accumulator for statistics
    for file in files:
        #events = analyse_logfile(file, events, get_grouped_by_queryid_dump)
        events = analyse_logfile(file, events, get_document_actions_with_queries)

    save_filtered_events_file(events, outputFile)
