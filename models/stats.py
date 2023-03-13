from .page import Page
from .field import Field
from emojis import WHITE_SQUARE, INVISIBLE, CHECK_SQUARE

class StatsPage(Page):
    def __init__(self):
        super().__init__()
        self.fields = [
            Field("STATS", f"{WHITE_SQUARE} Cool\n{CHECK_SQUARE} Hard\n{WHITE_SQUARE} Hot\n{WHITE_SQUARE} Sharp\n{WHITE_SQUARE} Weird", True),
            Field(f"{INVISIBLE}", f"[+2]\n[+0]\n[+1]\n[+3]\n[-1]", True)
        ]