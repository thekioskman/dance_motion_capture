from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db_connect import connect
from crud import *
from models import *
import os

# Initialize FastAPI app
app = FastAPI()

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # if security needed, change this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "/tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.delete("/reset")
def clear_all_data():
    """
    Delete all data from the database for testing purposes.
    """
    try:
        clear_all_tables()
        return {"message": "All tables cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing tables: {str(e)}")

# Video Comparison Endpoint
@app.post("/compare")
async def compare_endpoint(video1: UploadFile = File(...), video2: UploadFile = File(...)):
    """
    Endpoint to compare two uploaded videos.
    """
    # Save uploaded files
    video1_path = os.path.join(UPLOAD_FOLDER, video1.filename)
    video2_path = os.path.join(UPLOAD_FOLDER, video2.filename)

    try:
        with open(video1_path, "wb") as f:
            f.write(await video1.read())
        with open(video2_path, "wb") as f:
            f.write(await video2.read())

        # Call the function to compare videos
        result = compare_uploaded_videos(video1_path, video2_path)
    except Exception as e:
        error_message = str(e)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": error_message}
        )
    finally:
        # Clean up uploaded files
        if os.path.exists(video1_path):
            os.remove(video1_path)
        if os.path.exists(video2_path):
            os.remove(video2_path)

    return JSONResponse(content=result)

@app.get("/posts/{user_id}")
def get_posts():
    pass


# User Login
@app.post("/login")
def login(request_body: userLoginData):
    '''
    Authenticate user login
    '''
    username = request_body.username
    password = request_body.password
    try:
        result = authenticate_user(username, password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Register a user
@app.post("/register")
def register(request_body: userRegisterData):
    '''
    Register a new user in the system
    '''
    username = request_body.username
    password = request_body.password
    first_name = request_body.first_name
    last_name = request_body.last_name
    
    try:
        register_user(username, password, first_name, last_name)
        return {"message": "User registered successfully.", "success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get user details by user id
@app.get("/user/{user_id}")
def get_user(user_id: str):
    '''
    Get user details by user_id
    '''
    try:
        user = get_user_by_id(user_id)
        return {"message": "User found successfully.", "success": True, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add new user that current user is following
@app.post("/follow")
def add_following(follow_request: userFollowRequest):
    try:
        add_follower_following(follow_request.follower_id, follow_request.following_id)
        return {"message": f"{follow_request.follower_id} successfully followed {follow_request.following_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Remove user that user is currently follows and unfollow them
@app.delete("/unfollow")
def remove_following(unfollow_request: userFollowRequest):
    try:
        remove_follower_following(unfollow_request.follower_id, unfollow_request.following_id)
        return {"message": f"{unfollow_request.follower_id} successfully unfollowed {unfollow_request.following_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Get all accounts that a user follows
@app.get("/followings/{user_id}")
def get_followings(user_id: int):
    try:
        followings = get_user_followings(user_id)
        return {"following": followings}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching user followings: {str(e)}")
    
# Get all accounts that follows a user
@app.get("/followers/{user_id}")
def get_followers(user_id: int):
    try:
        followers = get_user_followers(user_id)
        return {"followers": followers}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching user followers: {str(e)}")

# Create a new club
@app.post("/club/new")
def create_club(club: newClub):
    try: 
        club_id = create_new_club(club.owner, club.name, club.description, club.club_tag)
        return {"message": f"New Club '{club.name}' was created successfully", "club_id": club_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating new club: {str(e)}")
    
# Get club details by id
@app.get("/club/{club_id}")
def get_club_details(club_id: int):
    try:
        club_details = get_club_by_id(club_id)
        return club_details
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching club details: {str(e)}")

# # Delete a club
# @app.delete("/club/delete/{club_id}")
# def delete_club(club_id: int):
#     try:
#         delete_club_by_id(club_id)
#         return {"message": f"Club with ID {club_id} deleted successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error deleting club: {str(e)}")

# # Add a member to a club
# @app.post("/club/{club_id}/add_member")
# def add_club_member(club_id: int, user_id: int):
#     try:
#         add_member_to_club(club_id, user_id)
#         return {"message": f"User with ID {user_id} added to club with ID {club_id}."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error adding member to club: {str(e)}")

# # Remove a member from a club
# @app.delete("/club/{club_id}/remove_member")
# def remove_club_member(club_id: int, user_id: int):
#     try:
#         remove_member_from_club(club_id, user_id)
#         return {"message": f"User with ID {user_id} removed from club with ID {club_id}."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error removing member from club: {str(e)}")

# # Get all clubs that a user is in
# @app.get("/clubs/{username}")
# def get_user_clubs(username: str):
#     try:
#         clubs = get_user_clubs(username)
#         return {"clubs": clubs}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching user clubs: {str(e)}")

# # Get all members of a club
# @app.get("/club/{club_id}/members")
# def get_club_members(club_id: int):
#     try:
#         members = get_club_members_by_id(club_id)
#         return {"members": members}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching club members: {str(e)}")

# # Add a new event to associated club
# @app.post("/club/{club_id}/event/new")
# def create_club_event(club_id: int, event: newEvent):
#     try:
#         create_new_event(club_id, event)
#         return {"message": f"New event created for club ID {club_id}."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error creating new event: {str(e)}")

# # Update an event for a club (edit/adding a video link to a club event)
# @app.put("/club/{club_id}/event/{event_id}")
# def update_event_video_link(club_id: int, event_id: int, video_link: str):
#     return crud.update_event_video_link(club_id, event_id, video_link)

# # Delete an event from a club
# @app.delete("/club/{club_id}/event/{event_id}")
# def delete_event(club_id: int, event_id: int):
#     return crud.delete_event(club_id, event_id)

# # Get all events of a club
# @app.get("/club/{club_id}/events")
# def get_club_events(club_id: int):
#     try:
#         events = get_events_by_club(club_id)
#         return {"events": events}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching club events: {str(e)}")

# # User interest in an event
# @app.post("/event/{event_id}/interest")
# def add_event_interest(event_id: int, user_id: int):
#     try:
#         add_interest_in_event(event_id, user_id)
#         return {"message": f"User with ID {user_id} is now interested in event with ID {event_id}."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error adding event interest: {str(e)}")
    
# # Get all events a user is interested in going to
# @app.get("/user/{username}/interested_events")
# def get_user_interested_events(username: str):
#     return crud.get_user_interested_events(username)

# # Get all users interested in an event
# @app.get("/event/{event_id}/interested")
# def get_users_interested_in_event(event_id: int):
#     try:
#         interested_users = get_interested_users_in_event(event_id)
#         return {"interested_users": interested_users}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching event interest data: {str(e)}")

# # Delete event interest
# @app.delete("/user/{username}/event/{event_id}/interest")
# def delete_event_interest(username: str, event_id: int):
#     return crud.delete_event_interest(username, event_id)

@app.get("/")
def hello_world():
    """
    Returns a simple Hello World message
    """
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
