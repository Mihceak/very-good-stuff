from info import database
from pyairtable.formulas import match


class Player:
    def __init__(self, player_id, name, progress=0, endingpoints=0, language=0):
        self.__id = player_id
        self.__name = name
        self.__language = language
        self.__progress = progress
        self.__endingpoints = endingpoints

    def get_id(self) -> int:
        return self.__id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_language(self):
        return self.__language

    def set_language(self, language):
        self.__language = language

    def get_progress(self):
        return self.__progress

    def set_progress(self, progress):
        self.__progress = progress

    def increaseEP(self, character):
        if character == "Vika":
            self.__endingpoints += 1
        elif character == "Nastya":
            self.__endingpoints += 10
        elif character == "Tanya":
            self.__endingpoints += 100

    def decrementEP(self):
        self.__endingpoints -= 1

    def create(self):
        """Creates a new player in the database"""
        database.player_table.create({
            'player_id': self.__id,
            'name': self.__name,
            'language': self.__language,
            'progress': self.__progress,
            'endingpoints': self.__endingpoints
        })

    def save_all(self):
        """Saves all data to the database"""
        player = match({'player_id': self.get_id()})
        database.player_table.update(database.player_table.first(formula=player)['id'], {
            'name': self.__name,
            'language': self.__language,
            'progress': self.__progress,
            'endingpoints': self.__endingpoints
        })

    def save_progress(self):
        """Saves progress and ending points to the database"""
        player = match({'player_id': self.get_id()})
        database.player_table.update(database.player_table.first(formula=player)['id'], {
            'progress': self.__progress,
            'endingpoints': self.__endingpoints
        })

    def load(self):
        try:
            player = match({'player_id': self.get_id()})
            self.set_name(database.player_table.first(formula=player)['fields']['name'])
            self.set_language(database.player_table.first(formula=player)['fields']['language'])
            self.set_progress(database.player_table.first(formula=player)['fields']['progress'])
            self.__endingpoints = database.player_table.first(formula=player)['fields']['endingpoints']
        except:
            self.create()
            return

    def leave_feedback(self, feedback):
        player = match({'player_id': self.get_id()})
        database.player_table.update(database.player_table.first(formula=player)['id'], {
            'feedback': feedback
        })


players = {}