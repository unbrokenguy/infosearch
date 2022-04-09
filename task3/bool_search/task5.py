from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from task3.bool_search import InvertedIndex
from task3.bool_search.task4 import tf_idf

import pymorphy2

MORPH = pymorphy2.MorphAnalyzer()


def to_normal_form(words):
    return list(map(lambda word: MORPH.parse(word)[0].normal_form, words))


def tf(vocab, list_of_words):

    tf_matrix = []

    arr = np.zeros(len(vocab))

    for i, word in enumerate(vocab):
        arr[i] = list_of_words.count(word)

    tf_matrix.append(list(map(lambda x: x / len(list_of_words), arr)))

    return np.array(tf_matrix)


def search(text, base):
    list_of_words = to_normal_form(text.lower().split(" "))
    inverse_index = InvertedIndex(index=None)
    inverse_index.from_pages(base)
    inverse_index = inverse_index.index
    set_of_words = list(inverse_index.keys())
    tf_of_search = tf(set_of_words, list_of_words)

    idf = pd.read_csv(base / "idf.csv").to_numpy().T[1]

    tf_idf_of_search = tf_idf(tf_of_search, idf).T[0]

    tf_idf_of_all_docs = pd.read_csv(base / "tf_idf.csv").to_numpy().T
    cosines = list(zip(range(0, 101), cosine_similarity(tf_idf_of_all_docs[1:], tf_idf_of_search.reshape(1, -1)).T[0]))

    return sorted(cosines, key=lambda tup: tup[1], reverse=True)


def get_relevant_docs(text, top_n, base):
    relevant_docs = search(text, base)
    return relevant_docs[:top_n]


def main(args):
    try:
        parameters = {"-index": args[args.index("-index") + 1], "-text": args[args.index("-text") + 1]}
        base = Path(parameters["-index"])
        print(get_relevant_docs(parameters["-text"], 101, base))
    except (IndexError, KeyError) as e:
        pass


if __name__ == '__main__':
    main(["-index", "C:/Users/User/PycharmProjects/infosearch/index", "-text", "прочитать дементьева"])