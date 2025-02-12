import os
from db_connect import connect
from models import User

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

def fetch_posts(user_id : int, timestamp : str):
    with connect() as conn:
        with conn.cursor() as cursor:
            #fetch posts from all people they are following
            cursor.execute(
                   f"""
                    SELECT * FROM {USER_POSTS_TABLE} 
                    WHERE owner IN (
                        SELECT following_id FROM {USER_FOLLOWINGS_TABLE} WHERE user_id = %s
                    ) 
                    AND created_on > %s 
                    ORDER BY created_at ASC;
                    """,
                    (user_id, timestamp)
            )
            user_posts = cursor.fetchall()
            user_col_names = [desc[0] for desc in cursor.description]



            cursor.execute(
                f"SELECT * FROM {USER_POSTS_TABLE} WHERE owner IN "
                f"(SELECT following_id FROM {USER_FOLLOWINGS_TABLE} WHERE user_id = %s) AND created_on > %s ORDER BY created_at ASC;",
                (user_id, timestamp)
            )
            club_posts = cursor.fetchall()
            club_col_names = [desc[0] for desc in cursor.description]


            return user_posts, club_posts, user_col_names, club_col_names





