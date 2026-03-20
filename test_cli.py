import os
import tempfile
from cli import process_file


def test_process_file_counts():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('hello\nworld\n')
        path = f.name
    try:
        result = process_file(path)
        assert result['path'] == path
        assert result['lines'] == 3   # 'hello\nworld\n' → 3 "lines" (content.count('\n') + 1)
        assert result['chars'] == 12  # len('hello\nworld\n')
    finally:
        os.unlink(path)


def test_process_file_single_line():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('no newline')
        path = f.name
    try:
        result = process_file(path)
        assert result['lines'] == 1
        assert result['chars'] == 10
    finally:
        os.unlink(path)
