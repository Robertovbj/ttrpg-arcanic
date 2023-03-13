from .page import Page
from .field import Field

class InventoryPage(Page):
    def __init__(self):
        super().__init__()
        self.fields = [
            Field(f"GEAR", f""".38 revolver
            A piece worth 1-armor"""),
            Field(f"BACKPACK", f"""Banter: 3
            Angel kit
            Oddments worth 1-barter""")
        ]