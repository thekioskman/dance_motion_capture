import os
from db_connect import connect
from compare_videos import compare_videos
from models import User, userLoginData, userRegisterData
import bcrypt
import jwt


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Table name MACROS
USERS_TABLE = "users"
USER_FOLLOWINGS_TABLE = "user_following"
USER_POSTS_TABLE = "user_posts"
CLUBS_TABLE = "clubs"
EVENTS_TABLE = "events"
CLUB_POSTS_TABLE = "club_posts"
CLUB_POST_COMMENTS_TABLE = "club_post_comments"
EVENTS_INTEREST_TABLE = "event_interest"
MEMBERSHIPS_TABLE = "membership"

# Function to clear all tables -> used for testing
def clear_all_tables():
    """
    Deletes all records from all tables in the database.
    """
    try:
        with connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {USERS_TABLE} CASCADE;")  # Clears user data -> cascades to all other tables
                
                # Reset the sequence for the id column of the users table back to 1
                cursor.execute(f"ALTER SEQUENCE {USERS_TABLE}_id_seq RESTART WITH 1;")
                
                conn.commit()
    except Exception as e:
        raise RuntimeError(f"Failed to clear tables: {str(e)}")
    
# **User Operations**

# Function to register a new user
def register_user(request_body: userRegisterData):

    username = request_body.username
    password = request_body.password
    first_name = request_body.first_name
    last_name = request_body.last_name

    with connect() as conn:
        with conn.cursor() as cursor:
            # Check if user already exists
            cursor.execute(f"SELECT COUNT(*) FROM {USERS_TABLE} WHERE username = %s", (username,))
            user_exists = cursor.fetchone()[0] > 0
            
            if user_exists:
                raise ValueError(f"Username '{username}' already exists.")
            
            # Hash the password before storing it in the database
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert the new user into the users table
            cursor.execute(
                f"INSERT INTO {USERS_TABLE} (username, password, first_name, last_name, total_dance_time, sessions_attended, followers, following) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (username, hashed_password, first_name, last_name, 0, 0, 0, 0)
            )
            conn.commit()

# Function to authenticate a user during login
def authenticate_user(request_body: userLoginData):
    
    username = request_body.username
    password = request_body.password
    
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id, password, first_name, last_name FROM {USERS_TABLE} WHERE username = %s", (username,))
            user_data = cursor.fetchone()

            if not user_data:
                raise ValueError("Incorrect username or password.")
            
            user_id, db_password, first_name, last_name = user_data
            
            # Compare the hashed password with the one stored in the database
            if bcrypt.checkpw(password.encode('utf-8'), bytes(db_password)):
                return {"success": True, "user_id": user_id, "first_name" : first_name, "last_name" : last_name}
            else:
                raise ValueError("Incorrect username or password.")
            
# Function to get a user by user_id
def get_user_by_id(user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(f"SELECT username, first_name, last_name, total_dance_time, sessions_attended, followers, following FROM {USERS_TABLE} WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                raise ValueError("User not found")
            
            # Return the user data in the correct format
            return User(
                username=user_data[0],
                first_name=user_data[1],
                last_name=user_data[2],
                total_dance_time=user_data[3],
                sessions_attended=user_data[4],
                followers=user_data[5],
                following=user_data[6],
            )
        
# **Video Comparison Operations**
            
# Function to compare two videos
def compare_uploaded_videos(video1_path: str, video2_path: str):
    try:
        result = compare_videos(video1_path, video2_path)
        return result
    except Exception as e:
        raise Exception(f"Error processing videos: {str(e)}")
    


# **Following Operations**

# Function to add a follower following relationship
def add_follower_following(follower_id: int, following_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (follower_id,))
            user_id = cursor.fetchone()
            if not user_id:
                raise Exception(f"Follower user with id {follower_id} not found.")
            
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (following_id,))
            following_id = cursor.fetchone()
            if not following_id:
                raise Exception(f"Following account with id {following_id} not found.")

            # Insert the relationship
            cursor.execute(f"INSERT INTO {USER_FOLLOWINGS_TABLE} (user_id, following_id) VALUES (%s, %s) ON CONFLICT (user_id, following_id) DO NOTHING", (follower_id, following_id))
            
            # Only increment if follow relationship didn't already exist
            if cursor.rowcount > 0:
                # Increment the followers count of the followed user
                cursor.execute(f"""
                    UPDATE {USERS_TABLE}
                    SET followers = followers + 1
                    WHERE id = %s
                """, (following_id,))

                # Increment the following count of the user following other user
                cursor.execute(f"""
                    UPDATE {USERS_TABLE}
                    SET following = following + 1
                    WHERE id = %s
                """, (follower_id,))

            conn.commit()

# Function to remove a follower following relationship
def remove_follower_following(follower_id: int, following_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (follower_id,))
            user_id = cursor.fetchone()
            if not user_id:
                raise Exception(f"Follower user with id {follower_id} not found.")
            
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (following_id,))
            following_id = cursor.fetchone()
            if not following_id:
                raise Exception(f"Following account with id {following_id} not found.")

            # Insert the relationship
            cursor.execute(f"DELETE FROM {USER_FOLLOWINGS_TABLE} f WHERE f.user_id = %s AND following_id = %s", (follower_id, following_id))
            
            # Only decrement if follow relationship existed
            if cursor.rowcount > 0:
                # Decrement the followers count of the unfollowed user
                cursor.execute(f"""
                    UPDATE {USERS_TABLE}
                    SET followers = followers - 1
                    WHERE id = %s
                """, (following_id,))

                # Decrement the following count of the user unfollowing other user
                cursor.execute(f"""
                    UPDATE {USERS_TABLE}
                    SET following = following - 1
                    WHERE id = %s
                """, (follower_id,))

            conn.commit()

# Function to get all accounts that a user follows
def get_user_followings(user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (user_id,))
            user_id = cursor.fetchone()
            if not user_id:
                raise Exception(f"User: {user_id} not found.")
            
            # Fetch all users that this user follows
            cursor.execute(f"""
                SELECT u.id, u.username, u.first_name, u.last_name
                FROM {USERS_TABLE} u 
                JOIN {USER_FOLLOWINGS_TABLE} f ON f.following_id = u.id 
                WHERE f.user_id = %s
            """, (user_id,))
            followings = cursor.fetchall()

            # Convert query result into a list of dictionaries
            followings_list = [
                {
                    "id": user[0],
                    "username": user[1],
                    "first_name": user[2],
                    "last_name": user[3]
                }
                for user in followings
            ]
            
            return followings_list
        
# Function to get all followers of a user
def get_user_followers(user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (user_id,))
            user_id = cursor.fetchone()
            if not user_id:
                raise Exception(f"User: {user_id} not found.")
            
            # Fetch all usernames that follows this user
            cursor.execute(f"""
                SELECT u.id, u.username, u.first_name, u.last_name
                FROM {USER_FOLLOWINGS_TABLE} f 
                JOIN {USERS_TABLE} u ON f.user_id = u.id 
                WHERE f.following_id = %s
            """, (user_id,))
            followers = cursor.fetchall()

            followers_list = [
                {
                    "id": user[0],
                    "username": user[1],
                    "first_name": user[2],
                    "last_name": user[3]
                }
                for user in followers
            ]
            
            return followers_list

def search_users_db(query: str):
    """
    Searches for users by username (partial match).
    Returns a list of matching users.
    """
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT id, username, first_name, last_name FROM {USERS_TABLE} WHERE username ILIKE %s",
                (f"%{query}%",)
            )
            users = cursor.fetchall()

            if not users:
                return []
            
            user_col_names = [desc[0] for desc in cursor.description]
            return [dict(zip(user_col_names, row)) for row in users]

# Function to get all members of a club
def get_club_members_by_id(club_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT u.id, u.username, u.first_name, u.last_name
                FROM {USERS_TABLE} u
                JOIN {MEMBERSHIPS_TABLE} mt ON mt.user_id = u.id
                WHERE club_id = %s
            """, (club_id,))
            members = cursor.fetchall()

            members_list = [
                {
                    "id": user[0],
                    "username": user[1],
                    "first_name": user[2],
                    "last_name": user[3]
                }
                for user in members
            ]

            return members_list

        
