class FlexetException(Exception):
    pass


def handle(message_generator):
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise FlexetException(f"{message_generator(*args, **kwargs)}")
        return wrapper
    return decorator
