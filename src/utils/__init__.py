superscript = {
    0: '⁰',
    1: "¹",
    2: "²",
    3: '³',
    4: '⁴',
    5: '⁵',
    6: '⁶',
    7: '⁷',
    8: '⁸',
    9: '⁹',
}


def get_superscript(num: int) -> str:
    '''
    Returns the superscript string of the given number.
    '''
    digits = []

    while num > 0:
        digit = num % 10
        digits.append(digit)

        num //= 10

    digits.reverse()
    superscripts = map(lambda digit: superscript[digit], digits)

    return ''.join(superscripts)
