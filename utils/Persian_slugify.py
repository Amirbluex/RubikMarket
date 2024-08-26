import re


def persian_slugify(text):
    # Replace non-alphanumeric characters with empty string
    text = re.sub(r'[^a-zA-Z0-9آ-ی\s]', '', text)

    # Replace spaces with hyphens
    text = re.sub(r'\s', '-', text)

    # Remove any consecutive hyphens and trailing hyphens
    text = re.sub(r'[-]+', '-', text)
    text = text.strip('-')

    return text
