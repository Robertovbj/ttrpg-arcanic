from .page import Page
from .field import Field
from emojis import INVISIBLE
from configs.database import Database
import sqlite3

class Character:
    def __init__(self):
        self.db = Database()

    def create_new(self, data: dict):
        """Create a new character for the user in this server."""
        insert_character = f"INSERT INTO CHARACTERS(CHR_SERVER_ID, CHR_USER_ID, CHR_NAME, FK_PLB_ID, CHR_IMAGE) VALUES (?, ?, ?, ?, ?);"
        insert_stats = f"INSERT INTO STATS(STT_STAT, STT_VALUE, FK_CHR_ID) VALUES (?, ?, ?), (?, ?, ?), (?, ?, ?), (?, ?, ?), (?, ?, ?);"

        try:
            self.db.cursor.execute(insert_character, (data['server'], data['user'], data['name'], data['playbook'], data['image']))
            insert_id = self.db.cursor.lastrowid
            self.db.cursor.execute(insert_stats, (1, data['stats']['cool'], insert_id, 2, data['stats']['hard'], insert_id, 3, data['stats']['hot'], insert_id, 4, data['stats']['sharp'], insert_id, 5, data['stats']['weird'], insert_id))
            self.db.conn.commit()
        except sqlite3.Error:
            self.db.conn.rollback()
            return "Sorry, something went wrong"
        finally:
            self.db.close()
        return None
    
    def check_if_exists(self, user: str, server: str) -> int:
        """Returns 0 if the user doesn't have a character in the server. Returns 1 otherwise."""
        return self.db.select("CHARACTERS", columns=["COUNT(*)"], where=f"CHR_SERVER_ID = {server} AND CHR_USER_ID = {user}")[0][0]
    
    def get_character_name(self, user: str, server: str) -> str:
        """Returns character name"""
        return self.db.select("CHARACTERS", columns=["CHR_NAME"], where=f"CHR_SERVER_ID = {server} AND CHR_USER_ID = {user}")[0][0]
    
    def get_character_id(self, user: str, server: str) -> int:
        """Returns character id"""
        return self.db.select("CHARACTERS", columns=["CHR_ID"], where=f"CHR_SERVER_ID = {server} AND CHR_USER_ID = {user}")[0][0]

    def delete_character(self, user: str, server: str) -> None:
        """Deletes character"""
        id = self.get_character_id(user, server)
        self.db.delete("CHARACTERS", 'CHR_ID', id)

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