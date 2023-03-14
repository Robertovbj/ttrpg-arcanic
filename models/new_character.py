from .page import Page
from .field import Field
from emojis import INVISIBLE

class NewCharacterPage(Page):
    def __init__(self, playbooks, emoji):
        super().__init__()
        self.fields = [
            Field(INVISIBLE, f"{emoji}", True),
            Field("Playbooks", f"{playbooks}", True)
        ]

class ChooseSetPage(Page):
    def __init__(self):
        super().__init__()
        self.fields = [
            Field("HX", f"@Player2\n@Player3\n@Player5", True),
            Field(f"{INVISIBLE}", f"[+2]\n[-2]\n[+1]", True)
        ]