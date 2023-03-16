from .page import Page
from .field import Field
from emojis import GREEN_SQUARE, YELLOW_SQUARE, ORANGE_SQUARE, RED_SQUARE, SKULL_CROSSBONES, WHITE_SQUARE

class HarmPage(Page):
    def __init__(self, harm: int):
        super().__init__()

        color = [f'{RED_SQUARE} {SKULL_CROSSBONES}', f'{ORANGE_SQUARE} 11', f'{ORANGE_SQUARE} 10', f'{YELLOW_SQUARE} 9\n{YELLOW_SQUARE}\n{YELLOW_SQUARE}', f'{GREEN_SQUARE} 6\n{GREEN_SQUARE}\n{GREEN_SQUARE}', f'{GREEN_SQUARE} 3\n{GREEN_SQUARE}\n{GREEN_SQUARE}']
        white = [f'{WHITE_SQUARE} {SKULL_CROSSBONES}', f'{WHITE_SQUARE} 11', f'{WHITE_SQUARE} 10', f'{WHITE_SQUARE} 9\n{WHITE_SQUARE}\n{WHITE_SQUARE}', f'{WHITE_SQUARE} 6\n{WHITE_SQUARE}\n{WHITE_SQUARE}', f'{WHITE_SQUARE} 3\n{WHITE_SQUARE}\n{WHITE_SQUARE}']
        conditions = ['Stabilized', 'Shattered', 'Crippled', 'Disfigured', 'Broken']

        harm_bar = "12pm\n"
        harm_bar += "\n".join(white[0:6-harm[0]]) + "\n" if harm != 6 else ""
        harm_bar += "\n".join(color[6-harm[0]:6])
        harm_bar += ("\n" if harm != 0 else "") + "12am"

        conditions_text = ''.join(('_' + conditions[i-1] + '_\n') if harm[i] == 1 else '' for i in range(1, len(harm))) 

        self.fields = [
            # Field("HARM", "-" * 14 + "3" + "-" * 8 + "6" + "-" * 8 + "9" + "-10-11-" + f"""{SKULL_CROSSBONES}-------
            # 12am |{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{YELLOW_SQUARE}{YELLOW_SQUARE}{YELLOW_SQUARE}{ORANGE_SQUARE}{ORANGE_SQUARE}{RED_SQUARE}| 12pm""", True),
            Field("Harm", f"""{harm_bar}""", True),
            Field("Conditions", f"{conditions_text}", True)
        ]