import sys
import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from queue import Queue
from uuid import uuid4
from urllib.parse import urlparse

PAGES_MINIMUM = 100
WORDS_MINIMUM = 1000


@dataclass
class Page:
    url: str
    id: int = 0
    text: str = field(init=False)


class Crawler:
    def __init__(self, url):
        self.root = f"{urlparse(url).scheme}://{urlparse(url).hostname}"
        self.url = url
        self._process_queue = Queue()
        self.index = {}
        self._processed = []
        self.http = requests.session()

    def start(self):
        self._process_queue.put(Page(url=self.url))
        self._crawl()

    def _crawl(self):
        index = 0
        while not self._process_queue.empty():
            if len(self._processed) > PAGES_MINIMUM:
                break
            page = self._process_queue.get()

            if self._process(page=page):
                page.id = index
                index += 1
                self._processed.append(page.url)
                self.index[page.id] = page
        self._save()

    def _process(self, page: Page):
        if page.url not in self._processed:
            response = self.http.get(page.url)
            self._extract_links(response.text)
            page.text = self._extract_plain_text(response.text)
            if len(page.text.split(" ")) < WORDS_MINIMUM:
                return False
            return True
        return False

    def _extract_plain_text(self, html: str):
        soup = BeautifulSoup(html, features="html.parser")

        for exclude in soup(["script", "style"]):
            exclude.extract()

        text = soup.get_text()
        text = re.sub(r"[^А-я\s]", "", text)
        text = re.sub(r"\n", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_links(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.findAll('a'):
            href = link.get('href')
            if href:
                if href.startswith("http"):
                    self._process_queue.put(Page(url=href))
                if href.startswith("/"):
                    self._process_queue.put(Page(url=self.root + href))

    def _save(self):
        Path.mkdir(Path("../../index2/pages"), exist_ok=True, parents=True)
        with open("../../index2/index.txt", "w", encoding="utf-8") as index:
            for key, value in self.index.items():
                index.write(f"{key} {value.url}\n")
                with open(f"../../index2/pages/{key}.txt", "wt", encoding="utf-8") as page:
                    page.write(value.text)


def main(argv):
    # crawler = Crawler(url="https://rustih.ru/stihi-russkih-poetov-klassikov")
    # crawler.start()
    try:
        parameters = {"-url": argv[argv.index("-url") + 1]}
        crawler = Crawler(url=parameters["-url"])
        crawler.start()
    except (IndexError, KeyError) as e:
        pass


if __name__ == "__main__":
    main(["-url", "https://rustih.ru/stihi-russkih-poetov-klassikov"])

