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

def get_user_clubs_db(user_id):
    '''
    Gets a list of clubs that the user is in
    '''
    with connect() as conn:
        with conn.cursor() as cursor:
            #fetch posts from all people they are following
            cursor.execute(
                   f"""
                    SELECT club_id FROM {MEMBERSHIPS_TABLE} WHERE user_id = %s
                    """,
                    (user_id)
            )
            clubs = cursor.fetchall()
            print(clubs)
            return [club[0] for club in clubs]
            
            

                