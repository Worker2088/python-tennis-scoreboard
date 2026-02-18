from pydantic import BaseModel, Field, ConfigDict

class MatchCreateDTO(BaseModel):
    # uuid: str
    player_one_name: str
    player_two_name: str
    # winner_id: int
    # score: str

class MatchDTO(BaseModel):
    id: int
    uuid: str
    player_one_name: str
    player_two_name: str
    winner_id: int | None
    score: str

class MatchScoreDTO(BaseModel):
    set1: int | None
    set2: int | None
    game1: int | None
    game2: int | None
    point1: int
    point2: int

# class MatchDTO(BaseModel):
#     id: int
#     uuid: str
#     player_one_id: int
#     player_two_id: int
#     winner_id: int | None
#     score: str

    model_config = ConfigDict(from_attributes=True)



