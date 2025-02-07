from pydantic import BaseModel

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
