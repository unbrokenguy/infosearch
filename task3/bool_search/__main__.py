from copy import copy
from pathlib import Path
from typing import Dict, Set, Callable, List, Optional, Union


class InvertedIndex:
    def __init__(self, index: Optional[Dict[str, Set[str]]]):
        self.index = index if index else {}

    def from_pages(self, index_base: Path):
        with open(index_base / "index.txt", encoding='utf-8') as file:
            index_txt = file.readlines()
            processed = index_base / "processed"
            for i in index_txt:
                uuid, url = i.split(" ")
                if Path.exists(processed):
                    with open(processed / f"{uuid}.txt", encoding='utf-8') as processed_page:
                        unique_words = set(processed_page.read().split("\n"))
                        for word in unique_words:
                            self.index[word] = self.index[word] | {uuid} if self.index.get(word) else {uuid}
                else:
                    print("Run tokenization and lemmatisation first.")
                    raise ValueError


def _and(left: Set[str], right: Set[str]) -> Set[str]:
    return left & right


def _or(left: Set[str], right: Set[str]) -> Set[str]:
    return left | right


class BoolSearch:
    def __init__(self, index: Dict[str, Set[str]]):
        self.index = index
        self.operators = ["&", "|", "!"]
        self._full_union = set()
        for k, v in self.index.items():
            self._full_union = self.full_union | v

    @property
    def full_union(self):
        return copy(self._full_union)

    def search(self, query: str) -> List:
        _query: List = query.split(" ")

        while "&" in _query:
            index = _query.index("&")
            left = _query[index - 1]
            right = _query[index + 1]
            _query[index] = self.calculate(left, right, _and)
            _query.remove(left)
            _query.remove(right)
        while "|" in _query:
            index = _query.index("|")
            left = _query[index - 1]
            right = _query[index + 1]
            _query[index] = self.calculate(left, right, _or)
            _query.remove(left)
            _query.remove(right)
        return _query

    def _not(self, right: Union[str, Set[str]]) -> Set[str]:
        if isinstance(right, set):
            return self.full_union - right
        if isinstance(right, str):
            return self.full_union - self.index.get(right)

    def calculate(self, left: Union[str, Set[str]], right: Union[str, Set[str]], operation: Callable[[Set[str], Set[str]], Set[str]]) -> Set[str]:
        if isinstance(left, set) and isinstance(right, set):
            return operation(left, right)

        if isinstance(left, set) and isinstance(right, str):
            return operation(left, self._prepare_not(right))

        if isinstance(left, str) and isinstance(right, set):
            return operation(self._prepare_not(left), right)

        if isinstance(left, str) and isinstance(right, str):
            return operation(self._prepare_not(left), self._prepare_not(right))

    def _prepare_not(self, right: str) -> Set[str]:
        if right.startswith("!"):
            return self._not(right[1:])
        return self.index.get(right)


def main(args):
    try:
        parameters = {"-index": args[args.index("-index") + 1]}
        base = Path(parameters['-index'])
        index = {"a": {"2"},
                 "banana": {"2"},
                 "is": {"0", "1", "2"},
                 "it": {"0", "1", "2"},
                 "what": {"0", "1"}}
        i = InvertedIndex(index=index)
        bs = BoolSearch(index=i.index)
        print(bs.search("what & is & !it"))
        i = InvertedIndex(index=None)
        i.from_pages(base)
        with open("txt.txt", mode='w', encoding='utf-8') as f:
            f.write(str(i.index))
        bs = BoolSearch(index=i.index)
        result = bs.search("стихотворение & твардовский")[0]
        pages = {}
        with open(base / "index.txt", encoding='utf-8') as file:
            index_txt = file.readlines()
            for i in index_txt:
                uuid, url = i.split(" ")
                pages[uuid] = url
        for item in result:
            print(pages.get(item).strip())

    except (IndexError, KeyError) as e:
        pass


if __name__ == '__main__':
    main(["-index", "C:/Users/User/PycharmProjects/infosearch/index2"])
