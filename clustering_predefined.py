#from clustering import get_queries_set
import regex as re

def get_queries_set(path):
    queries = set()
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            queries.add(line.strip())
    return queries

def get_boolean_queries(queries):
    boolean_queries = set()
    other = set()
    for query in queries:
        if ("<and>" in query) or ("<in>" in query) or ("<or>" in query) or ("<not>" in query):
            boolean_queries.add(query)
        else:
            other.add(query)
    return boolean_queries, other


def get_qta_search(input_queries):
    patterna = r"\b[A-Za-z0-9-\/.\+]{2,}(?:\s+[A-Za-z0-9\/.-]+)*\s* - \s*[^;\n]+(?:;[^;\n]+)*"
    patter2 = r"\b[A-Za-z0-9-\/.]{2,}(?:\s+[A-Za-z0-9.\/-]+)*\s* - \s*[^;\n]+(?:;[^;\n]+)*"
    #pattern = r"\b[A-Za-z0-9-\/.\+]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s* - \s*[^;\n]+(?:;[^;\n]+)*"
    pattern = r"\b[A-Za-z]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s* - \s*[^;\n]+(?:;[^;\n]+)*"

    qta_queries = set()
    other_q = set()
    for query in input_queries:
        matches = re.findall(pattern, query)
        if not matches:
            other_q.add(query)
            continue

        segments = query.split(' - ')
        if len(segments[1]) < 7:
            other_q.add(query)
            continue

        if matches[0] != query:
            other_q.add(query)
            continue

        qta_queries.add(query)

    return qta_queries, other_q


def get_abbreviature_search(input_queries):

    patter1 = r"\b[A-Za-z]{2,}(?:\s+[A-Za-z0-9/().,'\"-]+)*\s*[-–:]\s*[^;\n]+(?:;[^;\n]+)*"
    pattern = r"^[A-Za-z\-0-9]{2,}$"
    qta_queries = set()
    other_q = set()
    for query in input_queries:
        query = query.strip()
        matches = re.findall(pattern, query)
        if not matches:
            other_q.add(query)
            continue

        segments = query.split(' - ')
        if len(segments) > 1 and len(segments[1]) < 30:
            other_q.add(query)
            continue

        if matches[0] != query:
            other_q.add(query)
            continue

        qta_queries.add(query)

    return qta_queries, other_q


def get_standard_like_qta(input_queries):

    pattern = r"\b[A-Za-z0-9-\/.\+ ():]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s* - \s*[^;\n]+(?:;[^;\n]+)*"
    #pattern = r"^[A-Za-z\-0-9]{2,}$"
    qta_queries = set()
    other_q = set()
    for query in input_queries:
        query = query.strip()
        matches = re.findall(pattern, query)
        if not matches:
            other_q.add(query)
            continue

        segments = query.split(' - ')
        if len(segments) > 1 and len(segments[-1]) < 10:
            other_q.add(query)
            continue

        if matches[0] != query:
            other_q.add(query)
            continue

        qta_queries.add(query)

    return qta_queries, other_q


def has_numbers(input):
    return any(char.isdigit() for char in input)


def get_document_number_search(input_queries):
    patter1 = r"\b[A-Za-z0-9-\/.\+]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s*$"
    pattern = r"\b[A-Za-z0-9-\/.\+: ]{2,}(?: +[A-Za-z0-9\/().-]+)*$"
    doc_number_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        if " - " in query:
            other_q2.add(query)
            continue

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        if matches[0] != query:
            other_q2.add(query)
            continue

        if not has_numbers(query):
            other_q2.add(query)
            continue

        doc_number_queries.add(query)

    return doc_number_queries, other_q2


def get_digits_only(input_queries):
    patter1 = r"\b[A-Za-z0-9-\/.\+]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s*$"
    pattern = r"^[0-9]{2,}$"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        if matches[0] != query:
            other_q2.add(query)
            continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_letters_only(input_queries):

    pattern = r"^[a-z ]*$"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        if matches[0] != query:
            other_q2.add(query)
            continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_wildcard_search(input_queries):

    doc_wildcard_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()
        if '*' not in query:
            other_q2.add(query)
            continue

        doc_wildcard_queries.add(query)

    return doc_wildcard_queries, other_q2


def get_wildcard_question_search(input_queries):

    doc_wildcard_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()
        if '?' not in query:
            other_q2.add(query)
            continue

        if len(query) > 20:
            other_q2.add(query)
            continue

        doc_wildcard_queries.add(query)

    return doc_wildcard_queries, other_q2


def get_other_standard1(input_queries):

    pattern = r"\b[A-Za-z0-9-\/.\+ ():]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s* - \s*[^;\n]+(?:;[^;\n]+)*"
    #pattern = r"^[A-Za-z\-0-9]{2,}$"
    qta_queries = set()
    other_q = set()
    for query in input_queries:
        query = query.strip()
        matches = re.findall(pattern, query)
        if not matches:
            other_q.add(query)
            continue

        if matches[0] != query:
            other_q.add(query)
            continue

        qta_queries.add(query)

    return qta_queries, other_q


def get_document_number_v1_search(input_queries):
    patter1 = r"\b[A-Za-z0-9-\/.\+]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s*$"
    pattern1 = r"\b[A-Za-z0-9-\/.\+: ]{2,}(?: +[A-Za-z0-9\/().-]+)*$"
    pattern = r"\b[A-Za-z0-9-\/.\+ ():]{2,}(?:\s+[A-Za-z0-9\/().-]+)*\s*$"
    doc_number_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        #if (" - " in query) or (" - " in query):
        #    other_q2.add(query)
        #    continue

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        #if matches[0] != query:
        #    other_q2.add(query)
        #    continue

        if not has_numbers(query):
            other_q2.add(query)
            continue

        doc_number_queries.add(query)

    return doc_number_queries, other_q2


def get_letters_ext(input_queries):
    pattern = r"^[a-z ,\'\"().:&-]*$"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        if matches[0] != query:
            other_q2.add(query)
            continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2

def get_letters_ext2(input_queries):
    pattern = r"^[a-z ,\'\"().\&‘’\/–]*$"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        if matches[0] != query:
            other_q2.add(query)
            continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_letters_ext3(input_queries):
    pattern = r"^[a-z0-9 ,\'\"().\&‘’\/\\+\–]*$"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        if matches[0] != query:
            other_q2.add(query)
            continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_some_standard_(input_queries):
    pattern = r"^\b(aami |aashto |aci |aia/nas |ams |ansi|api|asce|asm |ashrae|asme|astm|aws|awwa|bpvc|bs |bsi |can/|code |csa |din|dnv|ds|iec |ieee |ipc|isa|iso|j-std|mil |mil-|mil_|nas |nfpa |sae |usp)[a-z0-9 ,_()\.\&\/\\+\-–]*"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        #if matches[0] != query:
        #    other_q2.add(query)
        #    continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_some_standard_2(input_queries):
    pattern = r"^a-a[_-][0-9_a-z-]*[\S]|^ams[0-9_a-z-]*[\S]|^an[0-9a-z]*[\S]|^as[\/-]nzs[0-9_a-z:. -]*[\S]|^as[_-]?[0-9_a-z:. -]*[\S]"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        #if matches[0] != query:
        #    other_q2.add(query)
        #    continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_some_standard_3(input_queries):
    pattern = r"^bs[_-][0-9_a-z-]*[\S]|^bsi[0-9_a-z\/-]*[\S]|^bsen[0-9a-z]*[\S]|^c[0-9]+[0-9_a-z:. -]*[\S]|^^d[0-9][0-9_a-z:. -]*[\S]|^do[_-]?[0-9][0-9_a-z:. -]*[\S]|^di[_-][acdeifgmnpst]{2,4}[_-][0-9][0-9_a-z:. -]*[\S]|^e[gi]_[0-9]+[0-9_a-z:. -]*[\S]|^en[ _]?[0-9]+[0-9_a-z:. ‐]*[\S]*|^en iec [0-9]+[0-9_a-z:. ‐]*[\S]*|^en[ _]iso[ _][0-9]+[0-9_a-z:. ‐]*[\S]*|^es_[0-9]+[0-9_]*[\S]*"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        #if matches[0] != query:
        #    other_q2.add(query)
        #    continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def get_some_standard_4(input_queries):
    pattern = r"^iec[_]?[0-9][0-9_a-z:.\/-]*[\S]|^j[0-9][0-9_a-z:.\/-]*[\S]|^nas[0-9][0-9_a-z: .\/-]*[\S]*|^mil[_–-][0-9_a-z.\/\–]*[\S]*"
    doc_digits_queries = set()
    other_q2 = set()
    for query in input_queries:
        query = query.strip()

        matches = re.findall(pattern, query)
        if not matches:
            other_q2.add(query)
            continue

        #if matches[0] != query:
        #    other_q2.add(query)
        #    continue

        doc_digits_queries.add(query)

    return doc_digits_queries, other_q2


def test_qta():
    phrases = set()
    phrases.add('bsi bs en 60601-1-2 + a1 - medical electrical equipment part 1-2: general requirements basic safety essential performance - collateral standard: electromagnetic disturbances - requirements tests - amd: march 31, 2021')
    phrases.add('uic 612-0 (edition 1) - driver machines intefaces emu-dmu, locomotives driving coaches - functional system requirements associated harmonised driver machine interfaces')

    q, o = get_qta_search(phrases)
    for qta in o:
        print(qta)

def test_document_number():
    phrases = set()
    phrases.add('10222-5 - steel forgings pressure purposes - part 5: martensitic, austenitic austenitic-ferritic stainless steels')
    #phrases.add('uic 612-0 (edition 1) - driver machines intefaces emu-dmu, locomotives driving coaches - functional system requirements associated harmonised driver machine interfaces')

    q, o = get_document_number_search(phrases)
    for qta in o:
        print(qta)


def save_cluster(cluster, clusters_result):
    with open(clusters_result, 'w', encoding='utf-8') as result:
        for item in sorted(cluster):
            result.write(item + '\n')


if __name__ == "__main__":

    #test_qta()
    test_document_number()

    path = r'c:\Data\ClickData_queries\acumulated\accumulator_normalized.txt'
    #path = r'c:\Data\ClickData_queries\acumulated\cluster_other.txt'
    queries = get_queries_set(path)
    boolean_queries, other = get_boolean_queries(queries)
    save_cluster(boolean_queries, r'c:\Data\ClickData_queries\acumulated\cluster_boolean.txt')

    print(len(queries))
    print("boolean queries {0}".format(len(boolean_queries)))
    print(len(other))

    document_letters, other = get_letters_only(other)
    print("letters only {0}".format(len(document_letters)))
    print(len(other))
    save_cluster(document_letters, r'c:\Data\ClickData_queries\acumulated\cluster_letters_only.txt')

    document_digits, other = get_digits_only(other)
    print("digits only {0}".format(len(document_digits)))
    print(len(other))
    save_cluster(document_digits, r'c:\Data\ClickData_queries\acumulated\cluster_digits.txt')
    
    qta_queries, other = get_qta_search(other)
    #for qta in qta_queries:
    #    print(qta)
    save_cluster(qta_queries, r'c:\Data\ClickData_queries\acumulated\cluster_qta.txt')
    print("qta queries {0}".format(len(qta_queries)))
    print(len(other))

    like_qta_queries, other = get_standard_like_qta(other)
    save_cluster(like_qta_queries, r'c:\Data\ClickData_queries\acumulated\cluster_likeqta.txt')
    print("like_qta queries {0}".format(len(like_qta_queries)))
    print(len(other))

    abbrev_standards, other = get_abbreviature_search(other)
    save_cluster(abbrev_standards, r'c:\Data\ClickData_queries\acumulated\cluster_abbreviature.txt')
    print("abbrev_standards {0}".format(len(abbrev_standards)))
    print(len(other))

    wildcards, other = get_wildcard_search(other)
    save_cluster(wildcards, r'c:\Data\ClickData_queries\acumulated\cluster_wildcards.txt')
    print("wildcards {0}".format(len(wildcards)))
    print(len(other))

    wildcards_question, other = get_wildcard_question_search(other)
    save_cluster(wildcards_question, r'c:\Data\ClickData_queries\acumulated\cluster_wildcards_question.txt')
    print("wildcards question {0}".format(len(wildcards_question)))
    print(len(other))

    other_standards1, other = get_other_standard1(other)
    save_cluster(other_standards1, r'c:\Data\ClickData_queries\acumulated\cluster_other_standards1.txt')
    print("other standards1 {0}".format(len(other_standards1)))
    print(len(other))

    document_number, other = get_document_number_search(other)
    save_cluster(document_number, r'c:\Data\ClickData_queries\acumulated\cluster_document_number.txt')
    print("document number {0}".format(len(document_number)))
    print(len(other))

    document_number1, other = get_document_number_v1_search(other)
    save_cluster(document_number1, r'c:\Data\ClickData_queries\acumulated\cluster_document_number_v1.txt')
    print("document number v1 {0}".format(len(document_number1)))
    print(len(other))

    some_standard, other = get_some_standard_(other)
    save_cluster(some_standard, r'c:\Data\ClickData_queries\acumulated\cluster_some_standard.txt')
    print("some_standard {0}".format(len(some_standard)))
    print(len(other))

    some_standard2, other = get_some_standard_2(other)
    save_cluster(some_standard2, r'c:\Data\ClickData_queries\acumulated\cluster_some_standard2.txt')
    print("some_standard2 {0}".format(len(some_standard2)))
    print(len(other))

    some_standard3, other = get_some_standard_3(other)
    save_cluster(some_standard3, r'c:\Data\ClickData_queries\acumulated\cluster_some_standard3.txt')
    print("some_standard3 {0}".format(len(some_standard3)))
    print(len(other))

    some_standard4, other = get_some_standard_4(other)
    save_cluster(some_standard4, r'c:\Data\ClickData_queries\acumulated\cluster_some_standard4.txt')
    print("some_standard4 {0}".format(len(some_standard4)))
    print(len(other))

    letters_ext, other = get_letters_ext(other)
    save_cluster(letters_ext, r'c:\Data\ClickData_queries\acumulated\cluster_letters_ext.txt')
    print("letters ext {0}".format(len(letters_ext)))
    print(len(other))

    letters_ext2, other = get_letters_ext2(other)
    save_cluster(letters_ext2, r'c:\Data\ClickData_queries\acumulated\cluster_letters_ext2.txt')
    print("letters ext2 {0}".format(len(letters_ext2)))
    print(len(other))

    letters_ext3, other = get_letters_ext3(other)
    save_cluster(letters_ext3, r'c:\Data\ClickData_queries\acumulated\cluster_letters_ext3.txt')
    print("letters ext3 {0}".format(len(letters_ext3)))
    print(len(other))

    save_cluster(other, r'c:\Data\ClickData_queries\acumulated\cluster_other.txt')


