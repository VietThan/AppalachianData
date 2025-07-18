import json
import logging
import re 
from random import randint
from time import sleep
import pathlib

import requests

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

YEAR = 1957

FIRST_PAGE_URL_FORMAT = "https://appalachiantrail.org/miler-listings-year/{year}/"
OTHER_PAGE_FORMAT = "https://appalachiantrail.org/miler-listings-year/{year}/page/{page_number}/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Safari/537.36"
    )
}

def get_year_first_page(year: int) -> None | requests.Response:
    first_page_url = FIRST_PAGE_URL_FORMAT.format(year=year)

    # get first page first, if page doesn't exist, there is no data
    response = requests.get(url=first_page_url, headers=HEADERS)

    try:
        response.raise_for_status()
    except Exception:
        logger.warning(f"Could not retrive first page of {year = }")
        return None
    
    return response

def get_year_other_page(year: int, page_number: int) -> None | requests.Response:
    other_page_url = OTHER_PAGE_FORMAT.format(year=year, page_number=page_number)

    # get first page first, if page doesn't exist, there is no data
    response = requests.get(url=other_page_url, headers=HEADERS)

    try:
        response.raise_for_status()
    except Exception:
        logger.warning(f"Could not retrieve {year = }, {page_number = }")
        return None
    
    return response
    
def process_html(html: str, year: int, page_number: int) -> None:
    # Save it in data
    filepath_format = "data/{year}_{page_number}.html"
    filepath = filepath_format.format(
        year=year,
        page_number=page_number
    )
    with open(filepath, "w+") as f:
        f.write(html)

    # Parse it with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find the div with the specific ID
    miler_div = soup.find("div", id="miler-listings")

    if not miler_div:
        logger.warning(f"No div with id='miler-listings' found for {year = }, {page_number = }")


    # Find all the <a> tags inside it with class="miler-listing"
    entries = miler_div.find_all("a", class_="miler-listing")

    # Extract data-id and cleaned text
    data: list[dict] = []
    for entry in entries:
        data_id = entry.get("data-id")
        raw_text = entry.get_text()
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        data.append({"id": data_id, "info": clean_text})

    # output
    output_filepath_format = "output/{year}_{page_number}.ndjson"
    output_filepath = output_filepath_format.format(
        year=year,
        page_number=page_number
    )

    with open(output_filepath, "w+") as f_o:
        for row in data:
            json_string = json.dumps(row)
            f_o.write(json_string)
            f_o.write("\n")
    

    logger.info(f"Finished processing {year = }, {page_number = }")


def one_year(year: int):
    # first page of year
    logger.info(f"Started script processing {year}")
    response = get_year_first_page(year=year)
    if response is None:
        return
    process_html(html=response.text, year=year, page_number=1)

    # other page of year
    should_continue = True
    page_number = 2
    while should_continue:
        logger.info(f"Started processing {year = } {page_number = }")
        response = get_year_other_page(year=year, page_number=page_number)
        if response is None:
            should_continue = False
            continue

        process_html(html=response.text, year=year, page_number=page_number)
        page_number += 1

    logger.info(f"Finished script")

    
def main():
    for year in range(2001, 2025):
        one_year(year=year)
        random_wait = randint(10,30)
        logger.info(f"sleeping for {random_wait} seconds after processing {year = }")
        sleep(random_wait)

def main2():
    dir = pathlib.Path("data")
    for item in dir.glob("*.html"):
        name_without_suffix = item.name.replace(".html", "")
        parts_split = name_without_suffix.split("_")

        year = int(parts_split[0])
        page_number = int(parts_split[1])
        process_html(
            html=item.read_text(),
            year=year,
            page_number=page_number
        )


if __name__ == "__main__":
    main2()