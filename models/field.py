class Field:
    def __init__(self, name, value, inline=False):
        self.name = name
        self.value = value
        self.inline = inline

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'inline': self.inline
        }
