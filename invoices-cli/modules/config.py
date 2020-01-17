import json


class Config:
    """
    Loads, updates, and saves the program's settings
    """

    def __init__(self, path):
        self.path = path
        self.settings = self.load(path)

    def load(self, path=""):
        data = {}
        assert path.endswith(".json")
        with open(path) as json_file:
            data = json.loads(json_file.read())
        return data

    def get(self, setting=""):
        return self.settings[setting] if setting in self.settings else ""

    def set(self, key, value=""):
        if not key:
            return
        self.settings[key] = value

    def save(self):
        with open(self.path, "w") as output_file:
            json.dump(self.settings, output_file)
