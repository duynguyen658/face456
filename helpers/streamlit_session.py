from fastapi import Request

IS_LOGGED_IN = "is_logged_in"


def set_session_by_key(request: Request, key: str, value):
    assert key is not None or value is not None, "Parameters key and value are required"
    request.session[key] = value


def get_session_by_key(request: Request, key: str):
    assert key is not None, "Parameter key is required"
    if not is_exist_key_in_session(request, key):
        return None
    return request.session[key]


def del_session_by_key(request: Request, key: str):
    assert key is not None, "Parameter key is required"
    if is_exist_key_in_session(request, key):
        del request.session[key]


def is_exist_key_in_session(request: Request, key: str):
    assert key is not None, "Parameter key is required"
    return key in request.session
