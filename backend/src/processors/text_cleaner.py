"""
this file receives a csv file and returns a clean csv file with clean sentences
"""

# ---------- imports ----------
import utils
import csv


class CleanSentences:
    """
       A class responsible for cleaning and preprocessing a list of sentences,
       such as removing punctuation, converting to lowercase, and removing unwanted words.

       Attributes:
           filename_mock_data (str): Path to the input CSV file containing sentences.
       """

    def __init__(self, filename_mock_data: str):
        self.filename_mock_data = filename_mock_data


    def generate_clean_sentences_list(self) -> list[list[str]]:
        """
        This function generates a clean sentences list from a CSV file.
        :return:
        """
        sentences = utils.open_csv_format_for_clean_text(self.filename_mock_data)

        cleaned_sentences = []
        for sentence in sentences:
            clean_sen = utils.clean_string(sentence)
            words = clean_sen.split()
            cleaned_sentences.append(words)

        cleaned_sentences = utils.remove_empty_sent(cleaned_sentences)
        return cleaned_sentences


def clean_text(file_path: str, cleaned_sentences: list[list[str]], output_path: str):
    """
    this function cleans a list of tokenized sentences, using a list of words to remove.
    :param file_path:
    :param cleaned_sentences:
    :param output_path:
    :return:
    """

    with open(file_path, mode='r', encoding='latin-1', newline='') as infile, \
            open(output_path, mode='w', encoding='latin-1', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(header)

        try:
            text_index = header.index('text')
        except ValueError:
            raise Exception("the text column is not present in the CSV file")

        for i, row in enumerate(reader):
            cleaned_text = " ".join(cleaned_sentences[i])
            row[text_index] = cleaned_text
            writer.writerow(row)


def generate_clean_tweets_csv(input_csv_path: str, output_csv_path: str):
    """
    this function generates a clean tweets csv file from a list of tokenized sentences.
    :param input_csv_path:
    :param output_csv_path:
    :return:
    """
    clean_sen = CleanSentences(input_csv_path)
    clean_sen = clean_sen.generate_clean_sentences_list()
    clean_text(input_csv_path, clean_sen, output_csv_path)


if __name__ == '__main__':
    generate_clean_tweets_csv("mock_data.csv", "cleaned_tweets.csv")