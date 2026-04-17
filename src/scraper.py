import logging
import httpx
import polars as pl
from datetime import date
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BJB:
    TAB_IDS = ["tab-0", "tab-1", "tab-2", "tab-3"]

    def __init__(self, urls: list[str]):
        self.urls = urls

    def _fetch(self, url: str) -> BeautifulSoup | None:
        try:
            resp = httpx.get(url, timeout = 10)
            resp.raise_for_status()
            
            return BeautifulSoup(resp.text, "html.parser")
        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

    def _parse_building(self, url: str) -> list[dict]:
        soup = self._fetch(url)
        if soup is None:
            return []

        units = []
        for tab_id in BJB.TAB_IDS:
            tab = soup.find(id = tab_id)
            if not tab:
                continue
            for row in tab.select("table tr")[1:]:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue
                units.append({
                    "url":            url,
                    "apartment_type": cols[0].get_text(strip = True),
                    "move_in_date":   cols[1].get_text(strip = True),
                    "market_rate":    cols[2].get_text(strip = True),
                    "date":           date.today().isoformat(),
                })

        if not units:
            logger.info(f"No available units found at {url}.")

        return units

    @staticmethod
    def _normalize(df: pl.DataFrame) -> pl.DataFrame:
        current_year = date.today().year

        return df.with_columns([
            pl.col("market_rate")
              .str.replace_all(r"[$,]", "")
              .cast(pl.Int32),

            pl.col("move_in_date")
              .str.strptime(pl.Date, r"%m/%d")
              .dt.replace(year = current_year)
              .map_elements(
                  lambda d: d.replace(year = current_year + 1) if d < date.today() else d,
                  return_dtype=pl.Date,
              ),

            pl.col("date").cast(pl.Date),
        ])

    def scrape(self) -> pl.DataFrame:
        COLS = ["address", "apartment_type", "move_in_date", "market_rate", "date", "source"]

        all_units = []
        for url in self.urls:
            all_units.extend(self._parse_building(url))

        if not all_units:
            logger.warning("No units found across all buildings.")
            return pl.DataFrame({c: [] for c in COLS})

        return (
            pl.DataFrame(all_units)
            .rename({"url": "source"})
            .pipe(self._normalize)
            .with_columns(
                address=pl.col("source")
                    .str.strip_chars("/")
                    .str.split("/")
                    .list.last()
                    .str.replace_all("-", " ")
                    .str.to_titlecase()
            )
            .select(COLS)
        )
