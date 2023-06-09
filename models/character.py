from .page import Page
from .field import Field
from emojis import INVISIBLE
from configs.database import Database
import sqlite3
import math
import itertools

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

    def get_exp(self) -> tuple[int, int]:
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

    def check_if_exists_name(self, name: str) -> int:
        """Returns 0 if theresn't a character with the specified name on the server. Returns id otherwise."""
        id = self.db.select("CHARACTERS", columns=["CHR_ID"], where=f"CHR_SERVER_ID = {self.server} AND CHR_NAME = '{name}'")
        if len(id) == 0:
            return 0
        else:
            return id[0][0]

    def change_user_by_name(self, name: str) -> str:
        """Changes self.user to named character's user snowflake"""
        self.user = self.db.select("CHARACTERS", columns=["CHR_USER_ID"], where=f"CHR_SERVER_ID = {self.server} AND CHR_NAME = '{name}'")[0][0]

    def get_improvements(self) -> list[tuple]:
        """Gets this character's improvements"""
        return self.db.select("CHARACTERS, CHARACTER_IMPROVEMENTS, IMPROVEMENTS", columns=["CHI_CHECKED", "IMP_TEXT", "CHI_ID"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND CHR_ID = FK_CHR_ID AND FK_IMP_ID = IMP_ID;")

    def add_improvement(self, number_list: list):
        """Adds improvements to the character"""
        self.db.conn.execute('BEGIN')
        update_query = "UPDATE CHARACTER_IMPROVEMENTS SET CHI_CHECKED = 1 WHERE CHI_ID = ?"
        update_imp = "UPDATE CHARACTERS SET CHR_IMPROVEMENT = CHR_IMPROVEMENT - ? WHERE CHR_USER_ID = ? AND CHR_SERVER_ID = ?"

        try:
            for number in number_list:
                self.db.cursor.execute(update_query, (number,))
        except sqlite3.Error as e:
            print(e)
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        self.db.cursor.execute(update_imp, (len(number_list), self.user, self.server))

        self.db.conn.commit()
        self.db.close()
        return None
    
    def remove_improvement(self, number_list: list):
        """Removes improvements from the character"""
        self.db.conn.execute('BEGIN')
        update_query = "UPDATE CHARACTER_IMPROVEMENTS SET CHI_CHECKED = 0 WHERE CHI_ID = ?"
        update_imp = "UPDATE CHARACTERS SET CHR_IMPROVEMENT = CHR_IMPROVEMENT + ? WHERE CHR_USER_ID = ? AND CHR_SERVER_ID = ?"

        try:
            for number in number_list:
                self.db.cursor.execute(update_query, (number,))
        except sqlite3.Error as e:
            print(e)
            self.db.conn.rollback()
            return "Sorry, something went wrong. Maybe you typed some character's name wrong."
        self.db.cursor.execute(update_imp, (len(number_list), self.user, self.server))

        self.db.conn.commit()
        self.db.close()
        return None
    
    def get_stats(self) -> list[tuple]:
        return self.db.select("STATS, CHARACTERS", columns=["STT_HIGHLIGHT", "STT_VALUE", "STT_STAT"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND CHR_ID = FK_CHR_ID;")

    def get_inventory(self) -> list[tuple]:
        return self.db.select("ITEMS, CHARACTERS", columns=["ITM_NAME", "ITM_DESCRIPTION", "ITM_QUANTITY", "ITM_EQUIPED"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND CHR_ID = FK_CHR_ID;")

    def highlight(self, stat_one: int, stat_two: int):

        id = self.get_character_id()
        update_query = f"UPDATE STATS SET STT_HIGHLIGHT = ? WHERE FK_CHR_ID = ? AND STT_STAT = ?;"
        try:
            for i in range(1, 6):
                value = 1 if i == stat_one or i == stat_two else 0
                self.db.cursor.execute(update_query, (value, id, i))
        except sqlite3.Error as e:
            print(e)
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None

    def stabilize(self) -> int:
        stabilized = self.db.select('CHARACTERS', columns=["CHR_ID", "CHR_STABILIZED"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server}")[0]
        stabilized_val = 0 if stabilized[1] == 1 else 1
        self.db.update("CHARACTERS", "CHR_ID", stabilized[0], CHR_STABILIZED = stabilized_val)
        return stabilized_val

    def reset_image(self) -> None:
        default = self.db.select("CHARACTERS, PLAYBOOK", columns=["PLB_IMAGE"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND FK_PLB_ID = PLB_ID")[0][0]
        self.set_image(default)

    def set_image(self, url: str) -> None:
        self.db.update("CHARACTERS", "CHR_ID", self.get_character_id(), CHR_IMAGE = url)

    def adjust_stats(self, stats: list, value: list) -> None:

        id = self.get_character_id()
        update_query = f"UPDATE STATS SET STT_VALUE = ? WHERE FK_CHR_ID = ? AND STT_STAT = ?;"

        try:
            for i in range(len(stats)):
                self.db.conn.execute(update_query, (value[i], id, stats[i]))
        except:
            self.db.conn.rollback()
            return "Sorry, something went wrong."
    
        self.db.conn.commit()
        self.db.close()
        return None

    def has_the_moves(self, id: int) -> int:
        chm_id = self.db.select("CHARACTER_MOVES, CHARACTERS", columns=["CHM_ID"], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server} AND FK_CHR_ID = CHR_ID AND FK_MVS_ID = {id}")
        return 0 if len(chm_id) == 0 else chm_id[0][0]

    def add_moves(self, moves: list) -> str:
        id = self.get_character_id()
        id_list = [id] * len(moves)  # Creates a list with the char id of interpolation
        zipped = list(zip(id_list, moves))  # Creates a list of tuples that intercalates with moves id like [(1, 10), (1, 12)]
        placeholders = ", ".join(["(?, ?)" for _ in range(len(zipped))])  # Creates as many placeholders needed
        values = tuple(itertools.chain(*zipped))  # Unpacks arguments so it can be used on the execute
        insert_query = f"INSERT INTO CHARACTER_MOVES(FK_CHR_ID, FK_MVS_ID) VALUES {placeholders}"

        try:
            self.db.conn.execute(insert_query, values)
        except:
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None

    def delete_moves(self, moves: list) -> str:
        id_list = ', '.join(str(id) for id in moves)
        query = f"DELETE FROM CHARACTER_MOVES WHERE CHM_ID IN ({id_list})"

        try:
            self.db.conn.execute(query)
        except:
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None

    def add_debility(self, column: str) -> str:
        update_query = f"UPDATE CHARACTERS SET {column} = 1 WHERE CHR_ID = ?"
        try:
            self.db.conn.execute(update_query, (self.get_character_id(),))
        except:
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None

    def check_for_debility(self, column: str) -> int:
        return self.db.select("CHARACTERS", columns=[column], where=f"CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server}")[0][0]

    def check_for_item(self, name: str) -> tuple:
        query = self.db.conn.execute(f"SELECT ITM_NAME, ITM_QUANTITY, ITM_ID, ITM_DESCRIPTION, ITM_EQUIPED FROM ITEMS, CHARACTERS WHERE ITM_NAME = ? AND FK_CHR_ID = CHR_ID AND CHR_USER_ID = {self.user} AND CHR_SERVER_ID = {self.server}", (name,))
        item = query.fetchall()
        if len(item) == 0:
            return 0
        else:
            return item[0]

    def insert_item(self, values: tuple) -> str:
        id = self.get_character_id()

        self.db.conn.execute('BEGIN')
        update_query = "INSERT INTO ITEMS (ITM_NAME, ITM_DESCRIPTION, ITM_QUANTITY, FK_CHR_ID) VALUES (?, ?, ?, ?) ON CONFLICT (ITM_NAME, FK_CHR_ID) DO UPDATE SET ITM_QUANTITY = EXCLUDED.ITM_QUANTITY + ITM_QUANTITY"

        try:
            for row in values:
                self.db.cursor.execute(update_query, (row[1], row[2], row[0], id))
        except:
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None

    def remove_item(self, values: tuple) -> None:
        for row in values:
            if row[0] == 0:
                self.db.delete("ITEMS", "ITM_ID", row[2])
            else:
                self.db.update("ITEMS", "ITM_ID", row[2], ITM_QUANTITY = row[0])

    def edit_description(self, values: tuple) -> str:
        update_query = "UPDATE ITEMS SET ITM_DESCRIPTION = ? WHERE ITM_ID = ?"
        try:
            for row in values:
                self.db.conn.execute(update_query, (row[0], row[1],))
        except:
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None
    
    def give_item(self, id_to: int, values: tuple) -> str:
        self.db.conn.execute('BEGIN')
        update_query = "INSERT INTO ITEMS (ITM_NAME, ITM_DESCRIPTION, ITM_QUANTITY, FK_CHR_ID) VALUES (?, ?, ?, ?) ON CONFLICT (ITM_NAME, FK_CHR_ID) DO UPDATE SET ITM_QUANTITY = EXCLUDED.ITM_QUANTITY + ITM_QUANTITY"

        try:
            for row in values:
                self.db.cursor.execute(update_query, (row[0], row[3], row[1], id_to))
                if row[2] == 0:
                    self.db.delete("ITEMS", "ITM_ID", row[4])
                else:
                    self.db.update("ITEMS", "ITM_ID", row[4], ITM_QUANTITY = row[2])
        except sqlite3.Error as e:
            print(e)
            self.db.conn.rollback()
            return "Sorry, something went wrong."
        
        self.db.conn.commit()
        self.db.close()
        return None
    
    def equip(self, values: tuple):
        self.db.update("ITEMS", "ITM_ID", values[0], ITM_EQUIPED = values[1])

    def final_advance(self):
        basic = self.get_basic_profile()
        stats = [row[1] for row in self.get_stats()]
        self.db.insert("FINAL_ADVANCE(FNA_SERVER_ID, FNA_CHR_NAME, FNA_PLB_NAME, FNA_COOL, FNA_HARD, FNA_HOT, FNA_SHARP, FNA_WEIRD)", (self.server, basic[1], basic[2], stats[0], stats[1], stats[2], stats[3], stats[4]))

    def get_players(self):
        return self.db.select("CHARACTERS", columns=["CHR_NAME"], where=f"CHR_SERVER_ID = {self.server}")
    
    def get_retired(self):
        return self.db.select("FINAL_ADVANCE", where=f"FNA_SERVER_ID = {self.server}")
    
    def new_type(self, playbook):
        id = self.get_character_id()
        self.db.update("CHARACTERS", "CHR_ID", id, FK_PLB_ID = playbook)
        insert_improvements = f"INSERT INTO CHARACTER_IMPROVEMENTS(FK_CHR_ID, FK_IMP_ID) VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?), (?, ?);"
        shift = 7+(playbook-1)*10
        self.db.cursor.execute(insert_improvements, (id, shift, id, shift+1, id, shift+2, id, shift+3, id, shift+4, id, shift+5, id, shift+6, id, shift+7, id, shift+8, id, shift+9))
        self.db.cursor.execute("UPDATE CHARACTER_IMPROVEMENTS SET CHI_CHECKED = 1 WHERE FK_CHR_ID = ? AND FK_IMP_ID = 4", (id,))
        self.db.conn.commit()

    def is_new_type(self):
        id = self.get_character_id()
        return self.db.select("CHARACTER_IMPROVEMENTS", columns=["CHI_CHECKED"], where=f"FK_CHR_ID = {id} AND FK_IMP_ID = 4")[0][0]

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

class AllCharacters(Page):
    def __init__(self, char_names):
        super().__init__()
        self.fields = [
            Field(f"Names", f"{char_names}")
        ]