from os import environ


def get_env_path(variable: str) -> str:
    """Return an env variabile, throws error if not exists"""
    try:
        value = environ.get(variable)
        if value is None:
            raise KeyError
        return value
    except KeyError:
        print(f"Missing {variable} env!")
        exit(1)
