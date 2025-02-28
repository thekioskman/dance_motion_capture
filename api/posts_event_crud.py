import os
from db_connect import connect
from models import ClubEvent, ClubPost, UserPost, postsUserRequest, postsClubRequest, EventInterest
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

def fetch_posts(request_body: postsUserRequest ):

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

def create_user_post_db(request_body : UserPost):
    title = request_body.title
    owner = request_body.owner
    desc = request_body.description
    vid_url = request_body.video_url
    pic_url = request_body.picture_url
    created_on = request_body.created_on
    timestamp_obj = datetime.fromisoformat(created_on.replace("Z", "+00:00"))

    with connect() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(
                f"INSERT INTO {USER_POSTS_TABLE} (title, owner, description, video_url, picture_url, created_on) VALUES (%s, %s, %s, %s, %s, %s)",
                (title, owner, desc, vid_url, pic_url, timestamp_obj)
            )
            conn.commit()

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
    club_id = request_body.club_id
    title = request_body.title
    description = request_body.description
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
                INSERT INTO {EVENTS_TABLE} (title, club, description, date, time, duration_minutes, location, picture_url, created_on)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (title, club_id, description, date, time, duration_minutes, location, picture_url, timestamp_obj ))

            event_id = cursor.fetchone()  

            if event_id is None:
                raise ValueError("Failed to retrieve event ID after insertion")  # Handle unexpected failure

            conn.commit()
            return event_id[0]


# Function to get all club events for a given user
def get_events_by_user_id(request_body: postsUserRequest):

    user_id = request_body.user_id
    timestamp = request_body.timestamp
    timestamp_obj = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    with connect() as conn:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (user_id,))
            if cursor.fetchone() is None:
                raise ValueError("User does not exist")
            
            cursor.execute(
                f"SELECT * FROM {EVENTS_TABLE} WHERE club IN "
                f"(SELECT club_id FROM {MEMBERSHIPS_TABLE} WHERE user_id = %s) AND created_on >= %s ORDER BY created_on ASC;",
                (user_id, timestamp_obj)
            )
            club_events = cursor.fetchall()
            club_col_names = [desc[0] for desc in cursor.description]
            club_events = [dict(zip(club_col_names, row)) for row in club_events]

            return club_events
        
# Function to get all club events for a given club
def get_events_by_club_id(request_body: postsClubRequest):

    club_id = request_body.club_id
    timestamp = request_body.timestamp
    timestamp_obj = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    with connect() as conn: 
        with conn.cursor() as cursor:
            # Check if club exists
            cursor.execute(f"SELECT id FROM {CLUBS_TABLE} WHERE id = %s", (club_id,))
            if cursor.fetchone() is None:
                raise ValueError("Club does not exist")
            
            cursor.execute(
                f"SELECT * FROM {EVENTS_TABLE} WHERE club = %s AND created_on >= %s ORDER BY created_on ASC;",
                (club_id, timestamp_obj)
            )
            club_events = cursor.fetchall()
            club_col_names = [desc[0] for desc in cursor.description]

    # Process the results outside the cursor's `with` block to ensure it's still accessible
    club_events = [dict(zip(club_col_names, row)) for row in club_events]

    return club_events

def delete_event_by_id(event_id: int):
    try: 
        with connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM {EVENTS_TABLE} WHERE id = %s", (event_id,))
                if cursor.rowcount > 0:  # Check if any row was deleted
                    conn.commit()
                    return {"success": True, "message": "Event deleted successfully."}
                else:
                    return {"success": False, "message": "No event found with the given ID."}
    except Exception as e:
        return {"success": False, "message": f"Error deleting event: {str(e)}"}
        
# Function to update event with video URL
def add_video_to_event(event_id: int, video_url: str):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE {EVENTS_TABLE}
                SET video_url = %s
                WHERE id = %s
                RETURNING id, video_url
                """,
                (video_url, event_id)
            )
            result = cursor.fetchone()  # Fetch the updated event details

            if result is None:
                raise ValueError(f"Event with ID {event_id} not found.")

            conn.commit()
            return {"event_id": result[0], "video_url": result[1]}

# **Event Interest Operations**
# Function to add interest in an event
def add_interest_in_event(request_body : EventInterest):

    event_id = request_body.event_id
    user_id = request_body.user_id

    with connect() as conn:
        with conn.cursor() as cursor:
            # Insert event interest
            cursor.execute(f"INSERT INTO {EVENTS_INTEREST_TABLE} (event_id, user_id) VALUES (%s, %s)", (event_id, user_id))

            # Increment sessions_attended for the user
            if cursor.rowcount > 0:
                # Get event duration
                cursor.execute(f"SELECT duration_minutes FROM {EVENTS_TABLE} WHERE id = %s", (event_id,))
                event_duration = cursor.fetchone()[0] # Fetch duration or default to 0
                
                cursor.execute(f"""
                    UPDATE {USERS_TABLE} 
                    SET sessions_attended = sessions_attended + 1,
                        total_dance_time = total_dance_time + %s
                    WHERE id = %s
                """, (event_duration, user_id))

        conn.commit()

# Function to remove interest in an event
def remove_interest_in_event(request_body : EventInterest):

    event_id = request_body.event_id
    user_id = request_body.user_id

    with connect() as conn:
        with conn.cursor() as cursor:
            # Remove event interest
            cursor.execute(f"DELETE FROM {EVENTS_INTEREST_TABLE} WHERE event_id = %s AND user_id = %s", (event_id, user_id))

            # Decrement sessions_attended for the user
            if cursor.rowcount > 0:
                # Get event duration
                cursor.execute(f"SELECT duration_minutes FROM {EVENTS_TABLE} WHERE id = %s", (event_id,))
                event_duration = cursor.fetchone()[0] # Fetch duration or default to 0
                
                cursor.execute(f"""
                    UPDATE {USERS_TABLE} 
                    SET sessions_attended = sessions_attended - 1,
                        total_dance_time = total_dance_time - %s
                    WHERE id = %s
                """, (event_duration, user_id))
        conn.commit()

# Function to get all events that a user was interested in 
def get_interested_events_by_user_id(user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (user_id,))
            if cursor.fetchone() is None:
                raise ValueError("User does not exist")
            
            cursor.execute(f"""
            SELECT e.*
            FROM {EVENTS_TABLE} AS e
            JOIN {EVENTS_INTEREST_TABLE} AS ei ON e.id = ei.event_id
            WHERE ei.user_id = %s;
            """, (user_id,))

            rows = cursor.fetchall()
            # Extract column names from the cursor description.
            column_names = [desc[0] for desc in cursor.description]

     # Map each row to a dictionary using the column names.
    events = [dict(zip(column_names, row)) for row in rows]
    return events
            
# Function to get all users interested in an event
def get_interested_events_by_user_id(event_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute(f"SELECT id FROM {EVENTS_TABLE} WHERE id = %s", (event_id,))
            if cursor.fetchone() is None:
                raise ValueError("Event does not exist")
            
            # Query the users interested in the event.
            cursor.execute(f"""
                SELECT u.id AS user_id, u.username
                FROM {USERS_TABLE} AS u
                JOIN {EVENTS_INTEREST_TABLE} AS ei ON u.id = ei.user_id
                WHERE ei.event_id = %s;
            """, (event_id,))

            rows = cursor.fetchall()
            # Extract column names from the cursor description.
            column_names = [desc[0] for desc in cursor.description]

     # Map each row to a dictionary using the column names.
    users = [dict(zip(column_names, row)) for row in rows]
    return users
