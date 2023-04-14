class Player:
    def __init__(self, player_id, name, progress=0):
        self.__id = player_id
        self.__name = name
        self.__progress = progress

    def save_progress(self, progress):
        self.__progress = progress

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

