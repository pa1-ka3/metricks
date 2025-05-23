import plotly.graph_objects as graph

'''
source = [0, 1, 1, 0, 3, 3, 2, 2]
target = [4, 6, 4, 5, 5, 6, 5, 6]
value5 = [6, 3, 3, 2, 2, 2, 1, 1, 1]

labels5 = ["0", "1", "2", "3", "4", "5", "6"]

fig = graph.Figure(data=[graph.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels5,
        color="blue"
    ),
    link=dict(
        source=source5,  # indices correspond to labels, eg A1, A2, A1, B1, ...
        target=target5,
        value=value5
    ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()
'''

def make_sources_fromsearches(first_column):
    """
    Creates a list of sources for the Sankey diagram based on the first column.

    Args:
        first_column: {dict} Searches in session.

    Returns:
        list: A list of sources for the Sankey diagram.
    """
    sources = []
    for i, search in enumerate(first_column):
        sources.append(i)
    return sources


def make_source_labels(first_column):
    """
    Creates a map of labels for the Sankey diagram based on the first column.

    Args:
        first_column: {dict} Searches in session.

    Returns:
        dict: A map of sources for the Sankey diagram.
    """
    labels_map = {}
    position = 0
    for i in sorted(first_column.keys()):
        labels_map[i] = position
        position += 1
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
    position = 0
    for i in sorted(opened_links_cumulative.keys()):
        labels_map[i] = position
        position += 1
    return labels_map


def make_source_target_value_relations(first_column_labels, second_column_labels, second_column):
    """
    Creates a dictionary of relations between sources and targets for the Sankey diagram.

    Args:
        first_column_labels: {dict} Searches in session.
        second_column_labels: {dict} Documents actions (views/openings) in one search.
        second_column: {dict} Documents actions (views/openings) in one search.
    Returns:
        dict: A dictionary of relations between sources and targets for the Sankey diagram.
    """
    sources = []
    targets = []
    values = []
    targets_shift = len(first_column_labels)

    for searches in sorted(second_column.keys()):
        source_item = first_column_labels[searches]
        openings_stat = second_column[searches]
        for opened_label in sorted(openings_stat.keys()):
            sources.append(source_item)
            target_item = second_column_labels[opened_label] + targets_shift
            targets.append(target_item)
            #opened = openings_stat[opened_label]
            opened = 1
            values.append(opened)

    # Аб’яднаем у спіс кортэжаў і адсартыруем па source
    links = sorted(zip(sources, targets, values), key=lambda x: x[0])

    # Раздзелім назад
    sources_sorted, targets_sorted, values_sorted = zip(*links)

    relations_dict = dict(
            source=sources_sorted,
            target=targets_sorted,
            value=values_sorted
        )
    return relations_dict


def get_positions(first_column_labels_map, second_column_labels_map):
    """
    Creates a list of positions for the Sankey diagram based on the first column and second column.

    Args:
        first_column_labels_map: {dict} Searches in session.
        second_column_labels_map: {dict} Documents actions (views/openings) in one search.

    Returns:
        tuple: A tuple containing two lists of positions for the Sankey diagram.
    """
    x = []
    y = []
    position = 0.0
    for i in sorted(first_column_labels_map.keys()):
        x.append(0)
        y.append(position)
        position += 0.2

    position = 0.0
    for i in sorted(second_column_labels_map.keys()):
        x.append(1)
        y.append(position)
        position += 0.2

    return x, y


def draw_diagram(first_column, second_column, second_column_cumulative, third_column):
    """
    Draws a Sankey diagram using Plotly.

    Args:
        first_column: {dict} Searches in session.
        second_column: {dict} Documents actions (views/openings) in one search grouped by search.
        second_column_cumulative: {dict} Documents actions (views/openings) in one search across all collection.
        third_column: {list} Opened document position in one search.
    """
    first_column_labels_map = make_source_labels(first_column)
    second_column_labels_map = make_target_labels(second_column_cumulative)
    labels = sorted(first_column_labels_map.keys()) + sorted(second_column_labels_map.keys())
    print(labels)

    x, y = get_positions(first_column_labels_map, second_column_labels_map)

    relations_dict = make_source_target_value_relations(first_column_labels_map, second_column_labels_map, second_column)

    fig = graph.Figure(data=[graph.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            x=x,
            y=y,
            color="blue"
        ),
        link=relations_dict)])

    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    fig.show()
