from re import search as validate_regex


def is_valid_username(text: str):
    username_regex = r'^(?![_.0-9])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'
    return validate_regex(username_regex, text)


def is_valid_email(text: str):
    email_regex = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    return validate_regex(email_regex, text)


def is_hard_password(text: str):
    return len(text) > 7


def is_valid_phone_number(text: str):
    phone_regex = r'^(0|0098|\+98)9\d{9}$'
    return validate_regex(phone_regex, text)
