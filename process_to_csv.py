import io
import json
import logging
import re 
import pathlib

from pydantic import BaseModel

from random import randint
from time import sleep

import requests

from bs4 import BeautifulSoup

OUTPUT_DIR = "output"

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

# pattern = re.compile(
#     r"^(?P<last_name>[^,]+), (?P<first_name>[^;'']+)"
#     r"(?: '(?P<nickname>[^']+)')?; "
#     r"(?P<state>[^,]+)?, (?P<country>[^,]*),?\s*(?P<type>\w+)?"
# )

class ProcessedInfo(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    trail_name: str | None = None
    state: str | None = None
    country: str | None = None
    hike_type: str | None = None

    def to_str(self) -> str:
        l_str = self.last_name if self.last_name else ""
        f_str = self.first_name if self.first_name else ""
        t_str = self.trail_name if self.trail_name else ""
        s_str = self.state if self.state else ""
        c_str = self.country if self.country else ""
        h_str = self.hike_type if self.hike_type else ""

        return f"{l_str}|{f_str}|{t_str}|{s_str}|{c_str}|{h_str}"


name_pattern = re.compile(
    r"^(?P<last_name>[^,]+), (?P<first_name>[^;']+)(?: '(?P<trail_name>.+?)')?$"
)
origin_pattern = re.compile(
    r"^(?P<state>[^,]*),\s*(?P<country>[^,]*),?\s*(?P<hike_type>\w+)?"
)

def process_info(info: str) -> ProcessedInfo:
    # logger.debug(info)
    processed_info = ProcessedInfo()

    info_parts = info.split(";")

    name_part = info_parts[0]
    # origin_part = info_parts[1]

    name_match = name_pattern.match(name_part)
    if name_match:
        name_data = {k: (v.strip() if v else None) for k, v in name_match.groupdict().items()}
        processed_info.last_name = name_data.get("last_name")
        processed_info.first_name = name_data.get("first_name")
        processed_info.trail_name = name_data.get("trail_name") if name_data.get("trail_name") != "'-" else None
    else:
        logger.warning(f"line does not match name pattern: {name_part}")

    if len(info_parts) != 2:
        logger.warning(f"not enough parts: {info_parts}")
        return processed_info

    origin_part = info_parts[1]
    origin_match = origin_pattern.match(origin_part)

    if origin_match:
        origin_data = {k: (v.strip() if v else None) for k, v in origin_match.groupdict().items()}
        processed_info.state = origin_data.get("state") if origin_data.get("state") != "'-" else None
        processed_info.country = origin_data.get("country")
        processed_info.hike_type = origin_data.get("hike_type")
    else:
        logger.warning(f"Line does not match origin pattern: {origin_part}. {info = }")

    return processed_info


def single_read_and_write(
    output_file: io.TextIOWrapper,
    input_filepath: pathlib.Path
):
    logger.info(f"processing {input_filepath.name = }")
    name_without_suffix = input_filepath.name.replace(".ndjson", "")
    parts_split = name_without_suffix.split("_")

    year = int(parts_split[0])
    page_number = int(parts_split[1])
    logger.info(f"processing {year = }, {page_number = }")

    with open(input_filepath, "r") as fp:
        lines = fp.readlines()

    for line in lines:
        line_dict = json.loads(line)
        id = line_dict["id"]
        info = line_dict["info"]
        processed_info = process_info(info=info)

        logger.info(processed_info)
        p_info_str = processed_info.to_str()
        output_file.write(
            f"{id}|{p_info_str}\n"
        )
        




def read_and_write_to_output_file(output_file: io.TextIOWrapper):
    dir = pathlib.Path(OUTPUT_DIR)
    for item in dir.glob("*.ndjson"):
        single_read_and_write(
            output_file=output_file,
            input_filepath=item
        )

        

def main():
    with open("output.csv", "w+") as output_file:
        read_and_write_to_output_file(output_file=output_file)


if __name__ == "__main__":
    main()
