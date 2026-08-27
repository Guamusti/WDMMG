"""Download the structured RUCT university codelist and create Madrid mapping."""
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
URL = 'https://datos.canarias.es/api/estadisticas/structural-resources/v1.0/codelists/ISTAC/CL_RUCT_UNIVERSIDADES/01.000/codes.csv?fields=+description'
RAW = ROOT / 'data' / 'raw' / 'ruct' / 'universidades.csv'
TARGET = ROOT / 'data' / 'processed' / 'ruct' / 'madrid-public-universities.json'
NAMES = {
    'Universidad de Alcalá': 'UAH',
    'Universidad Autónoma de Madrid': 'UAM',
    'Universidad Carlos III de Madrid': 'UC3M',
    'Universidad Complutense de Madrid': 'UCM',
    'Universidad Politécnica de Madrid': 'UPM',
    'Universidad Rey Juan Carlos': 'URJC',
}


def download():
    request = Request(URL, headers={'User-Agent': 'AtlasUniversitario/0.1'})
    payload = urlopen(request, timeout=30).read()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_bytes(payload)
    rows = list(csv.DictReader(io.StringIO(payload.decode('utf-8-sig'))))
    matches = []
    for row in rows:
        name = row.get('name#es', '').strip()
        if name in NAMES:
            matches.append({'ruct_code': row['code'], 'name': name, 'short': NAMES[name], 'source_url': URL})
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(matches, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Matched {len(matches)} Madrid public universities into {TARGET}')


if __name__ == '__main__':
    download()
