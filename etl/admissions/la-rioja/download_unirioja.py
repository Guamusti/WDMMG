"""Download the official Universidad de La Rioja cutoff workbook."""
from pathlib import Path
from urllib.request import urlretrieve

SOURCE_URL = (
    "https://unirioja.sharepoint.com/:x:/s/academica_publico/"
    "EQk7Ld-mCmxIs88pBsG789MB1npvMyM91McTY7rEHmc6uA"
    "?e=LYeSPv&download=1"
)
OUTPUT = Path("data/raw/admissions/la-rioja/2025-2026/unirioja-notas-corte-2025-2026.xlsx")


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(SOURCE_URL, OUTPUT)
    print(f"Downloaded {OUTPUT} from the official UR source")
