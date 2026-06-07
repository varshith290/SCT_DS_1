import re
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

import matplotlib.pyplot as plt
import pandas as pd


DATA_URL = "https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"
ZIP_FILE = Path("world_bank_population.zip")
EXTRACT_DIR = Path("world_bank_population")


def download_dataset():
    if not ZIP_FILE.exists():
        urlretrieve(DATA_URL, ZIP_FILE)

    EXTRACT_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP_FILE, "r") as zip_file:
        zip_file.extractall(EXTRACT_DIR)


def load_population_data():
    download_dataset()

    data_file = next(EXTRACT_DIR.glob("API_SP.POP.TOTL*.csv"))
    metadata_file = next(EXTRACT_DIR.glob("Metadata_Country_API_SP.POP.TOTL*.csv"))

    population = pd.read_csv(data_file, skiprows=4)
    metadata = pd.read_csv(metadata_file)

    year_columns = [
        column for column in population.columns
        if re.fullmatch(r"\d{4}", str(column))
    ]
    latest_year = max(year_columns)

    population = population[["Country Name", "Country Code", latest_year]]
    population = population.rename(columns={latest_year: "Population"})

    metadata = metadata[["Country Code", "Region"]]
    population = population.merge(metadata, on="Country Code", how="left")

    countries_only = population.dropna(subset=["Region", "Population"])
    return countries_only, latest_year


def create_top_population_bar_chart(data, latest_year):
    top_10 = data.sort_values("Population", ascending=False).head(10)

    plt.figure(figsize=(11, 6))
    plt.bar(
        top_10["Country Name"],
        top_10["Population"] / 1_000_000,
        color="#2563eb"
    )

    plt.title(f"Top 10 Countries by Population ({latest_year})")
    plt.xlabel("Country")
    plt.ylabel("Population in Millions")
    plt.xticks(rotation=35, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig("top_10_population_bar_chart.png", dpi=200)
    plt.show()


def create_population_histogram(data, latest_year):
    plt.figure(figsize=(10, 6))
    plt.hist(
        data["Population"] / 1_000_000,
        bins=25,
        color="#14b8a6",
        edgecolor="#0f172a"
    )

    plt.title(f"Distribution of Country Populations ({latest_year})")
    plt.xlabel("Population in Millions")
    plt.ylabel("Number of Countries")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig("population_histogram.png", dpi=200)
    plt.show()


def main():
    population_data, latest_year = load_population_data()
    create_top_population_bar_chart(population_data, latest_year)
    create_population_histogram(population_data, latest_year)


if __name__ == "__main__":
    main()