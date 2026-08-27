"""Quality checks for the processed Madrid admission extract (stdlib only)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data' / 'processed' / 'admissions' / 'madrid-2025-2026.json'
OUTPUT = ROOT / 'data' / 'quality' / 'madrid-2025-2026.json'

rows = json.loads(INPUT.read_text(encoding='utf-8'))
keys = [(row.get('source_page'), row.get('raw_row')) for row in rows]
invalid_cutoff = [row for row in rows if row.get('cutoff_score') is None or not 0 <= row['cutoff_score'] <= row.get('score_scale_max', 14)]
missing_degree = [row for row in rows if not row.get('degree_name_source')]
missing_university = [row for row in rows if not row.get('university_name_source')]
malformed_degree = [row for row in rows if re.search(r'\d', row.get('degree_name_source', '')) or re.search(r'^(?:www\.|info@|tel\.?\s*:|c/\s|avda\.?\s|paseo\s|centro\s|ces\s|eu\s|de la\s|«)', row.get('degree_name_source', ''), re.IGNORECASE)]
concatenated_branch = [row for row in rows if re.search(r'Rama de conocimiento', row.get('branch_name_source', ''), re.IGNORECASE)]
missing_ruct_code = [row for row in rows if not row.get('university_ruct_code')]
unknown_ruct_code = [row for row in rows if row.get('university_ruct_code') not in {'010', '023', '025', '029', '036', '056'}]
duplicate_keys = len(keys) - len(set(keys))
report = {
    'dataset': 'madrid-2025-2026-admission-cutoffs',
    'records': len(rows),
    'checks': {
        'invalid_cutoff_0_14': len(invalid_cutoff),
        'duplicate_source_rows': duplicate_keys,
        'missing_degree': len(missing_degree),
        'missing_university': len(missing_university),
        'malformed_degree_name': len(malformed_degree),
        'concatenated_branch_name': len(concatenated_branch),
        'missing_university_ruct_code': len(missing_ruct_code),
        'unknown_university_ruct_code': len(unknown_ruct_code),
        'unexpected_academic_year': sum(row.get('academic_year') != '2025-2026' for row in rows),
    },
    'warnings': [
        {'code': 'RUCT_TITLE_CENTER_MATCH_PENDING', 'count': len(rows), 'message': 'Los códigos de universidad están enlazados; faltan códigos RUCT individuales de títulos y centros.'},
    ],
    'status': 'pass' if not invalid_cutoff and not duplicate_keys and not missing_degree and not malformed_degree and not concatenated_branch and not missing_ruct_code and not unknown_ruct_code else 'review',
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
