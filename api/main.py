from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from compare_videos import compare_videos
from models import userLoginData
from db_connect import connect, close_connection
import bcrypt
import jwt

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # if security needed, change this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

        # Compare videos
        result = compare_videos(video1_path, video2_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing videos: {str(e)}")
    finally:
        # Delete uploaded files
        if os.path.exists(video1_path):
            os.remove(video1_path)
        if os.path.exists(video2_path):
            os.remove(video2_path)

    return JSONResponse(content=result)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/login")
def login(request_body: userLoginData):
    '''
    returns true if the username and password exists in the DB 
    '''
    user_name = request_body.user_name
    password = request_body.password
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s and password = %s", (user_name,password))
            user_exists = cursor.fetchone()[0] > 0
            
            if not user_exists:
                return {"success" : False, "message" : "incorrect username or password"}
           
    return {"success": True}


@app.post("/register")
def register(request_body: userLoginData):
    '''
    creates a entry for username and password in the DB
    '''
    user_name = request_body.user_name
    password = request_body.password
    
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user_name,))
            user_exists = cursor.fetchone()[0] > 0
            
            if user_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Username '{user_name}' already exists."
                )
            else:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (user_name, password)
                )
                conn.commit()

    return {"message": "User registered successfully.", "success" : True}

