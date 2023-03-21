from .page import Page
from .field import Field
from emojis import RED_SQUARE, WHITE_SQUARE, CHECK_SQUARE 

class ImprovementPage(Page):
    def __init__(self, exp: int, imp_points: int, imp_list: list[tuple]):
        super().__init__()

        white = [WHITE_SQUARE, WHITE_SQUARE, WHITE_SQUARE, WHITE_SQUARE, WHITE_SQUARE]
        color = [RED_SQUARE, RED_SQUARE, RED_SQUARE, RED_SQUARE, RED_SQUARE]

        exp_bar = "".join(color[0:exp])
        exp_bar += "".join(white[exp:5])

        # In case the character changed type
        if len(imp_list) == 26:
            imp_list = imp_list[-10:] + imp_list[10:-10] + imp_list[:10]

        imp_text = ""
        for imp in imp_list[0:10]:
            imp_text += (CHECK_SQUARE if imp[0] == 1 else WHITE_SQUARE) + "  " + imp[1] + "\n"
        imp_text += "----------------------------------\n"
        for imp in imp_list[10:16]:
            imp_text += (CHECK_SQUARE if imp[0] == 1 else WHITE_SQUARE) + "  " + imp[1] + "\n"
        if len(imp_list) == 26:
            imp_text += "----------------------------------\n"
            for imp in imp_list[16:26]:
                imp_text += (CHECK_SQUARE if imp[0] == 1 else WHITE_SQUARE) + "  " + imp[1] + "\n"

        self.fields = [
            Field(f"EXPERIENCE", f"""{exp_bar}\nImprovement points: {imp_points}"""),
            Field(f"IMPROVEMENT", f"""{imp_text}""")
        ]