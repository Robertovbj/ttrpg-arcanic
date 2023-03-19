from .page import Page
from .field import Field
from configs.database import Database

class MovesPage(Page):
    def __init__(self, moves: str, special: str = None):
        super().__init__()
        self.moves = moves
        self.special = special
        self.fields = []
        if self.special is not None:
            self.fields.append(Field(f"Special Moves", f"{self.special}"))
        if not self.moves == "":
            self.fields.append(Field(f"Moves", f"""{self.moves}"""))

class Moves:
    def __init__(self):
        self.db = Database()

    def get_all_moves(self) -> list[tuple]:
        """Returns all moves stored in the database"""
        return self.db.select("MOVES")