import os

def test_sorter():
    files = ["zip.ls.s3.0038591f-f3e0-491a-9268-d4fd70a33247.2025-05-01T12.55.part52.txt",
             "zip.ls.s3.0080de27-e976-4d32-9962-1c84dc7ae24d.2025-05-01T12.51.part14.txt",
             "zip.ls.s3.0096e8e4-48e6-411a-adec-0038157b2889.2025-05-01T12.26.part78.txt",
             "zip.ls.s3.01e7273f-dcae-4e05-b156-f322bd171028.2025-05-07T01.17.part478.txt",
             "zip.ls.s3.02a549d6-fc45-46dc-9878-cd74c74e5699.2025-05-01T12.26.part22.txt",
             "zip.ls.s3.032b3fcf-a15a-4e3a-bf08-104fa7bac0b9.2025-05-06T10.23.part279.txt"]
    # Sort the files based on the date in the filename
    sorted_files = sorted(files, key=lambda x: (x.split('.')[4], x.split('.')[5], x.split('.')[6]))
    # Print the sorted files
    for file in sorted_files:
        print(file)


def directories_sorter(root_path):

    sorted_dirs = get_sorted_dirs(root_path)

    return get_sorted_paths(sorted_dirs)


def get_sorted_paths(sorted_dirs):
    paths = []
    for direntry in sorted_dirs:
        # print("dirname: {0}".format(dirname))
        dir_path = direntry.path

        for root, _, files in os.walk(dir_path):
            for filename in files:
                if not filename.endswith('.txt'):
                    continue
                path = os.path.join(root, filename)
                print(path)
                paths.append(path)
    return paths


def get_sorted_dirs(root_path):
    if not os.path.exists(root_path):
        print("Directory does not exist: {0}".format(root_path))
        return []

    dirs = [d for d in os.scandir(root_path)]
    sorted_dirs = []
    try:
        # Sort the directories based on the date in the directory name
        sorted_dirs = sorted(dirs, key=lambda x: (
            x.name.split('.')[4],
            x.name.split('.')[5],
            x.name.split('.')[6])
                             )
    except IndexError as e:
        print("IndexError: {0}".format(e))
    return sorted_dirs


def get_sorted_files(root_path):
    files = directories_sorter(root_path)
    return files


if __name__ == "__main__":
    files = get_sorted_files(r'c:\Data\ClickData')  # just for test
