import os
from db_connect import connect
from models import ClubEvent, ClubPost, UserPost, postsReqest, EventInterest
from datetime import datetime

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

def fetch_posts(request_body: postsReqest ):

    user_id = request_body.user_id
    timestamp = request_body.timestamp
    timestamp_obj = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    with connect() as conn:
        with conn.cursor() as cursor:
            #fetch posts from all people they are following
            cursor.execute(
                   f"""
                    SELECT * FROM {USER_POSTS_TABLE} 
                    WHERE owner IN (
                        SELECT following_id FROM {USER_FOLLOWINGS_TABLE} WHERE user_id = %s
                    ) 
                    AND created_on >= %s 
                    ORDER BY created_on ASC;
                    """,
                    (user_id, timestamp_obj)
            )
            user_posts = cursor.fetchall()
            user_col_names = [desc[0] for desc in cursor.description]
            user_posts = [dict(zip(user_col_names, row)) for row in user_posts]
            

            cursor.execute(
                f"SELECT * FROM {CLUB_POSTS_TABLE} WHERE club IN "
                f"(SELECT club_id FROM {MEMBERSHIPS_TABLE} WHERE user_id = %s) AND created_on >= %s ORDER BY created_on ASC;",
                (user_id, timestamp_obj)
            )
            club_posts = cursor.fetchall()
            club_col_names = [desc[0] for desc in cursor.description]
            club_posts = [dict(zip(club_col_names, row)) for row in club_posts]
            
            
            if len(user_posts) != 0 and len(club_posts) != 0:
                if user_posts[-1]["created_on"] > club_posts[-1]["created_on"]:
                    return club_posts + user_posts
                else:
                    return user_posts + club_posts
            else: #order doesnt matter because on of them is empty anyway
                return user_posts + club_posts

def create_user_post_db(title, owner, desc , created_on, vid_url = None, pic_url = None ):
    timestamp_obj = datetime.fromisoformat(created_on.replace("Z", "+00:00"))

    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {USER_POSTS_TABLE} (title, owner, description, video_url, picture_url, created_on) "
                f"VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (title, owner, desc, vid_url, pic_url, timestamp_obj)
            )
            # Fetch the returned ID
            inserted_id = cursor.fetchone()[0]
            conn.commit()
    
    return inserted_id

def create_club_post_db(request_body : ClubPost):
    title = request_body.title
    club_id = request_body.club_id
    desc = request_body.description
    vid_url = request_body.video_url
    pic_url = request_body.picture_url
    event_id = request_body.event_id
    created_on = request_body.created_on
    timestamp_obj = datetime.fromisoformat(created_on.replace("Z", "+00:00"))
    with connect() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(
                f"INSERT INTO {CLUB_POSTS_TABLE} (title, club, description, video_url, picture_url, event_id, created_on) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (title, club_id, desc, vid_url, pic_url, event_id, timestamp_obj)
            )
            conn.commit()



# # **Event Operations**
# # Function to add a new event
def create_club_event_db(request_body : ClubEvent):
    club_id = request_body.club
    title = request_body.title
    name = request_body.name
    date = request_body.date
    time = request_body.time
    duration_minutes = request_body.duration_minutes
    location = request_body.location
    picture_url = request_body.picture_url
    created_on  = request_body.created_on
    timestamp_obj = datetime.fromisoformat(created_on.replace("Z", "+00:00"))

    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {EVENTS_TABLE} (title, club, name, description, date, time, duration_minutes, location, picture_url, created_on)
                VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
            """, (title, club_id, name, date, time, duration_minutes, location, picture_url, timestamp_obj ))
            conn.commit()


# Function to get all club events for a given user
def get_events_by_club(request_body: postsReqest):

    user_id = request_body.user_id
    timestamp = request_body.timestamp
    timestamp_obj = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    with connect() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                f"SELECT * FROM {EVENTS_TABLE} WHERE club IN "
                f"(SELECT club_id FROM {MEMBERSHIPS_TABLE} WHERE user_id = %s) AND created_on >= %s ORDER BY created_on ASC;",
                (user_id, timestamp_obj)
            )
            club_events = cursor.fetchall()
            club_col_names = [desc[0] for desc in cursor.description]
            club_events = [dict(zip(club_col_names, row)) for row in club_events]

            return club_events

# **Event Interest Operations**
# Function to add interest in an event
def add_interest_in_event(request_body : EventInterest):

    event_id = request_body.event_id
    user_id = request_body.user_id

    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"INSERT INTO {EVENTS_INTEREST_TABLE} (event_id, user_id) VALUES (%s, %s)", (event_id, user_id))

