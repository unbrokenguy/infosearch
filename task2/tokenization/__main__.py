from pathlib import Path
from dataclasses import dataclass, field
from typing import List

import pymorphy2

MORPH = pymorphy2.MorphAnalyzer()


@dataclass
class Page:
    id: str
    url: str
    file_path: Path
    words: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self._tokenization()
        self._lemmatisation()

    def _tokenization(self):
        with open(self.file_path, encoding='utf-8') as file:
            data = file.read()
            self.words = list(map(lambda word: word.lower(), data.split(" ")))

    def _lemmatisation(self):
        self.words = list(map(lambda word: MORPH.parse(word)[0].normal_form, self.words))

    def save(self, base: Path):
        with open(base / f"{self.id}.txt", encoding='utf-8', mode='w') as file:
            file.write("\n".join(self.words))


def main(args):
    try:
        parameters = {"-index": args[args.index("-index") + 1]}
        base = Path(parameters['-index'])
        processed = base / "processed"
        Path.mkdir(processed, exist_ok=True, parents=True)
        index_path = base / "index.txt"
        pages_path = base / "pages"
        with open(index_path, encoding='utf-8') as file:
            index = file.readlines()
            for i in index:
                uuid, url = i.split(" ")
                page = Page(id=uuid, url=url, file_path=pages_path / f"{uuid}.txt")
                page.save(processed)
                print(f"{uuid} processed.")
    except (IndexError, KeyError) as e:
        pass


if __name__ == '__main__':
    main(["-index", "C:/Users/User/PycharmProjects/infosearch/index2"])
