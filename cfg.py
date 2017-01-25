def load_config():
    from json import load
    with open("config.json") as fin:
        return load(fin)

def cfg(key):
    cfg = load_config()
    return cfg[key]