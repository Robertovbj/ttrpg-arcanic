from .field import Field

class Page:
    def __init__(self, fields=None):
        self.fields = fields or []

    def add_field(self, field):
        self.fields.append(field)

    def to_dict(self):
        return {
            'fields': [field.to_dict() for field in self.fields]
        }
