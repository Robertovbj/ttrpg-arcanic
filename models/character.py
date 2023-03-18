from .page import Page
from .field import Field
from emojis import INVISIBLE
from configs.database import Database
import sqlite3
import math

class Character:
    def __init__(self, user: str, server: str):
        self.db = Database()
        self.user = user
        self.server = server
        
    def create_new(self, data: dict):
        """Create a new character for the user in this server."""
        insert_character = f"INSERT INTO CHARACTERS(CHR_SERVER_ID, CHR_USER_ID, CHR_NAME, FK_PLB_ID, CHR_IMAGE) VALUES (?, ?, ?, ?, ?);"
        insert_stats = f"INSERT INTO STATS(STT_STAT, STT_VALUE, FK_CHR_ID) VALUES (?, ?, ?), (?, ?, ?), (?, ?, ?), (?, ?, ?), (?, ?, ?);"
        insert_improvements = f"INSERT INTO CHARACTER_IMPROVEMENTS(FK_CHR_ID, FK_IMP_ID) VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?);"

        try:
            self.db.cursor.execute(insert_character, (self.server, self.user, data['name'], data['playbook'], data['image']))
            insert_id = self.db.cursor.lastrowid
            self.db.cursor.execute(insert_stats, (1, data['stats']['cool'], insert_id, 2, data['stats']['hard'], insert_id, 3, data['stats']['hot'], insert_id, 4, data['stats']['sharp'], insert_id, 5, data['stats']['weird'], insert_id))
            shift = 7+(data['playbook']-1)*10
            self.db.cursor.execute(insert_improvements, (insert_id, shift, insert_id, shift+1, insert_id, shift+2, insert_id, shift+3, insert_id, shift+4, insert_id, shift+5, insert_id, shift+6, insert_id, shift+7, insert_id, shift+8, insert_id, shift+9, insert_id, 1, insert_id, 2, insert_id, 3, insert_id, 4, insert_id, 5, insert_id, 6))
            self.db.conn.commit()
        except sqlite3.Error:
            self.db.conn.rollback()
            return "Sorry, something went wrong"
        finally:
            self.db.close()
        return None
    
    def check_if_exists(self) -> int:
        """Returns 0 if the user doesn't have a character in the server. Returns 1 otherwise."""
        return self.db.select("CHARACTERS", columns=["COUNT(*)"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user}")[0][0]
    
    def get_character_name(self) -> str:
        """Returns character name"""
        return self.db.select("CHARACTERS", columns=["CHR_NAME"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user}")[0][0]
    
    def get_character_id(self) -> int:
        """Returns character id"""
        return self.db.select("CHARACTERS", columns=["CHR_ID"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user}")[0][0]

    def delete_character(self) -> None:
        """Deletes character"""
        id = self.get_character_id()
        self.db.delete("CHARACTERS", 'CHR_ID', id)

    def get_exp(self) -> int:
        """Returns character exp"""
        query = self.db.select("CHARACTERS", columns=["CHR_EXP", "CHR_IMPROVEMENT"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user}")
        return query[0][0], query[0][1]

    def add_exp(self, amount: int) -> int:
        exp, imp = self.get_exp()
        exp += amount
        imp += math.floor(exp / 5)
        exp = exp % 5
        self.db.update("CHARACTERS", "CHR_ID", self.get_character_id(), CHR_EXP = exp, CHR_IMPROVEMENT = imp)
        return imp
    
    def get_barter(self) -> int:
        """Returns character barter"""
        query = self.db.select("CHARACTERS", columns=["CHR_BARTER"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user}")
        return query[0][0]

    def add_barter(self, amount: int) -> int:
        barter = self.get_barter() + amount
        if barter > -1:
            self.db.update("CHARACTERS", "CHR_ID", self.get_character_id(), CHR_BARTER = barter)
        return barter

    def get_harms(self) -> tuple:
        """Returns character harms"""
        return self.db.select("CHARACTERS", columns=["CHR_HARM", "CHR_STABILIZED", "CHR_SHATTERED", "CHR_CRIPPLED", "CHR_DISFIGURED", "CHR_BROKEN"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user}")[0]

    def get_basic_profile(self) -> tuple:
        """Returns character id, name, playbook (name) and image"""
        return self.db.select("CHARACTERS, PLAYBOOK", columns=["CHR_ID", "CHR_NAME", "PLB_NAME", "CHR_IMAGE"], where=f"CHR_SERVER_ID = {self.server} AND CHR_USER_ID = {self.user} AND FK_PLB_ID = PLB_ID")[0]

    def update_harm(self, amount: int) -> None:
        """Updates harm amount. Can also heal"""
        self.db.update("CHARACTERS", "CHR_ID", self.get_character_id(), CHR_HARM = amount)

    def update_dharms(self, harms: tuple) -> None:
        """Updates harm amount and debilities. Can also heal and remove debilities."""
        self.db.update("CHARACTERS", "CHR_ID", self.get_character_id(), CHR_HARM = harms[0], CHR_STABILIZED = harms[1], CHR_SHATTERED = harms[2], CHR_CRIPPLED = harms[3], CHR_DISFIGURED = harms[4], CHR_BROKEN = harms[5])

    def get_char_moves(self) -> tuple[list[tuple], str]:
        """Gets specified character moves"""
        moves = self.db.select("CHARACTERS AS c, CHARACTER_MOVES AS cm, MOVES AS m", columns=["m.*"], where=f"c.CHR_USER_ID = {self.user} AND c.CHR_SERVER_ID = {self.server} AND c.CHR_ID = cm.FK_CHR_ID AND cm.FK_MVS_ID = m.MVS_ID")
        special = self.db.select("CHARACTERS, PLAYBOOK", columns=["PLB_SPECIAL"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND PLB_ID = FK_PLB_ID")
        return moves, special[0][0] 
    
    def get_hx_list(self):
        """Gets all hx from a character"""
        return self.db.select("CHARACTERS AS cto, CHARACTERS AS cfrom, HX AS h", columns=["cfrom.CHR_NAME", "cto.CHR_NAME", "h.HX_VALUE"], where=f"cfrom.CHR_USER_ID = {self.user} AND cfrom.CHR_SERVER_ID = {self.server} AND cto.CHR_SERVER_ID = cfrom.CHR_SERVER_ID AND cfrom.CHR_ID = h.FK_CHR_ID_FROM AND cto.CHR_ID = h.FK_CHR_ID_TO")

    def get_hx_ind(self, name_to: int):
        """Gets hx from a character to another"""
        return self.db.select("CHARACTERS AS cto, CHARACTERS AS cfrom, HX AS h", columns=["cfrom.CHR_NAME", "cto.CHR_NAME", "h.HX_VALUE"], where=f"cfrom.CHR_USER_ID = {self.user} AND cfrom.CHR_SERVER_ID = {self.server} AND cto.CHR_SERVER_ID = cfrom.CHR_SERVER_ID AND cfrom.CHR_ID = h.FK_CHR_ID_FROM AND cto.CHR_ID = h.FK_CHR_ID_TO AND cto.CHR_NAME = '{name_to}'")

    def update_hx(self, pair_list):

        self.db.conn.execute('BEGIN')
        update_query = "INSERT INTO HX (FK_CHR_ID_FROM, FK_CHR_ID_TO, HX_VALUE) VALUES ((SELECT c1.CHR_ID FROM CHARACTERS c1 WHERE c1.CHR_USER_ID = ? AND c1.CHR_SERVER_ID = ?), (SELECT c2.CHR_ID FROM CHARACTERS c2 WHERE c2.CHR_NAME = ? AND c2.CHR_SERVER_ID = ?), ?) ON CONFLICT(FK_CHR_ID_FROM, FK_CHR_ID_TO) DO UPDATE SET HX_VALUE = EXCLUDED.HX_VALUE"

        try:
            for pair in pair_list:
                self.db.cursor.execute(update_query, (self.user, self.server, pair[0], self.server, pair[1]))
        except sqlite3.Error as e:
            print(e)
            self.db.conn.rollback()
            return "Sorry, something went wrong. Maybe you typed some character's name wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None

    def check_if_exists_name(self, name) -> int:
        """Returns 0 if theresn't a character with the specified name on the server. Returns 1 otherwise."""
        return self.db.select("CHARACTERS", columns=["COUNT(*)"], where=f"CHR_SERVER_ID = {self.server} AND CHR_NAME = '{name}'")[0][0]

    def get_improvements(self) -> list[tuple]:
        """Gets this character's improvements"""
        return self.db.select("CHARACTERS, CHARACTER_IMPROVEMENTS, IMPROVEMENTS", columns=["CHI_CHECKED", "IMP_TEXT"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND CHR_ID = FK_CHR_ID AND FK_IMP_ID = IMP_ID;")

class NewCharacterPage(Page):
    def __init__(self, playbooks, emoji):
        super().__init__()
        self.fields = [
            Field(INVISIBLE, f"{emoji}", True),
            Field("Playbooks", f"{playbooks}", True)
        ]

class ChooseSetPage(Page):
    def __init__(self, sets):
        super().__init__()
        self.fields = [
            Field(f"Choose a stats set", f"{sets}")
        ]