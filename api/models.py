from pydantic import BaseModel
from typing import Optional

# Request body model
class userRegisterData(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str

class userLoginData(BaseModel):
    username: str
    password: str

# Follow request body model
class userFollowRequest(BaseModel):
    follower_id: int
    following_id: int

# New Club creation body model
class newClub(BaseModel):
    owner: int
    name: str
    description: str 
    club_tag: str

## The following are returned structures
class User(BaseModel):
    username: str
    first_name: str 
    last_name: str
    total_dance_time: int 
    sessions_attended: int 
    followers: int
    following: int

class postsUserRequest(BaseModel):
    user_id: int
    timestamp: str

class postsClubRequest(BaseModel):
    club_id: int
    timestamp: str

class ClubPost(BaseModel):
    club_id: int
    title : str
    description : Optional[str] = None
    video_url: Optional[str] = None
    picture_url: Optional[str] = None
    event_id : int
    created_on : str

class UserPost(BaseModel):
    owner : int
    title : str
    description : Optional[str] = None
    video_url : Optional[str] = None
    picture_url : Optional[str] = None
    created_on : str

class ClubEvent(BaseModel):
    club_id: int
    title : str
    description : str    
    date : str
    time : str
    duration_minutes :  int
    location : str
    latitude : str
    longitude : str
    picture_url : Optional[str] = None
    created_on : str

class EventInterest(BaseModel):
    user_id : int
    event_id : int

class ClubMember(BaseModel):
    club_id : int
    user_id : int
