from .page import Page
from .field import Field

class MovesPage(Page):
    def __init__(self):
        super().__init__()
        self.fields = [
            Field(f"ANGEL MOVES", f"""Sixth sense
            Infirmary"""),
            Field(f"SPECIAL MOVES", f"""If you and another character have sex, 
            your Hx with them on your sheet goes immediately 
            to +3, and they immediately get +1 to their Hx 
            with you on their sheet. If that brings their Hx 
            with you to +4, they reset it to +1 instead, as 
            usual, and so mark experience."""),
            Field("BASIC MOVES", f"""Do something under fire
            Go aggro
            Seize by force
            Seduce or manipulate
            Read a sitch
            Read a person
            Open your brain
            Help or interfere
            Session end""")
        ]