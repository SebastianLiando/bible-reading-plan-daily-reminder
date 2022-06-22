from typing import List
import re

VERSE_NO_PATTERN = r'<b>[¹²³⁴⁵⁶⁷⁸⁹⁰][¹²³⁴⁵⁶⁷⁸⁹⁰]{0,2}</b>'
FOOTNOTE_HEADER_PATTERN = r'📝 <b>Footnotes</b>'
FOOTNOTE_NOTE_PATTERN = r'[a-z]\. '


def split_by_indexes(text: str, indexes: List[int]) -> List[str]:
    result = []
    for i, index in enumerate(indexes):
        part = ''

        if i == 0:
            part = text[:index]
        else:
            part = text[indexes[i-1]:index]

        result.append(part)

    return result


def split_to_parts(message: str) -> List[str]:
    # Split each verses
    splits = re.findall(VERSE_NO_PATTERN, message)
    indexes = list(map(lambda split: message.index(split), splits))

    # Split footnote if exist
    if FOOTNOTE_HEADER_PATTERN in message:
        # Header
        footnote_header_index = message.index(FOOTNOTE_HEADER_PATTERN)
        indexes.append(footnote_header_index)

        # Footnotes
        footnotes = message[footnote_header_index:]
        for match in re.finditer(FOOTNOTE_NOTE_PATTERN, footnotes):
            match_index = match.start(0) + footnote_header_index
            indexes.append(match_index)

    # Add the end of message
    indexes.append(len(message))

    return split_by_indexes(message, indexes)


def split_html_message(message: str, length: int = 4000) -> List[str]:
    parts = split_to_parts(message)

    result = []
    msg = ''

    for part in parts:
        if len(msg) + len(part) > length:
            result.append(msg)
            msg = ''

        msg += part

    if len(msg) > 0:
        result.append(msg)

    return result
