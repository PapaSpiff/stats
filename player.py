
class Player:
    player_id: str = "(unknown)"
    name:str
    specie: str
    kind: str
    

    def __init__(self: 'Player', raw_result: dict) -> None:
        self.player_id = raw_result['pid']
        self.name      = raw_result['name']
        self.specie    = raw_result['player_type']['species']
        self.kind      = raw_result['player_type']['style']

    def __eq__(self: 'Player', other: 'Player'):
        if isinstance(other, self.__class__):
            return self.player_id == other.player_id
        else:
            return False

    def __ne__(self: 'Player', other: 'Player'):
        return not self.__eq__(other)
