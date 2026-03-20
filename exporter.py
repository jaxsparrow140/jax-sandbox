def export_rows(rows: list[dict], columns: list[str]) -> str:
    """Export rows as CSV text.

    Args:
        rows: List of row dicts.
        columns: Column names in desired output order.

    Returns:
        CSV string with header row + data rows.
    """
    header = ','.join(columns)
    output = [header]
    for row in rows:
        if row.get('status') == 'archived':
            continue
        values = [str(row.get(key, '')) for key in columns]
        output.append(','.join(values))
    return '\n'.join(output)
