import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

from task3.bool_search.__main__ import InvertedIndex


def calculate_term_frequency(path: Path, vocab):
    tf_matrix = []
    all_docs = os.listdir(path)
    for document_number, doc in enumerate(all_docs):
        arr = np.zeros(len(vocab))
        with open(path / doc, encoding='utf-8') as f:
            words_in_document = f.read().split("\n")
            for i, word in enumerate(vocab):
                arr[i] = words_in_document.count(word)
        tf_matrix.append(list(map(lambda x: x / len(words_in_document), arr)))
    return np.array(tf_matrix)


def calculate_inverse_document_frequency(index, n_docs=101):
    idf_per_word_in_vocab = np.zeros(len(index))
    for i, word in enumerate(index.keys()):
        idf_per_word_in_vocab[i] = math.log(n_docs / float(len(index[word])))
    return idf_per_word_in_vocab


def tf_idf(tf, idf):
    tf_idf_matrix = np.zeros((tf.shape[1], tf.shape[0]))

    for word_i, row in enumerate(tf.T):
        for doc_i, column in enumerate(row):
            tf_idf_matrix[word_i][doc_i] = column * idf[word_i]

    return tf_idf_matrix


def to_dataframe(arr, set_of_words):
    df = pd.DataFrame(arr)
    dict_of_indexes = dict()

    for i, word in enumerate(set_of_words):
        dict_of_indexes[i] = word

    return df.rename(index=dict_of_indexes)


def main(args):
    try:
        parameters = {"-index": args[args.index("-index") + 1]}
        base = Path(parameters["-index"])
        inverse_index = InvertedIndex(index=None)
        inverse_index.from_pages(base)
        inverse_index = inverse_index.index

        set_of_words = list(inverse_index.keys())

        tf_result = calculate_term_frequency(base / "processed", set_of_words)

        tf_df = to_dataframe(tf_result.T, set_of_words)
        tf_df.to_csv(base / "tf.csv")
        print(tf_df.head(10))

        idf_out = calculate_inverse_document_frequency(inverse_index)
        idf_df = pd.DataFrame.from_dict({k: v for k, v in zip(inverse_index.keys(), idf_out)}, orient='index')
        idf_df.to_csv(base / "idf.csv")
        print(idf_df.head(10))

        tf_idf_out = tf_idf(tf_result, idf_out)
        tf_idf_df = to_dataframe(tf_idf_out, set_of_words)
        tf_idf_df.to_csv(base / "tf_idf.csv")
        print(tf_idf_df.head(10))
    except (IndexError, KeyError) as e:
        pass


if __name__ == '__main__':
    main(["-index", "C:/Users/User/PycharmProjects/infosearch/index2"])

