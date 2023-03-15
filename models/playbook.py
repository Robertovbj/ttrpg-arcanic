from configs.database import Database

class Playbook:
    def __init__(self):
        self.db = Database()

    def get_playbooks(self) -> list[tuple[int, str, str, str]]:
        return self.db.select('PLAYBOOK')
    
    def get_count(self) -> int:
        return self.db.select('PLAYBOOK', ['COUNT(*)'])[0][0]
    
    def get_names(self) -> list[tuple[int, str]]:
        return self.db.select('PLAYBOOK', ['PLB_ID', 'PLB_NAME'])
