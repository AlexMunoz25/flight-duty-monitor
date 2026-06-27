ALL = "all"


def clear_sentinel(value):
    return None if value in (None, "", ALL) else value
