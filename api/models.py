from pydantic import BaseModel

# Request body model
class userLoginData(BaseModel):
    user_name: str
    password: str
