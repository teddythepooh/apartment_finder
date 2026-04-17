import polars as pl
import pydeck as pdk
import streamlit as st

from extract.scrape import BJB
from listings import URLS

@st.cache_data(ttl = 3600 * 24, show_spinner = "Extracting listings…")
def load_data() -> pl.DataFrame:
    coords = (
        pl.read_csv("coordinates.csv")
        .with_columns(
            pl.col("address")
              .str.replace(", Chicago, IL", "")
              .str.strip_chars()
              .alias("address_short")
        )
    )

    return (
        BJB(URLS).scrape()
        .with_columns(
            pl.col("apartment_type").str.to_titlecase()
        )
        .join(coords, left_on = "address", right_on = "address_short", how = "left")
        .with_columns(
            pl.col("source")
              .str.strip_chars("/")
              .str.split("/")
              .list.get(-2)
              .str.replace("-apartments", "")
              .str.replace_all("-", " ")
              .str.to_titlecase()
              .alias("neighborhood")
        )
    )

st.set_page_config(page_title = "teddythepooh", layout = "wide", initial_sidebar_state = "expanded")

st.title("BJB Properties: Apartment Finder")
st.markdown(
    "Browse for available units at [BJB Properties](https://bjbproperties.com/)! This dashboard scrapes their website once per day for the most up-to-date listings. "
    "I am NOT affiliated with BJB Properties, but I have been their tenant for four years and counting. I "
    "built this tool to circumvent BJB's website, which forces you to individually click each property to "
    "view available units. The search functionality is not any better, either. To prospective tenants, "
    "I hope you find this alternative useful!",
    unsafe_allow_html = True
)

df = load_data()

with st.sidebar:
    st.header("Filters")

    rent_min = int(df["market_rate"].drop_nulls().min())
    rent_max = int(df["market_rate"].drop_nulls().max())
    rent_range = st.slider(
        "Monthly Rent ($)",
        min_value = rent_min,
        max_value = rent_max,
        value = (rent_min, rent_max),
        step = 25,
    )

    neighborhoods = sorted(df["neighborhood"].drop_nulls().unique().to_list())
    st.markdown("**Neighborhood**")
    def on_all_neighborhoods():
        for n in neighborhoods:
            st.session_state[f"neighborhood_{n}"] = st.session_state["all_neighborhoods"]
    st.checkbox("All", value = True, key = "all_neighborhoods", on_change = on_all_neighborhoods)
    cols = st.columns(2)
    selected_neighborhoods = []
    for i, n in enumerate(neighborhoods):
        if cols[i % 2].checkbox(n, value = True, key = f"neighborhood_{n}"):
            selected_neighborhoods.append(n)

    unit_types = sorted(df["apartment_type"].drop_nulls().unique().to_list())
    st.markdown("**Unit Type**")
    def on_all_types():
        for u in unit_types:
            st.session_state[f"type_{u}"] = st.session_state["all_types"]
    st.checkbox("All", value = True, key = "all_types", on_change = on_all_types)
    cols = st.columns(2)
    selected_types = []
    for i, u in enumerate(unit_types):
        if cols[i % 2].checkbox(u, value = True, key = f"type_{u}"):
            selected_types.append(u)

    move_in_dates = sorted(df["move_in_date"].drop_nulls().unique().to_list())
    st.markdown("**Move-in Month**")
    def on_all_dates():
        for d in move_in_dates:
            st.session_state[f"date_{d}"] = st.session_state["all_dates"]
    st.checkbox("All", value = True, key = "all_dates", on_change = on_all_dates)
    cols = st.columns(2)
    selected_dates = []
    for i, d in enumerate(move_in_dates):
        if cols[i % 2].checkbox(d.strftime("%B %Y"), value = True, key = f"date_{d}"):
            selected_dates.append(d)

filtered = df.filter(
    (pl.col("market_rate") >= rent_range[0])
    & (pl.col("market_rate") <= rent_range[1])
    & pl.col("neighborhood").is_in(selected_neighborhoods)
    & pl.col("apartment_type").is_in(selected_types)
    & pl.col("move_in_date").is_in(selected_dates)
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Available Units", len(filtered))
col2.metric("Buildings", filtered["address"].n_unique())
col3.metric("Average Rent", f"${filtered['market_rate'].mean():,.0f}" if len(filtered) else "—")
col4.metric("Lowest Rent", f"${filtered['market_rate'].min():,}" if len(filtered) else "—")

st.divider()

map_df = (
    filtered
    .drop_nulls(subset = ["lat", "lon"])
    .group_by(["address", "neighborhood", "lat", "lon"])
    .agg([
        pl.len().alias("available_units"),
        pl.col("market_rate").min().alias("rent_from"),
        pl.col("market_rate").max().alias("rent_to"),
    ])
    .with_columns(
        pl.concat_str([
            pl.lit("$"), pl.col("rent_from").cast(pl.Utf8),
            pl.lit(" – $"), pl.col("rent_to").cast(pl.Utf8),
        ]).alias("rent_range")
    )
    .to_pandas()
)

if not map_df.empty:
    st.subheader("Locations")
    st.pydeck_chart(pdk.Deck(
        map_style = "light",
        initial_view_state = pdk.ViewState(
            latitude = map_df["lat"].mean(),
            longitude = map_df["lon"].mean(),
            zoom = 12,
            pitch = 0,
        ),
        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                data = map_df,
                get_position = ["lon", "lat"],
                get_radius = 80,
                get_fill_color = [30, 120, 220, 200],
                pickable = True,
            )
        ],
        tooltip = {
            "html": (
                "<b>{address}</b><br/>"
                "{neighborhood}<br/>"
                "Units available: {available_units}<br/>"
                "Rent: {rent_range}"
            ),
            "style": {"backgroundColor": "white", "color": "black", "fontSize": "13px"},
        },
    ))

st.divider()

st.subheader(f"{len(filtered)} Unit{'s' if len(filtered) != 1 else ''}")

display = (
    filtered
    .select(["neighborhood", "address", "apartment_type", "move_in_date", "market_rate", "source"])
    .rename({
        "neighborhood":   "Neighborhood",
        "address":        "Building",
        "apartment_type": "Unit Type",
        "move_in_date":   "Move-in Date",
        "market_rate":    "Rent ($)",
        "source":         "URL",
    })
    .sort(["Neighborhood", "Building", "Rent ($)"])
    .to_pandas()
)

st.dataframe(
    display,
    column_config = {
        "URL":          st.column_config.LinkColumn("Link"),
        "Rent ($)":     st.column_config.NumberColumn(format = "$%d"),
        "Move-in Date": st.column_config.DateColumn(format = "MMM D, YYYY"),
    },
    use_container_width = True,
    hide_index = True,
)
