from pydantic import BaseModel, Field, ConfigDict
from typing import List
from src.dto.score_DTO import MatchScoreDTO

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
    score: MatchScoreDTO = Field(default_factory=MatchScoreDTO)

    model_config = ConfigDict(from_attributes=True)

class MatchDisplayDTO(BaseModel):
    player_one_name: str
    player_two_name: str
    winner_name: str


    # model_config = ConfigDict(from_attributes=True)



