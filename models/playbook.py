from configs.database import Database

class Playbook:
    def __init__(self):
        self.db = Database()

    def get_playbooks(self):
        return self.db.select('PLAYBOOK')
    
    def get_count(self):
        return self.db.select('PLAYBOOK', ['COUNT(*)'])[0][0]
