import bz2
import json
import re


def get_combined_documents(etalon_dataset_file, tests_results_file, out_file):
    '''
    :param etalon_dataset_file: Etalon dataset file (adataset)
    :param tests_results_file: Tests result file
    :param out_file: Combined ethalon + tests in single file
    :return:
    '''

    isDocumentGlobalIdNumber = re.compile(r'[A-Z]{16}', re.IGNORECASE)

    runned_queries = []
    with open(tests_results_file, 'r', encoding='utf-8') as inF:
        for line in inF:
            item = json.loads(line.strip())
            runned_queries.append(item)

    with open(etalon_dataset_file, 'r', encoding='utf-8') as inF, \
            bz2.open(out_file, "wt", encoding='utf-8') as fl:
        for line in inF:
            item = json.loads(line.strip())
            query = item['request']['text']

            query_item = {}
            for q_item in runned_queries:
                if q_item['query'] == query:
                    query_item = q_item

            if not query_item:
                print(f'no query in runned queries, query: {query}')
                continue

            if not query_item['documents']:
                print(f'no documents for runned query: {query}')
                continue

            item['predicted_results'] = []
            for document in query_item['documents']:
                url = document['Url']
                doc_id = url.split("/")[-1]
                if isDocumentGlobalIdNumber.search(doc_id):
                    item['predicted_results'].append({'document': doc_id})
                else:
                    print(f'wrong document format: {doc_id}')

            fl.write(json.dumps(item) + '\n')