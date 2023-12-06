import json

_config = None


def get_config():
    global _config
    if not _config:
        with open("config.json", "r") as fp:
            _config = json.load(fp)
    return _config
