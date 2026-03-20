import csv
from io import StringIO


def parse_csv(raw_text: str, delimiter: str = ',') -> list[dict]:
    """Parse raw CSV text into a list of row dicts.

    Args:
        raw_text: CSV content as a string, first row is headers.
        delimiter: Column separator (default comma).

    Returns:
        List of dicts, one per data row, keyed by header names.
    """
    lines = raw_text.strip().split('\n')
    headers = [h.strip() for h in lines[0].split(delimiter)]
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        values = [v.strip() for v in line.split(delimiter)]
        row = dict(zip(headers, values))
        rows.append(row)
    return rows
