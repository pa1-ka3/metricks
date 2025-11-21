import argparse
import bz2
import json
import pandas
import os
from sys import argv


def get_json_data(dates, data_folder):
    """
    Returns:
        Dictionary in format: {query_norm: {id_doc:
                                            ({position, query_original, positive, is_test_user}, ... ), ... }, ... }
    """
    data = {}
    for d in dates:
        print(d)
        json_file = fr'{data_folder}\{d}\.json\out.documents.json'
        if not os.path.isfile(json_file):
            print(f'File not found: {json_file}')
            continue
        with open(json_file, 'r', encoding="utf-8") as fl:
            for line in fl:
                doc = json.loads(line)
                q_norm = doc['q_norm']
                id_doc = doc['doc']
                positive = doc['positive']
                test_user = doc['usr_test']

                # skip empty queries
                if skip_empty_queries and (not q_norm or q_norm == 'none'):
                    continue

                # skip test users
                if skip_test_users and test_user:
                    continue

                if q_norm not in data:
                    data[q_norm] = {}
                if id_doc not in data[q_norm]:
                    data[q_norm][id_doc] = ()
                data[q_norm][id_doc] += ({'position': doc['position'],
                                          'query': doc['query'],
                                          'positive': positive,
                                          'test_user': test_user},)
    return data


"""  
* Start Block Get Queries
"""


def get_position(doc_values):
    """
    The function determine the most common (most frequent) position in a list of document values,
    Resolving ties by selecting the lowest position number.

    :param doc_values:
    :return:
    """
    positions = {}
    for doc_value in doc_values:
        position = doc_value['position']
        if position not in positions:
            positions[position] = 1
        else:
            positions[position] += 1
    fr_positions = [key for key, value in positions.items() if value == max(positions.values())]
    return min(fr_positions)


def get_query(doc_values):
    """
    The function identifies the most frequent query in a list of document values,
    It returns a tuple containing the most frequent query as a string,
               the total number of unique queries,
               the total number of document values processed,
               and the count of the most frequent query:
    :param doc_values:
    :return:
    """
    queries = {}
    for doc_value in doc_values:
        query = doc_value['query']
        if query not in queries:
            queries[query] = 1
        else:
            queries[query] += 1
    fq_index = max(queries, key=queries.get)
    return str(fq_index), len(queries), len(doc_values), queries[fq_index]


def change_identical_positions(documents):
    """
    The function renumerate the positions of documents to ensure that each document has a unique position.
    :param documents:
    :return:
    """
    positions = set()
    for doc in documents.keys():
        position = documents[doc]['position']
        while True:
            if position not in positions:
                positions.add(position)
                documents[doc]['position'] = position
                break
            else:
                position += 1


def get_queries(data, doc_count_limit):
    """
    This function processes a nested dictionary of query data to aggregate statistics and filter documents
    based on a minimum count threshold.
    It iterates over each normalized query (`q_norm`) and its associated documents,
    initializing counters for positive and negative clicks.
    For each document, it separates the values into negative and positive clicks using list comprehensions:

    ```python
    docs_negative = tuple(i for i in doc_values if i['positive'] == 0)
    docs_positive = tuple(i for i in doc_values if i['positive'] == 1)
    ```

    The function then checks if the combined count of positive and negative clicks for a
    document meets the specified `doc_count_limit`. If not, that document is skipped:

    ```python
    if (doc_negative_count + doc_positive_count)  < doc_count_limit:
        continue
    ```

    For documents that pass the threshold, their position is determined and stored, and their statistics are added to
    the `documents` dictionary.
    The function also accumulates all document values for the current query.

    After processing all documents for a query, it skips queries with no valid documents.
    It then uses a helper function to find the most frequent query string and sorts the documents by total click count
    and position:

    ```python
    documents= dict(sorted(documents.items(), key=lambda k: (-(k[1]['negative'] + k[1]['positive']), k[1]['position'])))
    ```

    Another helper function is called to adjust document positions if there are duplicates.
    The aggregated data for each query is stored in the `queries` dictionary,
    including the most frequent query string, document statistics, and total positive/negative counts.

    Finally, the function sorts all queries by their total click counts in descending order and returns
    the resulting dictionary.
    This approach ensures that only queries and documents with sufficient data are included,
    and the output is organized for further analysis or reporting.


    :param data:
    :param doc_count_limit:
    :return:
    """
    queries = {}
    # for q_norm, query_values in dict(sorted(data.items())).items():
    for q_norm, query_values in data.items():
        documents = {}
        query_doc_values = ()
        query_doc_negative_count = 0
        query_doc_positive_count = 0
        for doc, doc_values in query_values.items():

            docs_negative = tuple(i for i in doc_values if i['positive'] == 0)
            doc_negative_count = len(docs_negative)
            query_doc_negative_count += doc_negative_count

            docs_positive = tuple(i for i in doc_values if i['positive'] == 1)
            doc_positive_count = len(docs_positive)
            query_doc_positive_count += doc_positive_count

            # skip docs by limit
            if (doc_negative_count + doc_positive_count) < doc_count_limit:
                continue

            position = get_position(doc_values)
            query_doc_values += doc_values
            documents[doc] = {'negative': doc_negative_count,
                              'positive': doc_positive_count,
                              'orig_position': position,
                              'position': position}

        if not documents:
            continue

        # skip queries without positive documents
        # if query_doc_positive_count == 0:
        #    continue

        query, uniq_queries_count, queries_count, query_count = get_query(query_doc_values)
        documents = dict(sorted(documents.items(),
                                key=lambda k: (-(k[1]['negative'] + k[1]['positive']), k[1]['position'])))
        change_identical_positions(documents)
        queries[q_norm] = {'query': query,
                           'documents': documents,
                           'negative': query_doc_negative_count,
                           'positive': query_doc_positive_count}
    queries = dict(sorted(queries.items(), key=lambda k: (-(k[1]['negative'] + k[1]['positive']))))
    return queries


"""
* Start Block for Export baseline
*
"""


def max_position(query_value):
    max_value = None
    for doc in query_value['documents'].values():
        position = doc['position']
        if not max_value:
            max_value = position
        if position > max_value:
            max_value = position
    return max_value


def max_positive_negative(query_value):
    max_value = None
    for doc in query_value['documents'].values():
        positive = doc['positive']
        negative = doc['negative']
        diff = positive - negative
        if not max_value:
            max_value = diff
        if diff > max_value:
            max_value = diff
    return max_value


def export_baseline(queries, out_file, export_doc_count, export_query_count):
    """
    Short: The function processes queries and their associated documents,
    calculates scores based on positive/negative feedback,
    sorts and formats the results, and writes them to a file for further analysis or evaluation.

    Detailed: The function iterates over each query in the `queries` dictionary.
    For each query, it calculates the maximum position and maximum difference:

    ```python
    max_pos = max_position(query_value)
    max_diff = max_positive_negative(query_value)
    ```

    It then creates a list of predicted results, assigning a unique document ID for each position:

    ```python
    for i in range(0, max_pos):
        doc_id = '_' + f'{sample_id:F>7}' + '_' + f'{str(i+1):F>7}'
        predicted_results.append({'document': doc_id})
    ```

    For each document in the query, the code calculates a score based on the positive and negative values,
    using the defined ratios and counts.
    The scoring logic is nested and increases the score if certain thresholds are met:

    ```python
    if negative == 0 \
            or positive/negative >= ratio_positive_negative_division \
            or positive >= ratio_positive_count:
        score = 1
        if diff > 0:
            score = 2
            if diff / max_diff >= ratio_diff_maxdiff_division:
                score = 3
    ```

    The actual results are sorted by score (descending) and position (ascending),
    and then exported in a simplified format:

    ```python
    actual_results_sorted = sorted(actual_results,
                                   key=lambda k: (-(k['score']), k['position']))
    ```

    Finally, the function writes each query's export data as a JSON line to the output file,
    limiting the number of documents and queries if specified:

    ```python
    fl.write(json.dumps(export) + '\n')
    if sample_id == export_query_count:
        break
    ```

    :param queries:
    :param out_file:
    :param export_doc_count:
    :param export_query_count:
    :return:
    """

    with open(out_file, 'w', encoding="utf-8") as fl:
        # with bz2.open(out_file, "wt", encoding='utf-8') as fl:
        sample_id = 0
        for q_norm, query_value in queries.items():
            sample_id += 1
            query = query_value['query']
            max_pos = max_position(query_value)
            if max_pos == 0:
                max_pos = 1
            max_diff = max_positive_negative(query_value)

            predicted_results = []
            for i in range(0, max_pos):
                doc_id = '_' + f'{sample_id:F>7}' + '_' + f'{str(i+1):F>7}'
                predicted_results.append({'document': doc_id})

            actual_results = []
            for id, doc in query_value['documents'].items():
                position = doc['position']
                if position == 0:
                    position = 1
                positive = doc['positive']
                negative = doc['negative']
                diff = positive - negative
                score = 0
                if negative == 0 \
                        or positive/negative >= ratio_positive_negative_division \
                        or positive >= ratio_positive_count:
                    score = 1
                    if diff > 0:
                        score = 2
                        if diff / max_diff >= ratio_diff_maxdiff_division:
                            score = 3
                actual_results.append({'document': id, 'score': score, 'position': position})
                predicted_results[position-1] = {'document': id}

            actual_results_sorted = sorted(actual_results,
                                           key=lambda k: (-(k['score']), k['position']))

            actual_results_export = []
            for item in actual_results_sorted:
                actual_results_export.append({'document': item['document'], 'score': item['score']})

            # set empty predicted_results
            # predicted_results = []

            request = {"text": query}
            export = {'sample_id': sample_id,
                      'request': request,
                      'actual_results': actual_results_export,
                      'predicted_results': predicted_results}
            if export_doc_count > 0:
                export = {'sample_id': sample_id,
                          'request': request,
                          'actual_results': actual_results_export[0:export_doc_count],
                          'predicted_results': predicted_results[0:export_doc_count]}
            fl.write(json.dumps(export) + '\n')
            if sample_id == export_query_count:
                break


"""
* End Block for Export baseline
"""


#   --startDate="2025-08-01" --endDate="2025-08-30" --inputDir="c:\Data\ClickData_2025_08"
#   --outputDir="c:\Data\ClickData_results\search-quality\popular-docs"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputDir", help="points to click-data location")
    parser.add_argument("--outputDir", help="points to directory with results")
    parser.add_argument("--startDate", help="start date in format YYYY-MM-DD")
    parser.add_argument("--endDate", help="end date in format YYYY-MM-DD")
    args = parser.parse_args()

    if args.inputDir is None:
        exit("No inputPath provided")
    data_folder = args.inputDir

    if args.outputDir is None:
        exit("No outputPath provided")
    out_folder = args.outputDir

    if args.startDate is None:
        exit("No startDate provided")
    start_date = args.startDate

    if args.endDate is None:
        exit("No endDate provided")
    end_date = args.endDate

    doc_count_limit = 10
    out_file = rf'{out_folder}\adataset.{start_date}.{end_date}.json'

    skip_empty_queries = 1
    skip_test_users = 1

    # 0 - unlimit
    export_doc_count = 100  # 10

    # 0 - unlimit
    export_query_count = 1000  # 1000

    # ratio
    ratio_positive_negative_division = 0.25
    ratio_positive_count = 100
    ratio_diff_maxdiff_division = 0.8

    dates = [d.strftime('%Y-%m-%d') for d in pandas.date_range(start_date, end_date)]
    json_data = get_json_data(dates, data_folder)
    print(len(json_data))
    queries = get_queries(json_data, doc_count_limit)

    export_baseline(queries, out_file, export_doc_count, export_query_count)
    pack_to_bz(out_file, rf'{out_file}.bz2')

    export_queries(get_queries(json_data, 1), rf'{out_folder}\alldata.{start_date}.{end_date}.json', 0, 0)