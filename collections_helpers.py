def merge_counts_dictionaries(counts, document_events_count, document_events_stat):
    """
    Merges dictionaries for opened links counts.

    Args:
        counts (dict): The dictionary to store opened links counts.
        document_events_count (int): The count of opened documents.
        document_events_stat (dict): The dictionary containing the position distribution.

    Returns:
        dict: A dictionary containing the merged counts.
    """
    if document_events_count in counts:
        for key, value in document_events_stat.items():
            if key in counts[document_events_count]:
                counts[document_events_count][key] += value
            else:
                counts[document_events_count][key] = value
    else:
        counts[document_events_count] = document_events_stat

    return counts


def add_dictionaries(counts, additional_dictionary):
    """
    Adds values from an additional dictionary to the counts dictionary.

    Args:
        counts (dict): The dictionary to store counts.
        additional_dictionary (dict): The dictionary with additional counts.

    Returns:
        dict: The updated counts dictionary.
    """
    for key, value in additional_dictionary.items():
        if key in counts:
            if isinstance(value, dict):
                counts[key] = merge_counts_dictionaries(counts[key], key, value)
            elif isinstance(value, list):
                counts[key] = counts.get(key, []) + value
            elif isinstance(value, int):
                counts[key] = counts.get(key, 0) + value
        else:
            counts[key] = value

    return counts

def add_simple_dictionaries(counts, additional_dictionary):
    """
    Adds values from an additional dictionary to the counts dictionary.

    Args:
        counts (dict): The dictionary to store counts.
        additional_dictionary (dict): The dictionary with additional counts.

    Returns:
        dict: The updated counts dictionary.
    """
    for key, value in additional_dictionary.items():
        if key in counts:
            if isinstance(value, dict):
                counts[key] = merge_counts_dictionaries(counts[key], key, value)
            elif isinstance(value, list):
                counts[key] = counts.get(key, []) + value
            elif isinstance(value, int):
                counts[key] = counts.get(key, 0) + value
        else:
            counts[key] = value

    return counts


def condense_dictionary(dictionary):
    """
    Condenses a dictionary by grouping keys (11..20) (21..100) (101..).

    Args:
        dictionary (dict): The dictionary to condense.

    Returns:
        dict: A condensed dictionary with unique keys.
    """
    condensed_dict = {}
    for key, value in dictionary.items():
        if key < 11:
            new_key = key
        elif key < 21:
            new_key = 11
        elif key < 101:
            new_key = 21
        else:
            new_key = 101
        if new_key not in condensed_dict:
            if isinstance(value, dict):
                # If the value is a dictionary, first condense it just like the main dictionary
                condensed_value = condense_dictionary(value)
                condensed_dict[new_key] = condensed_value
            else:
                condensed_dict[new_key] = value
        else:
            if isinstance(value, dict):
                # If the value is a dictionary, first condense it just like the main dictionary
                condensed_value = condense_dictionary(value)
                condensed_dict = merge_counts_dictionaries(condensed_dict, new_key, condensed_value)
            elif isinstance(value, list):
                condensed_dict[new_key] = condensed_dict.get(new_key, []) + value
            elif isinstance(value, int):
                condensed_dict[new_key] = condensed_dict.get(new_key, 0) + value
    return condensed_dict


def condense_third_dictionary(dictionary):
    """
    Condenses a dictionary by grouping keys (11..20) (21..100) (101..).

    Args:
        dictionary (dict): The dictionary to condense.

    Returns:
        dict: A condensed dictionary with unique keys.
    """
    condensed_dict = {}
    for key, value in dictionary.items():
        if key < 11:
            new_key = key
        elif key < 21:
            new_key = 11
        elif key < 101:
            new_key = 21
        else:
            new_key = 101
        if new_key not in condensed_dict:
            condensed_dict[new_key] = value
        else:
            if isinstance(value, dict):
                condensed_dict = merge_counts_dictionaries(condensed_dict, new_key, value)
            elif isinstance(value, list):
                condensed_dict[new_key] = condensed_dict.get(new_key, []) + value
            elif isinstance(value, int):
                condensed_dict[new_key] = condensed_dict.get(new_key, 0) + value
    return condensed_dict


def print_dictionary(dictionary):
    """
    Prints a dictionary in a readable format.

    Args:
        dictionary (dict): The dictionary to print.
    """
    for key, value in sorted(dictionary.items()):
        print(f"{key}: {value}")

