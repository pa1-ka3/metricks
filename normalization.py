import nltk
from nltk.corpus import stopwords


def get_queries_set():
    queries = set()
    path = r'c:\Data\ClickData_queries\acumulated\accumulator_10.txt'
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            queries.add(line.strip())
    return queries


def normalize_query(queries_set):
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    print(stop_words)

    normalizwd_queries_set = set()

    for query in queries_set:
        segments = query.split()
        result_segments = []
        for segment in segments:
            if segment in stop_words:
                continue
            else:
                result_segments.append(segment)
        normalized = ' '.join(result_segments)
        normalizwd_queries_set.add(normalized)

    return normalizwd_queries_set


def dump_normalized_queries(queries_set, outputFile):
    with open(outputFile, 'w', encoding="utf-8") as outFile:
        for query in sorted(queries_set):
            outFile.write(f"{query}\n")


if __name__ == "__main__":
    queries = get_queries_set()
    normal_queries = normalize_query(queries)
    normalized_path = r'c:\Data\ClickData_queries\acumulated\accumulator_normalized_10.txt'
    dump_normalized_queries(normal_queries, normalized_path)