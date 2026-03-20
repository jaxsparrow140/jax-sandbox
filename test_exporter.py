from exporter import export_rows


def test_basic_export():
    rows = [
        {'name': 'Alice', 'age': '30', 'status': 'active'},
        {'name': 'Bob', 'age': '25', 'status': 'active'},
    ]
    result = export_rows(rows, columns=['name', 'age'])
    lines = result.split('\n')
    assert lines[0] == 'name,age'
    assert lines[1] == 'Alice,30'
    assert lines[2] == 'Bob,25'


def test_filters_archived():
    rows = [
        {'name': 'Alice', 'status': 'active'},
        {'name': 'Bob', 'status': 'archived'},
        {'name': 'Carol', 'status': 'active'},
    ]
    result = export_rows(rows, columns=['name', 'status'])
    lines = result.split('\n')
    names = [l.split(',')[0] for l in lines[1:]]
    assert 'Bob' not in names
    assert 'Alice' in names
    assert 'Carol' in names


def test_missing_column_defaults_empty():
    rows = [{'name': 'Alice'}]
    result = export_rows(rows, columns=['name', 'score'])
    lines = result.split('\n')
    assert lines[1] == 'Alice,'


def test_empty_rows():
    result = export_rows([], columns=['name', 'age'])
    assert result == 'name,age'
