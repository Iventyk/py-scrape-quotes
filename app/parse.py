import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_quotes() -> list[Quote]:
    all_quotes: list[Quote] = []
    current_page_url = BASE_URL

    while current_page_url:
        text = requests.get(current_page_url).text
        soup = BeautifulSoup(text, "html.parser")
        quotes = soup.select(".quote")
        all_quotes.extend(parse_single_quote(quote) for quote in quotes)

        next_page = soup.select_one(".next a")
        if next_page:
            next_page_url = next_page["href"]
            current_page_url = BASE_URL.rstrip("/") + next_page_url
        else:
            current_page_url = None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote]) -> None:
    with open("result.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes())


if __name__ == "__main__":
    main("quotes.csv")
