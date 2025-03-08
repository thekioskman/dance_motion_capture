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
                    SELECT * FROM {CLUBS_TABLE} WHERE id in (SELECT club_id FROM {MEMBERSHIPS_TABLE} WHERE user_id = %s)
                    """,
                    (user_id)
            )
            clubs = cursor.fetchall()
            clubs_col_names = [desc[0] for desc in cursor.description]
            clubs = [dict(zip(clubs_col_names, row)) for row in clubs]
           
            return clubs
            

# Function to create a new club
def create_new_club(owner: int, name: str, description: str, club_tag: str):
    with connect() as conn:
        with conn.cursor() as cursor:
            # Check if owner exists
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (owner,))
            if cursor.fetchone() is None:
                raise ValueError("Owner does not exist")
            
            # Check if club with same name already exists
            cursor.execute(f"SELECT id FROM {CLUBS_TABLE} WHERE name = %s", (name,))
            if cursor.fetchone():
                raise ValueError("A club with this name already exists")
            
            # Insert new club
            cursor.execute(
                f"""
                INSERT INTO {CLUBS_TABLE} (owner, name, description, club_tag)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (owner, name, description, club_tag)
            )
            club_id = cursor.fetchone()[0]
            conn.commit()
        
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"INSERT INTO {MEMBERSHIPS_TABLE} (club_id, user_id) VALUES (%s, %s)", (club_id, owner))
            conn.commit()

    
    return club_id
            

# Function to get club by ID
def get_club_by_id(club_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {CLUBS_TABLE} WHERE id = %s", (club_id,))
            club = cursor.fetchone()
            if club:
                return {
                    "id": club[0],
                    "owner": club[1],
                    "name": club[2],
                    "description": club[3],
                    "club_tag": club[4],
                }
            else:
                raise Exception("Club not found.")

# # Function to delete club by ID
def delete_club_by_id(club_id: int):

    #first delete all of this clubs entries in the membership table
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {MEMBERSHIPS_TABLE} WHERE club_id = %s", (club_id,))
            conn.commit()


    #then delete the club itself
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {CLUBS_TABLE} WHERE id = %s", (club_id,))
            conn.commit()

# # Function to add a member to a club
def add_member_to_club_db(club_id: int, user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"INSERT INTO {MEMBERSHIPS_TABLE} (club_id, user_id) VALUES (%s, %s)", (club_id, user_id))
            conn.commit()

# # Function to remove a member from a club
def remove_member_from_club(club_id: int, user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {MEMBERSHIPS_TABLE} WHERE club_id = %s AND user_id = %s", (club_id, user_id))
            conn.commit()

# # Function to get all members of a club
# def get_club_members_by_id(club_id: int):
#     with connect() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(f"""
#                 SELECT u.username
#                 FROM users u
#                 JOIN {MEMBERSHIPS_TABLE} m ON m.user_id = u.id
#                 WHERE m.club_id = %s
#             """, (club_id,))
#             members = cursor.fetchall()
#             return [member[0] for member in members]         

                