import json


def humanize(string):
    # return " ".join(string.split("_")).capitalize()

    if "count" in string and len(string.split("count")) > 1:
        string = string.replace("count", "")

    string = string.replace("_", " ")
    string = string.strip()
    string = string.capitalize()

    return string


def read_from_json(path):
    with open(path, "r") as file:
        data = json.loads(file.read())

    return data


def save_to_json(path, data):
    with open(path, "w") as file:
        file.write(json.dumps(data))
