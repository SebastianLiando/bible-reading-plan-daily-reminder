import os


def get_asset(name: str) -> str:
    """Returns the path to the asset.

    Args:
        name (str): The asset path. Relative to the assets folder.

    Returns:
        str: The path to the asset.
    """
    
    # https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
    __location__ = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))

    return os.path.join(__location__, name)
