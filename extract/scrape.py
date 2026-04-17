import logging
from datetime import date
from pathlib import Path
from polars import DataFrame

from src import BJB
from listings import URLS

today = date.today().isoformat()

output_dir = Path("output")
logs_dir = output_dir.joinpath("logs/")

logs_dir.mkdir(exist_ok = True, parents = True)

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s %(levelname)s %(message)s",
    handlers = [
        logging.FileHandler(logs_dir.joinpath(f"scraper_{today}.log")),
        logging.StreamHandler(),
    ]
)

def main() -> DataFrame:
    listings = BJB(URLS).scrape()
    
    return listings

if __name__ == "__main__":
    df = main()
    
    df.write_csv(output_dir.joinpath(f"listings_{today}.csv"))
