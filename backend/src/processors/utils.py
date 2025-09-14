"""
This module provides utility functions used across multiple tasks in the project.

It includes helper methods for:
- Reading and cleaning data from CSV and JSON files
- Handling string and word processing operations
- Reusable data structures (e.g., defaultdict configurations)
- Other general-purpose operations used by the logic and task modules
"""

# Import python library:
import csv
import re
import json
from collections import defaultdict


def open_csv_format_for_clean_text(file_path: str) -> list[list[str]]:
    """
    This function receives a path to a CSV file and returns the text column
    as a list of lists.
    :param file_path:
    :return:
    """
    result = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        try:
            text_index = header.index('text')
        except ValueError:
            raise Exception("the text column is not present in the CSV file")

        for row in reader:
            text = row[text_index]
            words = text.split()
            result.append(words)

    return result


def remove_punctuations(string: str) -> str:
    """
    Remove all punctuation from a string, leaving only letters and numbers.
    :param string:
    :return:
    """
    fixed_word = re.sub(r'[^a-zA-Z0-9 ]', ' ', str(string))
    return fixed_word


def convert_lower(string: str) -> str:
    """
    Convert a string to lowercase
    :param string:
    :return:
    """
    return string.lower()


def remove_whitespace(string: str) -> str:
    """
    Remove extra whitespace from a string.
    :param string:
    :return:
    """
    return " ".join(string.split())


def flatten_list(nested_list: list[list[str]]) -> list[str]:
    """
    Flatten a nested list into a single list.
    :param nested_list:
    :return:
    """
    return [word for sublist in nested_list for word in sublist]


def clean_string(string: str) -> str:
    """
    Clean a string by removing punctuations, converting to lowercase,
    removing specific words, and removing extra whitespace.
    :param string:
    :return:
    """
    string = remove_punctuations(string)
    string = convert_lower(string)
    string = remove_whitespace(string)
    return string


def remove_empty_sent(string_list: list[list[str]]) -> list[list[str]]:
    """
    Remove empty sentences from a list of lists.
    :param string_list:
    :return:
    """
    return [sub_list for sub_list in string_list if sub_list and sub_list != ['']]


def turn_list_to_single_str(sentence_list: list[list[str]]) -> list[list[str]]:
    """
    Convert each sentence in a list of lists to a list of words.
    :param sentence_list:
    :return:
    """
    return [sublist[0].split() for sublist in sentence_list]


def remove_empty_str_from_list(string_list: list[str]) -> list[str]:
    """
    thus func remove any empty string from a list of strings.
    :param string_list:
    :return:
    """
    no_empty_str_list = []
    for string in string_list:
        if string != '':
            no_empty_str_list.append(string)
    return no_empty_str_list


def remove_empty_names(string_list: list[list[str]]) -> list[list[str]]:
    """
    this func receives a list and returns a list with no empty names
    :param string_list:
    :return:
    """
    if not string_list[0]:
        return False

    return True


def strip_name_list(string: str | None = None) -> str:
    """
    A placeholder clean_string function for this example.
    :param string:
    :return:
    """
    if string is None:
        string = []
    if string == ['']:
        return []
    else:
        return string.strip()


def task1_into_lists(json_filename_path: str) -> tuple[list, list[str]]:
    """
    This function reads a JSON file and extracts the processed sentences and names.
    :param json_filename_path
    :return: A tuple containing (list of sentences, list of names)
        """
    with open(json_filename_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    sentences = data.get("Question 1", {}).get("Processed Sentences", [])
    names = data.get("Question 1", {}).get("Processed Names", [])

    return sentences, names


def count_common_words(sentence_list: str, n: int) -> dict[str, list[list[str]]]:
    """
    this func receives a list of sentences and returns a dict of the count of each seq according to
    the given N
    :return: dict[str, int]
    """
    words_dict = {}
    for sublist in sentence_list:
        if len(sublist) < n:
            continue
        for i in range(len(sublist) - n + 1):
            new_word = ' '.join(sublist[i:i + n])
            if new_word in words_dict:
                words_dict[new_word] += 1
            else:
                words_dict[new_word] = 1

    sorted_dict = {key: words_dict[key] for key in sorted(words_dict)}

    return sorted_dict


def count_names_in_sentence(sentence_list: list[list[str]], name_list: list[str]) -> dict[str, int]:
    """
    this func counts how many times each word occurs in the sentence and returns a dict of main name as
    key and the number of times it occurs in the sentence as value
    :param sentence_list:
    :param name_list:
    :return:
    """
    return_dict = {}
    for full_name in name_list:
        if not full_name or not full_name[0]:
            continue
        main_name = " ".join(full_name[0])
        return_dict[main_name] = 0

    for sublist in sentence_list:
        for full_name in name_list:
            main_name = " ".join(full_name[0])
            for name in full_name[0]:
                return_dict[main_name] += sublist.count(name)

            if full_name[1]:
                for other_name in full_name[1]:
                    return_dict[main_name] += sublist.count(other_name)

    return_dict = {key: value for key, value in return_dict.items() if value != 0}
    return_dict = {k: return_dict[k] for k in sorted(return_dict)}
    return return_dict


def change_dict_into_list_q3(sentence_list: list[list[str]], name_list: list[list[str]]) -> list[list[str]]:
    """
    this func changes dictionary into list according to the wanted format
    :param sentence_list:
    :param name_list:
    :return:
    """
    count_name_dict = count_names_in_sentence(sentence_list, name_list)
    return_list = []
    for key, value in count_name_dict.items():
        return_list.append([key, value])
    return return_list


def remove_duplicates_seq(kseq_keys_list: str) -> list[str]:
    """
    Removes duplicate strings from a list while maintaining order.
    :param kseq_keys_list: A list of strings.
    :return: A list with duplicates removed.
    """
    seen = set()
    cleaned_list = []
    for item in kseq_keys_list:
        if item not in seen:
            seen.add(item)
            cleaned_list.append(item)
    return cleaned_list


def generate_all_seq_from_words_list(words_list: list[str], n: int | None = None)\
        -> list[list[str]]:
    """
    this func returns a dict of all possible seq when the key is the seq and the value is
    all the santances
    :return:
    """
    res = []
    for start in range(len(words_list)):
        for end in range(start + 1, len(words_list) + 1):
            sub_list = words_list[start:end]
            if n is not None and len(sub_list) > n:
                break
            res.append(sub_list)
    return res


def count_seq_in_sentence(sentence_seq_dict: dict[str, list[str]], kseq_keys_list: list[str])\
        -> list[list[str]]:
    """
    this func search all seq according to the seq_list in the sentences and returns a dict when the
    key is the seq and the value is all the santances
    the O(1) - because I created a dict of all possible seq when the key is the seq and the value is all the santances
    and in this func I created a set of all the possible seq in the list so the loop if only to search
    for the correct seq matching to the key
    :return: dict[str,list[str]]
    """
    res = []
    sentence_keys_set = set(sentence_seq_dict.keys())
    for seq in sorted(kseq_keys_list):
        if seq in sentence_keys_set:
            seq_item = [seq, sentence_seq_dict[seq]]
            res.append(seq_item)

    return res


def generate_all_search_seq_from_sentences_list(sentences_list: list[str], n: int | None = None)\
        -> dict[str, list[str]]:
    """
    this func returns a dict of all possible seq when the key is the seq and the value is
    all the santances
    :return:
    """
    seq__all_sentences_dict = defaultdict(list)
    sentences_list.sort()
    for words_list in sentences_list:
        combinations = generate_all_seq_from_words_list(words_list, n)
        for seq in combinations:
            seq__all_sentences_dict[' '.join(seq)].append(words_list)
    return seq__all_sentences_dict


def check_names_in_sentences(sentence_list: list[list[str]], names_list: list[list[str]])\
        -> dict[str, list[str]]:
    """
    this func checks names in sentences and returns a dict of names as keys and lists of
    santances as values
    :return: dict[main_name,list[sentence]]
    """
    return_dict = {}
    sorted_sentences_list = sorted(sentence_list, key=lambda x: x[0])
    for full_name in names_list:
        main_name = " ".join(full_name[0])
        return_dict[main_name] = []

    for sublist in sorted_sentences_list:
        for full_name in names_list:
            main_name = " ".join(full_name[0])
            for name in full_name[0]:
                if name in sublist:
                    return_dict[main_name].append(sublist)

            for other_name in full_name[1]:
                if other_name in sublist:
                    return_dict[main_name].append(sublist)

    for key in return_dict:
        return_dict[key] = [list(sublist) for sublist in {tuple(sublist) for sublist in return_dict[key]}]

    for key in return_dict:
        return_dict[key] = sorted(return_dict[key])

    return_dict = {key: value for key, value in return_dict.items() if value != []}
    return_dict = {k: return_dict[k] for k in sorted(return_dict.keys())}

    return return_dict


def all_possible_pairs_list(names_list: list[list[str]]) -> list[list[str]]:
    """
    this func creates all possible pairs
    :param names_list:
    :return:
    """
    pairs = []
    for i in range(len(names_list)):
        for j in range(i + 1, len(names_list)):
            pairs.append([names_list[i], names_list[j]])

    return pairs


def check_move_edges(dict_pairs: dict[str, int], t: int) -> list[list[list[str]]]:
    """
    this func returns all the edges that are larger
    :param dict_pairs:
    :param t:
    :return:
    """
    edges = []
    for names, count in dict_pairs.items():
        if count >= t:
            names_list = [name.split() for name in names]
            edges.append(names_list)

    return edges


def sort_pairs_list(pairs_dict: dict[str, int]) -> dict[str, list[str]]:
    """
    this func sort a list of pairs
    :return:
    """
    sorted_data = [sorted(pair, key=lambda x: ' '.join(x)) for pair in pairs_dict]
    sorted_data.sort(key=lambda pair: (' '.join(pair[0]), ' '.join(pair[1])))

    return sorted_data


def sort_groups(groups_list: list[list[str]]) -> list[list[str]]:
    """
    this func sorts the groups of connected sentences in the graph and returns a dict of the
    number of group as key and all sorted sentences as values.
    :return:
    """
    for sublist in groups_list:
        sublist.sort()

    return sorted(groups_list, key=lambda x: (len(x), x))
