from typing import List, Dict
from types import SimpleNamespace
import json


class CelebRole:
    FilmTitle: str = None
    FilmUrl: str = None
    Year: str = None
    CharacterName: str = None
    Directors: List[str] = None
    Metascore: int = None
    UserReviews: int = None
    Popularity: int = None
    CriticReviews: int = None
    Writers: List[str] = None
    Stars: List[str] = None
    PlotKeywords: List[str] = None 
    ReleaseDate: str = None
    Genres: List[str] = None
    MotionPictureRating: str = None
    Budget: int = None
    OpeningWeekend: int = None
    Gross: int = None
    CumulativeWorldwideGross: int = None
    RuntimeMinutes: int = None
    ProductionCompanies: List[str] = None
    

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
    Roles: List[CelebRole] = None

    def toJson(self, indent=0):
        return json.dumps(self, default=lambda o: o.__dict__, indent=indent)