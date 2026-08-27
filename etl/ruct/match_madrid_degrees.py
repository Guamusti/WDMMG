"""Download active RUCT grade titles and conservatively match Madrid offers."""
import html
import json
import re
import time
import unicodedata
from io import StringIO
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
MADRID = ROOT / 'data' / 'processed' / 'admissions' / 'madrid-2025-2026.json'
OUT = ROOT / 'data' / 'processed' / 'ruct' / 'madrid-degree-matches.json'
REPORT = ROOT / 'data' / 'processed' / 'ruct' / 'madrid-degree-matches-quality.json'
RAW = ROOT / 'data' / 'raw' / 'ruct' / 'madrid-degrees'
UNIVERSITIES = {
    '010': 'Universidad Complutense de Madrid', '023': 'Universidad Autónoma de Madrid',
    '025': 'Universidad Politécnica de Madrid', '029': 'Universidad de Alcalá',
    '036': 'Universidad Carlos III de Madrid', '056': 'Universidad Rey Juan Carlos',
}


def clean_text(value):
    value = html.unescape(re.sub(r'<[^>]+>', ' ', str(value)))
    return re.sub(r'\s+', ' ', value).strip()


def normalized(value):
    value = clean_text(value).lower()
    value = re.sub(r'\([^)]*\)', ' ', value)
    value = re.split(r'\s+por la universidad\b|\s*/\s*bachelor\b', value, maxsplit=1)[0]
    value = re.sub(r'\b(graduado|graduada|grado|bachelor)\s+(o\s+graduada?\s+)?en\b', '', value)
    value = re.sub(r'\bdoble\s+grado\s+en\b', '', value)
    value = ''.join(c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def request_data(session, university_code):
    url = urljoin('https://www.educacion.gob.es/ruct/', 'consultaestudios.action?actual=estudios')
    payload = {'consulta': '1', 'codigoUniversidad': university_code, 'descripcionEstudio': '',
               'codigoTipo': 'G', 'codigoSubTipo': '', 'codigoRama': '', 'ambito': '',
               'codigoEstado': 'P', 'situacion': 'A', 'buscarHistorico': 'N',
               'action:listaestudios': 'Consultar'}
    response = session.post(url, data=payload, timeout=45)
    response.raise_for_status(); response.encoding = 'iso-8859-15'
    pages = [response.url]
    links = re.findall(r'href="([^"]*listaestudios[^"]*d-1335801-p=(\d+)[^"]*)"', response.text)
    pages += [urljoin(response.url, html.unescape(link)) for link, _ in links]
    pages = list(dict.fromkeys(pages)); records = []; RAW.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(pages, start=1):
        page_response = response if index == 1 else session.get(page, timeout=45)
        page_response.raise_for_status(); page_response.encoding = 'iso-8859-15'
        (RAW / f'{university_code}-page-{index}.html').write_text(page_response.text, encoding='utf-8')
        tables = pd.read_html(StringIO(page_response.text))
        if not tables: continue
        for _, row in tables[0].iterrows():
            code = re.sub(r'\D', '', str(row.iloc[0])); title = clean_text(row.iloc[1])
            if len(code) != 7 or not title: continue
            records.append({'ruct_degree_code': code, 'ruct_degree_name': title,
                            'university': clean_text(row.iloc[2]), 'university_ruct_code': university_code,
                            'source_url': f'https://www.educacion.gob.es/ruct/estudio.action?codigoCiclo=SC&codigoTipo=G&CodigoEstudio={code}&actual=estudios',
                            'source_page': index})
    return list({item['ruct_degree_code']: item for item in records}.values())


def request_detail(session, code):
    url = f'https://www.educacion.gob.es/ruct/estudio.action?codigoCiclo=SC&codigoTipo=G&CodigoEstudio={code}&actual=estudios'
    response = session.get(url, timeout=45)
    response.raise_for_status(); response.encoding = 'iso-8859-15'
    (RAW / f'degree-{code}.html').write_text(response.text, encoding='utf-8')
    def span(identifier):
        match = re.search(rf'id="{identifier}"[^>]*>(.*?)</span>', response.text, re.S)
        return clean_text(match.group(1)) if match else None
    centers = []
    block = re.search(r'<table[^>]+id="centro"[^>]*>(.*?)</table>', response.text, re.S)
    if block:
        tables = pd.read_html(StringIO(block.group(0)))
        if tables:
            for _, row in tables[0].iterrows():
                centers.append({'code': re.sub(r'\D', '', str(row.iloc[1])), 'name': clean_text(row.iloc[2])})
    return {'branch': span('estudio_descripcionRama'), 'field': span('estudio_descripcionAmbito'),
            'ects': span('estudio_creditos_ecs'), 'centers': centers, 'source_url': url}


def main():
    session = requests.Session(); session.headers['User-Agent'] = 'AtlasUniversitario/0.1 (datos abiertos)'
    ruct = [item for code in UNIVERSITIES for item in request_data(session, code)]
    by_university = {}
    for row in ruct:
        by_university.setdefault(row['university_ruct_code'], {}).setdefault(normalized(row['ruct_degree_name']), []).append(row)
    offers = json.loads(MADRID.read_text(encoding='utf-8')); matches = []
    detail_by_code = {}
    matched_codes = {candidates[0]['ruct_degree_code'] for university in by_university.values() for candidates in university.values() if len(candidates) == 1}
    for number, code in enumerate(sorted(matched_codes), start=1):
        detail_by_code[code] = request_detail(session, code)
        if number % 25 == 0: print(f'Fetched RUCT details: {number}/{len(matched_codes)}')
        time.sleep(0.05)
    counts = {'matched_unique': 0, 'pending_no_match': 0, 'pending_ambiguous': 0}
    for index, offer in enumerate(offers, start=1):
        candidates = by_university.get(str(offer.get('university_ruct_code')), {}).get(normalized(offer.get('degree_name_source', '')), [])
        if len(candidates) == 1:
            candidate, status, method = candidates[0], 'matched', 'normalized_exact_unique'; counts['matched_unique'] += 1
        elif len(candidates) > 1:
            candidate, status, method = None, 'pending', 'ambiguous_normalized_exact'; counts['pending_ambiguous'] += 1
        else:
            candidate, status, method = None, 'pending', 'no_normalized_exact_match'; counts['pending_no_match'] += 1
        detail = detail_by_code.get(candidate['ruct_degree_code']) if candidate else None
        matches.append({'admission_id': offer.get('id') or f'madrid:{index}', 'admission_degree': offer.get('degree_name_source'),
                        'university_ruct_code': str(offer.get('university_ruct_code')), 'status': status,
                        'match_method': method, 'ruct_degree_code': candidate['ruct_degree_code'] if candidate else None,
                        'ruct_degree_name': candidate['ruct_degree_name'] if candidate else None,
                        'ruct_source_url': candidate['source_url'] if candidate else None,
                        'ruct_branch': detail['branch'] if detail else None, 'ruct_field': detail['field'] if detail else None,
                        'ruct_ects': detail['ects'] if detail else None, 'ruct_centers': detail['centers'] if detail else []})
    quality = {'source': 'RUCT · consulta oficial de títulos · estado publicado · grado',
               'source_url': 'https://www.educacion.gob.es/ruct/consultaestudios.action?actual=estudios',
               'ruct_titles_downloaded': len(ruct), 'ruct_details_downloaded': len(detail_by_code), 'admission_offers_reviewed': len(offers), 'counts': counts,
               'accepted_only_unique_normalized_matches': True, 'unmatched_are_not_inferred': True}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(matches, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(quality, ensure_ascii=False))


if __name__ == '__main__': main()
