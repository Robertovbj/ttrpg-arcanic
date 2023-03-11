from .field import Field

class Page:
    def __init__(self, description, fields=None):
        self.description = description
        self.fields = fields or []

    def add_field(self, field):
        self.fields.append(field)

    def to_dict(self):
        return {
            'description': self.description,
            'fields': [field.to_dict() for field in self.fields]
        }
