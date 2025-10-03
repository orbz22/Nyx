import json
import os

class Settings:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'minimize_to_tray': True
            }

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
