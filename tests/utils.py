import os
from typing import List, Tuple

cur_dir = os.path.dirname(__file__)
test_asset_dir = os.path.join(cur_dir, 'asset')


def get_test_asset_content(file: str) -> str:
    result = ''
    file_dir = os.path.join(test_asset_dir, file)

    with open(file_dir, encoding='utf8') as f:
        result = ''.join(f.readlines())

    return result


def get_expected_footnotes(file: str) -> List[Tuple[str, str]]:
    content = get_test_asset_content(file)

    result = []

    lines = content.split('\n')

    for i in range(0, len(lines) - 1, 2):
        result.append((lines[i], lines[i + 1]))

    return result
