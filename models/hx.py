from .page import Page
from .field import Field
from emojis import INVISIBLE

class HxPage(Page):
    def __init__(self, hx: list[tuple]):
        super().__init__()

        players = '' 
        status = ''

        for i in range(len(hx)):
            if hx[i][2] != 0:
                players += str(hx[i][1]) +'\n'
                status += '[' + str(hx[i][2]) + ']\n'

        self.fields = [
            Field("HX", f"{status}", True),
            Field(f"{INVISIBLE}", f"{players}", True)
        ]