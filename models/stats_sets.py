from configs.database import Database

class StatsSets:
    def __init__(self):
        self.db = Database()

    def get_stats_sets_for_pb(self, pb: int):
        return self.db.select('STATS_SETS', where=f'STS_PLAYBOOK = {pb}')
