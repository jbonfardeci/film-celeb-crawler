from typing import List, Dict
from types import SimpleNamespace
import json

class Film:
    FilmTitle: str = None
    Seasons: List[int]
    Years: List[int]
    FilmType: str = None
    ReleaseDate: str = None
    StudioName: str = None
    Producer: str = None
    Genres: List[str]
    Creators: List[str]
    Certificate: str = None
    Popularity: int = None
    ImdbUserReviews: int = None
    ImdbCriticReviews: int = None
    Rating: int
    Budget: int = None
    BoxOfficeRevenue: int = None
    DomesticBoxOfficeRevenue: int = None
    DataSource: str = None


class CelebRole:
    FilmTitle: str = None
    FilmUrl: str = None
    Year: str = None
    Role: str = None
    CharacterName: str = None


class CelebAward:
    AwardCategory: str = None
    AwardName: str = None
    AwardType: str = None
    AwardFor: str = None
    Year: str = None
    FilmTitle: str = None

class Celeb:
    FullName: str = None
    FirstName: str = None 
    LastName: str = None
    PhotoUrl: str = None
    Height: float = None
    Gender: str = None
    DOB: str = None
    BornIn: str = None
    DOD: str = None
    MaritalStatus: str = None
    Location: str = None
    Rank: int = None
    DomesticBoxOfficeRevenue: int = None
    AverageDomesticBoxOfficeRevenue: int = None
    LocalDataSourcePath: str = None
    Trademark: str = None
    DataSourceUrl: str = None
    AstrologicalSign: str = None
    AwardsUrl: str = None
    AwardNominations: int = None
    AwardsWins: int = None
    # Films: List[Film] = None
    Roles: List[CelebRole] = None
    # Awards: List[CelebAward] = None

    def toJson(self, indent=0):
        return json.dumps(self, default=lambda o: o.__dict__, indent=indent)