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
    
    def get_id_by_name(self, name: str) -> int:
        name = name.replace("'", "''")
        id =  self.db.select("MOVES", columns=["MVS_ID"], where=f"MVS_NAME = '{name}'")
        return 0 if len(id) == 0 else id[0][0]