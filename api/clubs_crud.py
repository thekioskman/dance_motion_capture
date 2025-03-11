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

# Function to get all clubs that a user is a member of
def get_user_clubs_by_id(user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE id = %s", (user_id,))
            if cursor.fetchone() is None:
                raise ValueError("User does not exist")
            
            # Fetch all club details instead of just club IDs
            cursor.execute(f"""
                SELECT c.id, c.name, c.description, c.club_tag, c.owner
                FROM {MEMBERSHIPS_TABLE} m
                JOIN {CLUBS_TABLE} c ON m.club_id = c.id
                WHERE m.user_id = %s
            """, (user_id,))

            clubs = cursor.fetchall()

            # Convert query result into a list of dictionaries
            club_list = [
                {
                    "id": club[0],
                    "name": club[1],
                    "description": club[2],
                    "club_tag": club[3],
                    "owner_id": club[4]
                }
                for club in clubs
            ]
            
            return club_list
            

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

# Function to delete club by ID
def delete_club_by_id(club_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {CLUBS_TABLE} WHERE id = %s", (club_id,))
            conn.commit()

# # Function to add a member to a club
def add_member_to_club(club_id: int, user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {MEMBERSHIPS_TABLE} (user_id, club_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, club_id) DO NOTHING
                """,
                (user_id, club_id)
            )
            conn.commit()

# # Function to remove a member from a club
def remove_member_from_club(club_id: int, user_id: int):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {MEMBERSHIPS_TABLE} WHERE club_id = %s AND user_id = %s", (club_id, user_id))
            conn.commit()

def search_clubs_db(query: str):
    """
    Searches for clubs by name or club_tag (partial match).
    Returns a list of matching clubs.
    """
    with connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM clubs WHERE name ILIKE %s OR club_tag ILIKE %s"
            cursor.execute(sql, (f"%{query}%", f"%{query}%"))
            clubs = cursor.fetchall()

            if not clubs:
                return []

            club_col_names = [desc[0] for desc in cursor.description]
            return [dict(zip(club_col_names, row)) for row in clubs]


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

                