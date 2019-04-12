from functools import wraps

from flask import request

from redis_store import store


def token_required(f):
    @wraps(f)
    def fnc(*args, **kwargs):
        if (
                'X-API-TOKEN' in request.headers and
                store.get_token_data(get_token_from_request_headers())
        ):
            return f(*args, **kwargs)
        return {}, 401
    return fnc


def get_token_from_request_headers():
    return request.headers['X-API-TOKEN']



