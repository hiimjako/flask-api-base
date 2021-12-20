from os import environ, path

dot_env_var = {}

if path.exists(".env"):
    for line in open(".env"):
        var = line.strip().split("=")
        if len(var) == 2:
            dot_env_var[var[0]] = var[1].replace('"', "")


def get_env_path(variable: str) -> str:
    """Return an env variabile, throws error if not exists (env >> .env)"""
    try:
        value = environ.get(variable)
        if value is None:
            if variable in dot_env_var:
                return dot_env_var[variable]
            raise KeyError
        return value
    except KeyError:
        print(f"Missing {variable} env!")
        exit(1)
