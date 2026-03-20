from parser import parse_csv

def test_basic():
    data = "name,age\nAlice,30\nBob,25"
    result = parse_csv(data)
    assert len(result) == 2
    assert result[0] == {'name': 'Alice', 'age': '30'}

def test_blank_lines():
    data = "name,age\nAlice,30\n\nBob,25\n\n"
    result = parse_csv(data)
    assert len(result) == 2  # Should skip blank lines
    assert result[1] == {'name': 'Bob', 'age': '25'}
