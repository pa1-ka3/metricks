import holoviews as hv
import pandas as pd
import panel as pn
from collections_helpers import condense_dictionary, print_dictionary, condense_third_dictionary

hv.extension('bokeh')


def make_source_labels(first_column):
    """
    Creates a map of labels for the Sankey diagram based on the first column.

    Args:
        first_column: {dict} Searches in session.

    Returns:
        dict: A map of sources for the Sankey diagram.
    """
    labels_map = {}
    for i in sorted(first_column.keys()):
        labels_map[i] = 'Searches_{0}'.format(i)
    return labels_map


def make_target_labels(opened_links_cumulative):
    """
    Creates a map of labels for the Sankey diagram based on the opened_links.

    Args:
        opened_links_cumulative: {dict} Searches in session.

    Returns:
        dict: A map of targets for the Sankey diagram.
    """
    labels_map = {}
    for i in sorted(opened_links_cumulative.keys()):
        labels_map[i] = 'Opened_{0}'.format(i)
    return labels_map


def make_third_labels_map(third_column):
    """
    Creates a map of labels for the third column of the Sankey diagram.

    Args:
        third_column: {dict} Opened document position in one search.

    Returns:
        dict: A map of third column labels for the Sankey diagram.
    """
    labels_map = {
        1: "1",
        "1": "1",
        2: "2",
        "2": "2",
        3: "3",
        "3": "3",
        4: "4",
        "4": "4",
        5: "5",
        "5": "5",
        6: "6",
        "6": "6",
        7: "7",
        "7": "7",
        8: "8",
        "8": "8",
        9: "9",
        "9": "9",
        10: "10",
        "10": "10",
        11: "(11-20)",
        "(11-20)": "(11-20)",
        21: "(21-100)",
        "(21-100)": "(21-100)",
        101: "(101-...)",
        "(101-...)": "(101-...)",
        "downloadpdf": "downloadpdf"
    }

    return labels_map


def make_source_target_value_relation(first_column_labels, second_column_labels, second_column):
    """
    Creates a dictionary of relations between sources and targets for the Sankey diagram.

    Args:
        first_column_labels: {dict} Searches in session.
        second_column_labels: {dict} Documents actions (views/openings) in one search.
        second_column: {dict} Documents actions (views/openings) in one search.
    Returns:
        list: A list of tuples represent relations between sources, targets and values for the Sankey diagram.
    """

    links = []

    for searches in sorted(second_column.keys()):
        source_label = first_column_labels[searches]
        openings_stat = second_column[searches]
        for opened_number in sorted(openings_stat.keys()):
            target_label = second_column_labels[opened_number]
            opened = openings_stat[opened_number]
            link_vector = (source_label, target_label, opened)

            links.append(link_vector)

    return links


def get_labels_list(column_labels_map):
    """
    Creates a list of labels for the Sankey diagram.

    Args:
        column_labels_map: {dict} number actions : Label for actions.

    Returns:
        list: A list of labels for the Sankey diagram.
    """
    labels_list = []
    for i in sorted(column_labels_map.keys()):
        labels_list.append(column_labels_map[i])
    return labels_list

def get_third_column_labels_list(third_column_labels_map):
    """
    Creates a list of labels for the third column of the Sankey diagram.

    Args:
        third_column_labels_map: {dict} Opened document position in one search.

    Returns:
        list: A list of labels for the third column of the Sankey diagram.
    """
    labels_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                   "(11-20)", "(21-100)", "(101-...)", "downloadpdf"]

    return labels_list


def draw_diagram(first_column, second_column, second_column_cumulative, third_column):
    """
    Draws a Sankey diagram using Holoviews.

    Args:
        first_column: {dict} Searches in session.
        second_column: {dict} Documents actions (views/openings) in one search grouped by search.
        second_column_cumulative: {dict} Documents actions (views/openings) in one search across all collection.
        third_column: {list} Opened document position in one search.
    """

    # {dict} Key(int number searches in session): value(string Node Label - number searches in session)
    first_column_condensed = condense_dictionary(first_column)
    print_dictionary(first_column_condensed)
    first_column_labels_map = make_source_labels(first_column_condensed)

    # {dict} Key(int number openings in searches): value(string Node Label - number openings in searches)
    second_column_cumulative_condensed = condense_dictionary(second_column_cumulative)
    print_dictionary(second_column_cumulative_condensed)
    second_column_labels_map = make_target_labels(second_column_cumulative_condensed)

    second_column_condensed = condense_dictionary(second_column)
    relations_list = make_source_target_value_relation(first_column_labels_map,
                                                       second_column_labels_map,
                                                       second_column_condensed)

    # Define nodes order (in reality it doesn't force the order, but it helps to approximately locate nodes)
    labels = get_labels_list(first_column_labels_map) + get_labels_list(second_column_labels_map)
    print(labels)

    if third_column:
        third_column_condensed = condense_third_dictionary(third_column)
        print_dictionary(third_column_condensed)
        third_column_labels_map = make_third_labels_map(third_column_condensed)
        opens_relations_list = make_source_target_value_relation(second_column_labels_map,
                                                                 third_column_labels_map,
                                                                 third_column_condensed)
        relations_list.extend(opens_relations_list)
        third_column_labels = get_third_column_labels_list(third_column_labels_map)
        labels.extend(third_column_labels)

    hv.extension('bokeh')

    ordered_labels = labels

    # In nodes have to use 'name' instead of 'label'
    nodes = [{'name': label} for label in ordered_labels]
    nodes_df = pd.DataFrame(nodes)

    # Links: values in source/target must comply 'name'
    links = relations_list
    links_df = pd.DataFrame(links, columns=['source', 'target', 'value'])

    # Create Sankey (firs links, then nodes)
    sankey = hv.Sankey((links_df, nodes_df))

    # Options
    sankey.opts(
        width=1800, height=768,
        node_color='name',  # 'name', because now it is key
        edge_color='source',
        label_position='left',
        cmap='Category10',
        labels='name',
        tools=['hover']
    )

    pn.extension()
    pn.panel(sankey).save(r'c:\Temp\1\sankey_output8.html', embed=True)
