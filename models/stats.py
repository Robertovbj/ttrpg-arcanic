from .page import Page
from .field import Field
from emojis import WHITE_SQUARE, INVISIBLE, CHECK_SQUARE

class StatsPage(Page):
    def __init__(self, stats_list: list[tuple]):
        super().__init__()

        stats_names = ['Cool', 'Hard', 'Hot', 'Sharp', 'Weird']

        stats_txt = ''
        stats_value = ''
        for i in range(5):
            stats_txt += (CHECK_SQUARE if stats_list[i][0] == 1 else WHITE_SQUARE) + f"  {stats_names[i]}\n"
            stats_value += f"[{stats_list[i][1]}]\n" 

        self.fields = [
            Field("STATS", f"{stats_txt}", True),
            Field(f"{INVISIBLE}", f"{stats_value}", True)
        ]