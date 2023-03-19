from .page import Page
from .field import Field

class InventoryPage(Page):
    def __init__(self, inv: list[tuple], barter: int):
        super().__init__()

        gear_txt = ''
        backpack_txt = f'Barter: {barter}\n'

        for item in inv:
            if item[3] == 1:
                gear_txt += f"**{item[2]}x {item[0]}** -> _{item[1]}_\n" 
            else:
                backpack_txt += f"**{item[2]}x {item[0]}** -> _{item[1]}_\n" 


        self.fields = [
            Field(f"GEAR", f"""{gear_txt}"""),
            Field(f"BACKPACK", f"""{backpack_txt}""")
        ]