import datetime
from dateutil.relativedelta import *
from .sort_click_data_files import get_sorted_dirs, get_sorted_paths


def get_dirs_week_period(period_end, period_start, input_click_path_base):
    """
    Get the directories for the week period (from previous Sunday to the last Saturday) based on the given date.
    :param period_end:
    :param period_start:
    :param input_click_path_base:
    :return: sorted list of directories
    """

    period_end_month = period_end.strftime("%Y-%m")
    end_month_path = input_click_path_base + '\\' + period_end_month
    print(end_month_path)

    start_month_path = input_click_path_base + '\\' + period_start.strftime("%Y-%m")
    print(start_month_path)

    if end_month_path == start_month_path:
        sorted_dirs = get_sorted_dirs(end_month_path)
    else:
        l1 = get_sorted_dirs(start_month_path)
        l2 = get_sorted_dirs(end_month_path)
        sorted_dirs = l1 + l2

    first_index_search = (i for i, v in enumerate(sorted_dirs) if is_interval_starter(period_start, v.name))
    first_dir_index = next(first_index_search, len(sorted_dirs) - 1)  # if not found, take the last index

    last_index_search = (i for i, v in enumerate(reversed(sorted_dirs)) if is_interval_finisher(period_end, v.name))
    last_dir_index = len(sorted_dirs) - 1 - next(last_index_search, -1)

    print(sorted_dirs[first_dir_index])
    print(sorted_dirs[last_dir_index])

    selected_dirs = sorted_dirs[first_dir_index:last_dir_index + 1]

    return selected_dirs


def get_period_boundaries(today):
    today = today.replace(hour=0, minute=0, second=0)
    period_end = today + relativedelta(weekday=SA(-1))  # get last Saturday
    print(period_end)
    period_start = period_end - relativedelta(days=7)
    print(period_start)
    return period_end, period_start


def is_interval_starter(period_start_data, dir_name):
    """
    Directories already sorted, so we can just check if the date in the directory name is
    greater than period start date.
    :param period_start_data:
    :param dir_name:
    :return:
    """
    try:
        dir_date_str = dir_name.split('.')[4]
        # Data is in format 2025-08-01T09.33, so we need to split by 'T' and take the first part and parse
        dir_date_str = dir_date_str.split('T')[0]
        dir_data = datetime.datetime.strptime(dir_date_str, "%Y-%m-%d")

        if dir_data < period_start_data:
            return False
        else:
            return True
    except IndexError as e:
        print("IndexError: {0}".format(e))
        return False


def is_interval_finisher(period_end_data, dir_name):
    """
    Directories already sorted, so we can just check if the date in the directory name is
    less than period start date.
    :param period_end_data:
    :param dir_name:
    :return:
    """
    try:
        dir_date_str = dir_name.split('.')[4]
        # Data is in format 2025-08-01T09.33, so we need to split by 'T' and take the first part and parse
        dir_date_str = dir_date_str.split('T')[0]
        dir_data = datetime.datetime.strptime(dir_date_str, "%Y-%m-%d")

        if dir_data < period_end_data:
            return True
        else:
            return False
    except IndexError as e:
        print("IndexError: {0}".format(e))
        return False


if __name__ == "__main__":
    day = datetime.datetime(year=2026, month=2, day=10)
    #input_click_path_base = r"\\fsxnetapp01.ihsglobal.local\goldfire-arch-prod\ewb-click-data\prod"
    #day = datetime.datetime(year=2025, month=8, day=9)
    input_click_path_base = r"c:\Data\ClickData_2025"
    period_end, period_start = get_period_boundaries(day)
    dirs = get_dirs_week_period(period_end, period_start, input_click_path_base)  # just for test
    files = get_sorted_paths(dirs)
    # Print the sorted paths
    print('---------------')
    for path in files:
        print(path)
