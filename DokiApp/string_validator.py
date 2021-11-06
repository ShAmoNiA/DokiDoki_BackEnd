from re import search as validate_regex


def is_valid_username(text: str):
    username_regex = r'^(?![_.0-9])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'
    return validate_regex(username_regex, text)


def is_valid_email(text: str):
    email_regex = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    email_regex_prof = r'(?:[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*|\"(?:[' \
                       r'\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(' \
                       r'?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[' \
                       r'0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[' \
                       r'0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[' \
                       r'\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    return validate_regex(email_regex, text)


def is_hard_password(text: str):
    return len(text) > 7


def is_valid_phone_number(text: str):
    phone_regex = r'^(0|0098|\+98)9\d{9}$'
    return validate_regex(phone_regex, text)
