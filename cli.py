import argparse
import os
import sys


def process_file(filepath: str) -> dict:
    """Read a file and return basic stats."""
    with open(filepath) as f:
        content = f.read()
    return {
        'path': filepath,
        'lines': content.count('\n') + 1,
        'chars': len(content),
    }


def main():
    parser = argparse.ArgumentParser(description='File stats tool')
    parser.add_argument('files', nargs='+', help='Files to process')
    parser.add_argument('--output', choices=['json', 'text'], default='text',
                        help='Output format')
    parser.add_argument('--verbose', action='store_true',
                        help='Print each file name as it is processed')
    args = parser.parse_args()

    results = []
    for f in args.files:
        if os.path.isfile(f):
            if args.verbose:
                print(f"Processing: {f}", file=sys.stderr)
            results.append(process_file(f))

    if args.output == 'json':
        import json
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['path']}: {r['lines']} lines, {r['chars']} chars")


if __name__ == '__main__':
    main()
