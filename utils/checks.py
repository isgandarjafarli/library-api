from errors import bad_request, not_found


def require_fields(data, fields, message):
    for field in fields:
        if not data.get(field):
            raise bad_request(message)

def require_found(item, message):
    if item is None:
        raise not_found(message)
    return item
