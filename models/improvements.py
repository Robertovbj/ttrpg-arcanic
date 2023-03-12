from .page import Page
from .field import Field
from emojis import RED_SQUARE, WHITE_SQUARE, CHECK_SQUARE 

class ImprovementPage(Page):
    def __init__(self):
        super().__init__("Improvement")
        self.fields = [
            Field(f"EXPERIENCE", f"""{RED_SQUARE}{RED_SQUARE}{WHITE_SQUARE}{WHITE_SQUARE}{WHITE_SQUARE}"""),
            Field(f"IMPROVEMENT", f"""{CHECK_SQUARE} get +1 sharp (max sharp+3)
            {CHECK_SQUARE} get +1 cool (max cool+2)
            {WHITE_SQUARE} get +1 hard (max hard+2)
            {WHITE_SQUARE} get +1 hard (max hard+2)
            {WHITE_SQUARE} get +1 weird (max weird+2)
            {CHECK_SQUARE} get a new angel move
            {WHITE_SQUARE} get a new angel move
            {WHITE_SQUARE} get 2 gigs (detail) and moonlighting
            {WHITE_SQUARE} get a move from another playbook
            {WHITE_SQUARE} get a move from another playbook
            ----------------------------------
            {WHITE_SQUARE} get +1 to any stat (max stat+3)
            {WHITE_SQUARE} retire your character (to safety)
            {WHITE_SQUARE} create a second character to play
            {WHITE_SQUARE} change your character to a new type
            {WHITE_SQUARE} choose 3 basic moves and advance them.
            {WHITE_SQUARE} advance the other 4 basic moves.""")
        ]