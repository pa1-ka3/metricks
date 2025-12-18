from .collections_helpers import merge_counts_dictionaries
from .constants import document_actions, doc_extra_actions
import queue


def collect_search_counts_in_sessions(counts, session_description):
    """
    Collects search counts in sessions.
    searches_count is the number of searches in the session

    <--- ToDo -- we have to distinguish search ang qta
    Opening from QTA - is valid positive search --->

    Args:
        session_description (tuple): The session description tuple.
        counts (dict): The dictionary to store search counts.

    Returns:
        dict: A dictionary with key - search counts in one session.
    """
    if not isinstance(session_description, tuple):
        return counts

    searches = session_description[1]
    searches_count = len(searches)
    if searches_count in counts:
        counts[searches_count] += 1
    else:
        counts[searches_count] = 1
    return counts


def collect_opened_links_in_searches(counts, session_description):
    """
    Collects {opened_links: searches_count} through sessions

    Args:
        session_description (tuple): The session description tuple.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary with key - opened links in one search
             {opened_links: searches_count} counts.

    Code definitions:
        session_description is a tuple with session_id and collection of searches
    """
    if not isinstance(session_description, tuple):
        return counts

    searches = session_description[1]

    for queryid, search in searches.items():
        document_events = set()  # analyze for every search
        active_search = False
        for event in search:
            if "documentvieweropened" in event \
                    or "documentviewed" in event:
                # Replace action name and get unique document attribute, e.g. re-1-10
                print("Processing event: {0}".format(event))
                if isinstance(event, tuple):
                    name = event[1]
                    document_events.add(name)
                else:
                    name = event.replace("documentvieweropened", "").replace("documentviewed", "")
                    document_events.add(name)
            if "downloadpdf" in event:
                active_search = True
        count = len(document_events)
        if count == 0 and active_search:
            count = 1
        if count in counts:
            counts[count] += 1
        else:
            counts[count] = 1
    return counts


def collect_opened_links_by_searchnumbers_in_session(counts, session_description):
    """
    Collects opened links (inkl. 0) in searches according to number of searches.

    Args:
        session_description (tuple): The session description tuple.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary of dictionaries,
         top key - search counts in one session,
          inner keys - opened links counts.
          {searches_count: {opened_links_count: count}}
    """
    if not isinstance(session_description, tuple):
        return counts

    searches = session_description[1]
    searches_count = len(searches)

    for queryid, search in searches.items():
        document_events = set()
        active_search = False
        for event in search:
            if "documentvieweropened" in event or "documentviewed" in event:
                document_events.add(
                   event.replace("documentvieweropened", "").replace("documentviewed", ""))
            if "downloadpdf" in event:
                active_search = True

        document_events_count = len(document_events)
        if document_events_count == 0 and active_search:
            document_events_count = 1
        counts.setdefault(searches_count, {}).setdefault(document_events_count, 0)
        counts[searches_count][document_events_count] += 1

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
        try:
            segments = position_description.split("-")
        except Exception as e:
            print(f"Error splitting position description: {position_description}, error: {e}")
            continue

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
        session_description (tuple): The session description dictionary.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary of dict containing the opened links counts.
        dict: A dictionary of dictionaries,
         top key - search counts in one session,
          inner keys - opened links counts.
          {searches_count: {opened_links_count: count}}
    """
    if not isinstance(session_description, tuple):
        return counts

    session_events = session_description[1]
    searches_count = len(session_events)

    for events in session_events.values():
        document_events = set()
        document_events_stat = {}
        active_search = False
        for event in events:
            if "downloadpdf" in event:  # calculate all downloadpdf events in the session
                if "downloadpdf" not in document_events_stat:
                    document_events_stat["downloadpdf"] = 1
                else:
                    document_events_stat["downloadpdf"] += 1
                active_search = True
                continue
            if "documentvieweropened" in event \
                    or "documentviewed" in event:
                name = event.replace("documentvieweropened", "").\
                    replace("documentviewed", "")
                document_events.add(name)
                active_search = True
        if active_search:
            document_events_stat = position_distribution(document_events_stat, document_events)
        else:
            document_events_stat = {'0': 1}

        counts = merge_counts_dictionaries(counts, searches_count, document_events_stat)
    return counts


def collect_opened_documents_positions_distribution_in_searches_v2(counts, session_description):
    """
    Collects opened links distribution in searches according to number of searches.

    Args:
        session_description (tuple): The session description dictionary.
        counts (dict): The dictionary to store opened links counts.

    Returns:
        dict: A dictionary of dict containing the opened links counts.
        dict: A dictionary of dictionaries,
         top key - search counts in one session,
          inner keys - opened links counts.
          {searches_count: {opened_links_count: count}}
    """
    if not isinstance(session_description, tuple):
        return counts

    session_events = session_description[1]
    searches_count = len(session_events)

    for events in session_events.values():
        document_events = set()
        document_events_stat = {}
        active_search = False
        for event in events:
            if "downloadpdf" in event:  # calculate all downloadpdf events in the session
                if "downloadpdf" not in document_events_stat:
                    document_events_stat["downloadpdf"] = 1
                else:
                    document_events_stat["downloadpdf"] += 1
                active_search = True
                continue
            if "documentvieweropened" in event \
                    or "documentviewed" in event:
                name = event[1]  # here already event description like 're-1-10'
                if name is None:
                    name = 'qt-1-1'  # if None, then it is qta event, so hardcode its position
                document_events.add(name)
                active_search = True
        if active_search:
            document_events_stat = position_distribution(document_events_stat, document_events)
        else:
            document_events_stat = {'0': 1}

        counts = merge_counts_dictionaries(counts, searches_count, document_events_stat)
    return counts


def separate_qta_searches(searches):
    """
    Args:
        searches (dict): The dictionary containing searches.

    Returns:
        tuple: queue of QTA search, queue of other searches.
    """
    qta_search = None
    qta_q = None
    q = queue.Queue()
    for searchid, search in searches.items():
        if searchid.startswith('0 '):  # QTA search session id starts with '0 '
            qta_search = search
        else:
            q.put((searchid, search))
    if qta_search is not None:
        qta_q = queue.Queue()
        for item in qta_search:
            if item[0] == 'documentviewed':
                qta_q.put(item)
    return qta_q, q


def append_accumulations(accumulations, session_description):
    """
    Append session description to accumulations without any processing.

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        session_description (tuple): The session description tuple.

    Returns:
        dict: The updated accumulations dictionary.
    """

    accumulations[session_description[0]] = session_description[1]
    return accumulations


def distribute_qta_searches(qta_search, other_searches):
    """
    Distribute QTA searches across searches in 're' (researcher)

    Args:
        qta_search (queue): The queue of QTA documentviews.
        other_searches (queue): The queue of other searches.

    Returns:
        List: The updated searches list.
    """
    if other_searches.empty():
        # No other searches, return QTA search only
        qta_searches_list = []
        while not qta_search.empty():
            value = qta_search.get()
            qta_searches_list.append(value)
        return {'0': qta_searches_list}

    '''''
    if qta_search is None:
        # No QTA searches, return other searches as original dict
        result = {}
        while not other_searches.empty():
            key, value = other_searches.get()
            result[key] = value
        return result
    '''

    if qta_search is not None:
        while not qta_search.empty():
            item_left = qta_search.get()
            item_right = other_searches.get()
            item_right[1].append(item_left)
            other_searches.put(item_right)

    distributed_searches = {}
    while not other_searches.empty():
        key, value = other_searches.get()
        distributed_searches[key] = value

    return distributed_searches


def preprocess_events(accumulations, session_description):
    """
    Distribute QTA searches across searches in 're' (researcher)

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        session_description (tuple): The session description tuple.

    Returns:
        dict: The updated accumulations dictionary.
    """
    if not isinstance(session_description, tuple):
        return accumulations

    qta_searches, other_searches = separate_qta_searches(session_description[1])
    #if qta_searches is None:
    #    return append_accumulations(accumulations, session_description)

    searches = distribute_qta_searches(qta_searches, other_searches)

    accumulations[session_description[0]] = searches

    return accumulations


def select_events_with_not_opened(accumulations, session_description):
    """
    Get events were no documents were clicked.

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        session_description (tuple): The session description tuple.

    Returns:
        dict: The updated accumulations dictionary.
    """
    if not isinstance(session_description, tuple):
        return accumulations

    clicked = False
    clicked_events = {'documentvieweropened', 'documentviewed', 'downloadpdf'}
    for searchid, events in session_description[1].items():
        if any(event[0] in clicked_events for event in events):
            clicked = True
            break

    if not clicked:
        accumulations[session_description[0]] = session_description[1]
    return accumulations


def select_topmost_click_in_searches(accumulations, session_description):
    """
    Collect the only topmost clicked document in each search. It could be qtq like 'qt-1-1' or re-1-10

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        session_description (tuple): The session description tuple.

    Returns:
        dict: The updated accumulations dictionary. looks like  { search_id : topmost_click}
        in case no document was clicked - 9999 position {search_id : 9999}
    """
    if not isinstance(session_description, tuple):
        return accumulations

    clicked_events = {'documentvieweropened', 'documentviewed'}
    topmost_clicks = {}
    for searchid, events in session_description[1].items():
        topmost_click = 9999  # Default to 9999 if no document is clicked
        for event in events:
            if not isinstance(event, tuple):
                continue
            if event[0] not in clicked_events:
                continue
            if event[1] is None:
                continue
            if event[1] == '':
                continue

            click_position_label = event[1].split('-')[1]
            if click_position_label.isdigit():
                click_position = int(click_position_label)
                topmost_click = min(topmost_click, click_position)

        if topmost_click == 9999:
            # there was no active click found, should check for extra actions
            for event in events:
                if not isinstance(event, tuple):
                    continue
                if event[1] is None:
                    continue
                if event[1] == '':
                    continue
                if event[0] in doc_extra_actions:
                    topmost_click = 1
                    break

        topmost_clicks[searchid] = topmost_click

    if topmost_clicks:
        accumulations[session_description[0]] = topmost_clicks

    return accumulations


def collect_first_click(accumulations, session_description):
    """
    Collect the first clicked document in each session.

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        session_description (tuple): The session description tuple.

    Returns:
        dict: The updated accumulations dictionary.
    """
    if not isinstance(session_description, tuple):
        return accumulations

    clicked_events = {'documentvieweropened', 'documentviewed'}
    first_click = None
    for searchid, events in session_description[1].items():
        for event in events:
            if not isinstance(event, tuple):
                continue
            if event[1] is None:
                continue
            if event[1] == '':
                continue
            if event[0] in clicked_events:
                first_click = event
                break
        if first_click is not None:
            break

    try:
        if (first_click is not None) and isinstance(first_click, tuple):
            first_click_description = first_click[1]  # e.g. 're-1-10'
            description_components = first_click_description.split('-')
            position = 0
            if len(description_components) == 3 and description_components[1].isdigit():
                position = int(description_components[1])
            if description_components[1] == 'qt':
                position = 1
            if position > 0:
                accumulations[session_description[0]] = position
    except Exception as e:
        print(f"Error processing first click: {first_click}, error: {e}")
    return accumulations


def calculate_click_through(accumulations, position_threshold):
    """
    Calculate click-through rate based on topmost click positions.

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        position_threshold (int): filtering value - only positions less or equal will be counted

    Returns:
        float: rate of clicks with position higher than The updated accumulations dictionary with click-through rates.
    """

    counted_clicks = 0
    total_clicks = 0

    for searches_session in accumulations.values():
        for search_topmost_click in searches_session.values():
            total_clicks += 1
            if search_topmost_click <= position_threshold:
                counted_clicks += 1

    click_through_rate = 0.0
    if total_clicks > 0:
        click_through_rate = counted_clicks / total_clicks

    result = {}
    result['click_through_rate'] = click_through_rate
    result['counted_clicks'] = counted_clicks
    result['total_clicks'] = total_clicks

    return result


def filter_extra_actions_only(accumulations, session_description):
    """
    Keep sessions with extra actions only (linksaved, bookmarked etc).

    Args:
        accumulations (dict): The dictionary to store accumulated statistics.
        session_description (tuple): The session description tuple.

    Returns:
        dict: The updated accumulations dictionary.
    """
    if not isinstance(session_description, tuple):
        return accumulations

    for searchid, events in session_description[1].items():
        for event in events:
            if event[0] in document_actions:
                return accumulations

    # the rest should be extra actions only
    accumulations[session_description[0]] = session_description[1]
    return accumulations
