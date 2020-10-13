from typing import List, Dict
from types import SimpleNamespace

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
    Year: int = None
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
    NumMovies: int = 0
    AverageDomesticBoxOfficeRevenue: int = None
    BestKnownAs: str = None
    LocalDataSourcePath: str = None
    Trademark: str = None
    DataSourceUrl: str = None
    AstrologicalSign: str = None
    Films: List[Film] = None
    Roles: List[CelebRole] = None
    Award: List[CelebAward] = None