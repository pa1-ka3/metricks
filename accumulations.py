

def collect_search_counts_in_sessions(counts, session_description):
    """
    Collects search counts in sessions.
    searches_count is the number of searches in the session and also downloadpdf from direct link or qta search

    Args:
        session_description (tuple): The session description tuple.
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
        session_description (tuple): The session description tuple.
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
                        or "documentviewed" in event:
                    # Replace action name and get unique document attribute, e.g. re-1-10
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
