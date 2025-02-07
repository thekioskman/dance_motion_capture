import requests

"""
This script can be used to populate the database with new users, make sure authentications works,
and also add follow relationships to user_following
"""
# The URL of your FastAPI server's register endpoint
BASE_URL = "http://localhost:8000" 


# Define users (username, password)
users = [
    {"id": "1", "username": "jilly", "password": "123", "first_name": "jilly", "last_name": "song"},
    {"id": "2", "username": "brian", "password": "123", "first_name": "brian", "last_name": "qiu"},
    {"id": "3", "username": "tk", "password": "123", "first_name": "tk", "last_name": "tk"},
]

# Function to register users
def register_users():
    # Loop through the users and send a POST request for each one
    for user in users:
        response = requests.post(f"{BASE_URL}/register", json=user)
        
        if response.status_code == 200:
            print(f"User '{user['username']}' added successfully!")
        else:
            print(f"Failed to add user '{user['username']}': {response.json()}")

def login_users():
    # Authenticate and check all registered users can log in successfully
    for user in users:
        login_data = {"username": user["username"], "password": user["password"]}
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        if response.status_code == 200 and response.json().get("success"):
            print(f"User '{user['username']}' logged in successfully!")
        else:
            print(f"Failed to log in user '{user['username']}': {response.json()}")

def follow_users():
    # Define the follow relationships in a list of tuples (follower, following)
    follow_relationships = [
        ("1", "2"),
        ("3", "1"),
        ("3", "2")
    ]
    
    # Loop through each relationship and perform the follow action
    for follower, following in follow_relationships:
        response = requests.post(f"{BASE_URL}/follow", json={"follower_id": follower, "following_id": following})
        
        if response.status_code == 200:
            print(f"{follower} followed {following} successfully.")
        else:
            print(f"Failed to follow {following} by {follower}. Status code: {response.status_code}")

def check_followings():
    for user in users:
        response = requests.get(f"{BASE_URL}/followings/{user['id']}")
        
        if response.status_code == 200:
            print(f"{user['id']} is following:", response.json())
        else:
            print(f"Failed to retrieve followings for {user}. Status code: {response.status_code}")


# Main function to run the test
def main():
    # Register users
    register_users()

    # Log in users
    login_users()
    
    # Make users follow each other
    follow_users()
    
    # Check the followings of each user
    check_followings()

if __name__ == "__main__":
    main()


