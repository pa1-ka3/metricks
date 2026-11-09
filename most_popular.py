import os
from collections import defaultdict
from nltk.corpus import stopwords
from .create_baseline import EnsureDir


def get_normalized_query(query, stop_words):
    segments = query.split()
    result_segments = [segment for segment in segments if segment not in stop_words]
    normalized = ' '.join(result_segments)
    return normalized


def load_normalised_accumulation(path):
    accumulator = defaultdict(int)
    stop_words = set(stopwords.words('english'))

    with open(path, 'r', encoding='utf-8') as input:
        for row_line in input:
            try:
                line = row_line.strip()
                segments = line.split('\t')
                if len(segments) == 2:
                    normalized_query = get_normalized_query(segments[0].strip('"').strip("'").strip(), stop_words)
                    accumulator[normalized_query] += int(segments[-1])
                elif len(segments) == 3:
                    normalized_query = get_normalized_query(segments[1].strip('"').strip("'").strip(), stop_words)
                    accumulator[normalized_query] += int(segments[-1])
            except Exception as e:
                print(row_line)
    return accumulator


def get_cluster_with_counts(normalized_accumulator, path):
    with open(path, 'r', encoding='utf-8') as input:
        loaded_cluster = defaultdict(int)
        for row_line in input:
            line = row_line.strip()
            query = line.strip('"').strip("'").strip()
            count = normalized_accumulator.get(query, 0)
            loaded_cluster[query] = count
        return loaded_cluster


def save_cluster_with_counts(cluster, output_path):
    EnsureDir(output_path)
    with open(output_path, 'w', encoding="utf-8") as outFile:
        for query in cluster.keys():
            outFile.write(f"{query}\t{cluster[query]}\n")


if __name__ == "__main__":
    accu_path = r"c:\Data\ClickData_queries\acumulated\accumulator.txt"
    normalized_accumulator = load_normalised_accumulation(accu_path)

    input_folder = r"c:\Data\ClickData_queries\clusters6a"
    output_folder = r"c:\Data\ClickData_queries\clusters_with_counts"
    for root, _, files in os.walk(input_folder):
        for filename in files:
            if not filename.endswith('.txt'):
                continue
            path = os.path.join(root, filename)
            print(path)
            cluster = get_cluster_with_counts(normalized_accumulator, path)
            output_path_orig = path.replace(input_folder, output_folder)
            save_cluster_with_counts(cluster, output_path_orig)

            path_by_counts = os.path.join(root, filename.replace('.txt', '_by_counts.txt'))
            output_path_by_counts = path_by_counts.replace(input_folder, output_folder)
            cluster_by_counts = dict(sorted(cluster.items(), key=lambda item: item[1], reverse=True))
            save_cluster_with_counts(cluster_by_counts, output_path_by_counts)

