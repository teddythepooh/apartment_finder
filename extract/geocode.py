import time
import requests
import polars as pl

from listings import IDS

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "teddythepooh"}

def parse_address(listing_id: str) -> str:
    street_slug = listing_id.rstrip("/").split("/")[1]
    tokens = street_slug.split("-")
    formatted = []
    for token in tokens:
        if token.lower() in ("n", "s", "e", "w"):
            formatted.append(token.upper())
        else:
            formatted.append(token.title())
    return " ".join(formatted)

def geocode(address: str) -> tuple[float | None, float | None]:
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "us",
    }
    try:
        resp = requests.get(NOMINATIM_URL, params = params, headers = HEADERS, timeout = 10)
        resp.raise_for_status()
        results = resp.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            return lat, lon
    except Exception as e:
        print(f"  [error] {address}: {e}")
    return None, None

def main() -> pl.DataFrame:
    rows = []
    
    for listing_id in IDS:
        street = parse_address(listing_id)
        full_address = f"{street}, Chicago, IL"
        print(f"Geocoding: {full_address}")
        lat, lon = geocode(full_address)
        rows.append({
            "address": full_address,
            "lat": lat,
            "lon": lon,
            "coordinates": f"({lat}, {lon})" if lat is not None else None,
        })
        time.sleep(1.1)

    return pl.DataFrame(rows, schema = {
        "address": pl.Utf8,
        "lat": pl.Float64,
        "lon": pl.Float64,
        "coordinates": pl.Utf8,
    })


if __name__ == "__main__":
    df = main()
    
    df.write_csv("coordinates.csv")
