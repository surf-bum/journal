import os


class EnvMeta(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Value):
                attrs[attr_name] = attr_value.get(attr_name)
        return super().__new__(cls, name, bases, attrs)


class Value:
    def __init__(self, default, prefix=None):
        self.default = default

    def get(self, attr_name):
        env_key = attr_name
        return os.getenv(env_key, self.default)
