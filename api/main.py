from fastapi import FastAPI, File, UploadFile, HTTPException, UploadFile, Form, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
from db_connect import connect
from crud import *
from models import *
import os
from posts_event_crud import *
from clubs_crud import *

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

AWS_ACCESS_KEY = "AKIAQXUIXLGG3CCMRFMY"
AWS_SECRET_KEY = "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"
S3_BUCKET_NAME = "fydp25stravadance"

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='us-east-2'
)

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

#Fetch POsts
# TODO: this needs to be changed to GET! But the params into query parameters
@app.post("/posts")
#clubs fetch
def get_posts(request_body: postsUserRequest):
    try:
        response = fetch_posts(request_body)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#create posts
@app.post("/userpost/create")
async def upload_post(files: list[UploadFile] = File(...),
    title: str = Form(...),
    description: str = Form(...),
    owner: str = Form(...),
    createdOn : str = Form(...)):
    try:
        file_names = []
        for file in files:
            file_names.append(file.filename)

        #add post to the DB with filenames, we can extract the URL back from the filenames
        #in case we change s3 buckets
        pic_urls = ",".join(file_names) #up to 9 images in 1 section
        post_id = create_user_post_db(title, int(owner), description, createdOn, pic_urls)

        for file in files:
            # Upload each file to S3
            s3_client.upload_fileobj(
                file.file,
                S3_BUCKET_NAME,
                f"user_post/{post_id}-{file.filename}",
                ExtraArgs={"ContentType": file.content_type}
            )
        
        return {"message": "Post uploaded successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/clubpost/create")
def create_club_post(request_body: ClubPost):
    try:
        create_club_post_db(request_body)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/clubevent/create")
def create_club_event(request_body: ClubEvent):
    try:
        create_club_event_db(request_body)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# User Login
@app.post("/login")
def login(request_body: userLoginData):
    '''
    Authenticate user login
    '''
    try:
        result = authenticate_user(request_body)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Register a user
@app.post("/register")
def register(request_body: userRegisterData):
    '''
    Register a new user in the system
    '''
    try:
        register_user(request_body)
        return {"message": "User registered successfully.", "success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get all events applicable to a user based off the clubs they follow
# TODO: change this to a get later...
@app.post("/user/events")
def get_user_club_events(request_body: postsUserRequest):
    # TODO: somehow get rid of the user_id here...?
    try:
        events = get_events_by_user_id(request_body)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching club events: {str(e)}")

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
        return {"followings": followings}
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

# Get all events by a club
@app.post("/club/events")
def get_club_events(request_body: postsClubRequest):
    try:
        events = get_events_by_club_id(request_body)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching club events: {str(e)}") 

# Get club details by id
@app.get("/club/{club_id}")
def get_club_details(club_id: int):
    try:
        club_details = get_club_by_id(club_id)
        return club_details
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching club details: {str(e)}")

# Delete a club
@app.delete("/club/{club_id}")
def delete_club(club_id: int):
    try:
        delete_club_by_id(club_id)
        return {"message": f"Club with ID {club_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting club: {str(e)}")


# Add a member to a club
@app.post("/club/{club_id}/members")
def add_club_member(club_id: int, user_id: int = Body(..., embed=True)):
    try:
        add_member_to_club(club_id, user_id)
        return {"message": f"User with ID {user_id} added to club with ID {club_id}."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding member to club: {str(e)}")

# Remove a member from a club
@app.delete("/club/{club_id}/members/{user_id}")
def remove_club_member(club_id: int, user_id: int):
    try:
        remove_member_from_club(club_id, user_id)
        return {"message": f"User with ID {user_id} removed from club with ID {club_id}."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error removing member from club: {str(e)}")

# Get all clubs that a user is in
@app.get("/user/{user_id}/clubs")
def get_user_clubs(user_id: int):
    try:
        clubs = get_user_clubs_by_id(user_id)
        return {"clubs": clubs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching user clubs: {str(e)}")

@app.get("/search/clubs")
def search_clubs(query: str):
    """
    API endpoint to search for clubs.
    """
    clubs = search_clubs_db(query)

    if not clubs:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "No clubs found", "data": []}
        )

    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Clubs found", "data": clubs}
    )


@app.get("/search/users")
def search_users(query: str):
    """
    API endpoint to search for users.
    """
    users = search_users_db(query)

    if not users:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "No users found", "data": []}
        )

    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Users found", "data": users}
    )

# Get all members of a club
@app.get("/club/{club_id}/members")
def get_club_members(club_id: int):
    try:
        members = get_club_members_by_id(club_id)
        return {"members": members}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching club members: {str(e)}")

# Create an event for a club
@app.post("/events/create")
def create_club_event(request_body: ClubEvent):
    try:
        event_id = create_club_event_db(request_body)
        return {"event_id": event_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# User interest in an event
@app.post("/events/interest")
def add_event_interest(request_body: EventInterest):
    try:
        add_interest_in_event(request_body)
        return {"message": f"User with ID {request_body.user_id} is now interested in event with ID {request_body.event_id}."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding event interest: {str(e)}")
    
# Delete event interest
@app.delete("/events/interest")
def delete_event_interest(request_body: EventInterest):
    try:
        remove_interest_in_event(request_body)
        return {"message": f"User with ID {request_body.user_id} is no longer interested in event with ID {request_body.event_id}."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error removing event interest: {str(e)}")
    

# Update an event for a club (edit/adding a video link to a club event)
@app.patch("/events/{event_id}")
def update_event_video_link(event_id: int, video_url: str = Body(..., embed=True)):
    try:
        updated_event = add_video_to_event(event_id, video_url)
        return {"event_id": updated_event["event_id"], "video_url": updated_event["video_url"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating event: {str(e)}")

# Delete an event from a club based on event id
@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    try:
        result = delete_event_by_id(event_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting event: {str(e)}")
    
    if result["success"]:
            return {"message": result["message"]}
    else:
        raise HTTPException(status_code=404, detail=result["message"])
    
# Get all events a user is interested in going to
@app.get("/user/{user_id}/interested")
def get_user_interested_events(user_id: int):
    try:
        events = get_interested_events_by_user_id(user_id)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching club events: {str(e)}") 

# Get all users interested in an event
@app.get("/events/{event_id}/interested")
def get_user_interested_events(event_id: int):
    try:
        users = get_interested_users_by_event_id(event_id)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching users interested in event: {str(e)}") 


@app.get("/")
def hello_world():
    """
    Returns a simple Hello World message
    """
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
