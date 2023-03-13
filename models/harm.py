from .page import Page
from .field import Field
from emojis import GREEN_SQUARE, YELLOW_SQUARE, ORANGE_SQUARE, RED_SQUARE, SKULL_CROSSBONES

class HarmPage(Page):
    def __init__(self):
        super().__init__()
        self.fields = [
            # Field("HARM", "-" * 14 + "3" + "-" * 8 + "6" + "-" * 8 + "9" + "-10-11-" + f"""{SKULL_CROSSBONES}-------
            # 12am |{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{GREEN_SQUARE}{YELLOW_SQUARE}{YELLOW_SQUARE}{YELLOW_SQUARE}{ORANGE_SQUARE}{ORANGE_SQUARE}{RED_SQUARE}| 12pm""", True),
            Field("HARM", f"""12pm
            {RED_SQUARE} {SKULL_CROSSBONES}
            {ORANGE_SQUARE} 11
            {ORANGE_SQUARE} 10
            {YELLOW_SQUARE} 9
            {YELLOW_SQUARE}
            {YELLOW_SQUARE}
            {GREEN_SQUARE} 6
            {GREEN_SQUARE}
            {GREEN_SQUARE}
            {GREEN_SQUARE} 3
            {GREEN_SQUARE}
            {GREEN_SQUARE}
            12am""", True),
            Field("Conditions", "Crippled\nBroken", True)
        ]