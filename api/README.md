# API Documentation
The following is documentation for how to call / use the api endpoints

For now, our db is running only locally. So, the baseurl for all API requests should be: "http://localhost:8000" 

## Table of Contents

- [Structure](#structure)
- [Endpoints](#endpoints)
- [Error Codes](#error-codes)

## Structure
API code is split in the following manner:
- `main.py`: Defines API endpoints
    - Entry point of the application and contains the application logic to start the web server, route API requests, and handle user interactions. It is where you define the endpoints of the API and handle incoming requests, usually by calling functions from other modules (`crud.py`)
- `models.py`: Contains all body data structs for requests
    - It is responsible for representing the entities in the database as Python classes, which make it easier to interact with the database and perform operations like creating, reading, updating, and deleting data.
- `crud.py`: Where direct interaction with db occurs
    - Functions that define the "Create", "Read", "Update", and "Delete" operations (CRUD operations) for interacting with the database. It abstracts the database logic and provides a clean interface for manipulating data in the database.
- `db_connect.py` : Handle database connection setup and management

## Endpoints
### **Reset**
- **URL**: `/reset`
- **Method**: `POST`
- **Description**: Clear all tables: used mostly for debugging

- **Response**:
    - **200 OK**

### **Video Compare**
- **URL**: `/compare`
- **Method**: `POST`
- **Description**: Compares two uploaded videos and returns a similarity score and analysis.
- **Request Body**:
    ```json
    {
        "video1": <video file>,
        "video2": <video file>
    }
    ```
    - ##### Request Parameters:
        - **`video1`**: The first video file to be compared. (required)
            - Type: `File`
            - Format: Video file (e.g., .mp4, .mov, .avi)
        
        - **`video2`**: The second video file to be compared. (required)
            - Type: `File`
            - Format: Video file (e.g., .mp4, .mov, .avi)
- **Response**:
    - **200 OK**:
    ```json
    {
        "result": {
            "similarity_score": 87.5,
            "comments": [
            "Videos are very similar in terms of timing and movement.",
            "Minor differences in arm positioning."
            ]
        }
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Create User**
- **URL**: `/register`
- **Method**: `POST`
- **Description**: Creates a new user.
- **Request Body**:
    ```json
    {
        "username": "johndoe",
        "password": "123",
        "first_name": "john",
        "last_name": "doe"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "User registered successfully.", 
        "success": True
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Authenticate/Login User**
- **URL**: `/login`
- **Method**: `POST`
- **Description**: User Login
- **Request Body**:
    ```json
    {
        "username": "johndoe",
        "password": "123",
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "success": true,
        "user_id": 1
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get User Details**
- **URL**: `/user/{user_id}`
- **Method**: `GET`
- **Description**: Get user details by user id
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "User found successfully.",
        "success": true,
        "user": {
            "username": "jilly",
            "first_name": "jilly",
            "last_name": "song",
            "total_dance_time": 0,
            "sessions_attended": 0,
            "followers": 0,
            "following": 0
        }
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Follow New User**
- **URL**: `/follow`
- **Method**: `POST`
- **Description**: Have one user follow another user; Pass in their usernames
- **Request Body**:
    ```json
    {
        "follower_id": "1",
        "following_id": "2",
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "johndoe successfully followed brian"
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Unfollow a User**
- **URL**: `/unfollow`
- **Method**: `DELETE`
- **Description**: Have one user unfollow another user; Pass in their usernames
- **Request Body**:
    ```json
    {
        "follower_id": "1",
        "following_id": "2",
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "johndoe successfully unfollowed brian"
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get Followings of User**
- **URL**: `/followings/{user_id}`
- **Method**: `GET`
- **Description**: Get all the accounts that the passed in user follows
- **Response**:
    - **200 OK**:
    ```json
    {
        "followings": [
            {
                "id": 2,
                "username": "brian",
                "first_name": "brian",
                "last_name": "qiu"
            },
            {
                "id": 1,
                "username": "jilly",
                "first_name": "jilly",
                "last_name": "song"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get Followers of User**
- **URL**: `/followers/{user_id}`
- **Method**: `GET`
- **Description**: Get all the accounts that follows the passed in user
- **Response**:
    - **200 OK**:
    ```json
    {
        "followers": [
            {
                "id": 3,
                "username": "tk",
                "first_name": "tk",
                "last_name": "tk"
            },
            {
                "id": 1,
                "username": "jilly",
                "first_name": "jilly",
                "last_name": "song"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Create New Club**
- **URL**: `/club/new`
- **Method**: `POST`
- **Description**: Add a new club
- **Request Body**:
    ```json
    {
        "owner": 1,
        "name": "UW Hip Hop",
        "description": "Hip hop dancing woo",
        "club_tag": "UWHH"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "New Club 'UW Hip Hop' was created successfully",
        "club_id": 2
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get Club Details**
- **URL**: `/club/{club_id}`
- **Method**: `GET`
- **Description**: Get details of a club by club id (returned when a new club is created)
- **Response**:
    - **200 OK**:
    ```json
    {
        "id": 2,
        "owner": 1,
        "name": "UW Hip Hop",
        "description": "Hip hop dancing woo",
        "club_tag": "UWHH"
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Delete Club**
- **URL**: `/club/{club_id}`
- **Method**: `DELETE`
- **Description**: Delete a club based on club id
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "Club with ID 2 deleted successfully."
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Add Member to Club**
- **URL**: `/club/{club_id}/members`
- **Method**: `POST`
- **Description**: Add a new club
- **Request Body**:
    ```json
    {
        "user_id": 1,
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "User with ID 1 added to club with ID 1."
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Delete Member from a Club**
- **URL**: `/club/{club_id}/members/{user_id}`
- **Method**: `DELETE`
- **Description**: Remove a member from a club
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "User with ID 1 removed from club with ID 1."
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get User Clubs**
- **URL**: `/user/{user_id}/clubs`
- **Method**: `GET`
- **Description**: Get all club_ids for clubs that a user is in
- **Response**:
    - **200 OK**:
    ```json
    {
        "clubs": [
            {
                "id": 1,
                "name": "UW Hip Hop",
                "description": "Hip hop dancing woo",
                "club_tag": "UWHH",
                "owner_id": 1
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get Members of Club**
- **URL**: `/club/{club_id}/members`
- **Method**: `GET`
- **Description**: Get all user_ids for a club (all member of a club)
- **Response**:
    - **200 OK**:
    ```json
    {
        "members": [
            {
                "id": 2,
                "username": "brian",
                "first_name": "brian",
                "last_name": "qiu"
            },
            {
                "id": 1,
                "username": "jilly",
                "first_name": "jilly",
                "last_name": "song"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Add a Club Event**
- **URL**: `/events/create`
- **Method**: `POST`
- **Description**: Add a new event for a club
- **Request Body**:
    ```json
    {
        "club_id": 1,
        "title": "Jilly Choreographer Session",
        "description": "description",    
        "date": "2025-03-10",
        "time": "18:00:00+00:00",
        "duration_minutes": 90,
        "location": "E7",
        "created_on": "2025-02-18T12:00:00Z"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "event_id": 7
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Add Video to a Club Event**
- **URL**: `/events/{event_id}`
- **Method**: `PATCH`
- **Description**: Add a video to an event
- **Request Body**:
    ```json
    {
        "video_url": "https://www.youtube.com/watch?v=RCtCxGQiV8Q&list=RDRCtCxGQiV8Q&start_radio=1"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "event_id": 2,
        "video_url": "https://www.youtube.com/watch?v=RCtCxGQiV8Q&list=RDRCtCxGQiV8Q&start_radio=1"
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Delete Club Event**
- **URL**: `/events/{event_id}`
- **Method**: `DELETE`
- **Description**: Delete a club event by event id
- **Response**:
    - **200 OK**:
    ```json
    {
        "message": "Event deleted successfully."
    }
    ```
    - **404 Event Not Found**: Event with event_id not found
    ```json
    {
        "detail": "No event found with the given ID."
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get All User Events**
- **URL**: `/user/events`
- **Method**: `GET`
- **Description**: Get all events for a user based on all the clubs they are a member of
- **Request Body**:
    ```json
    {
        "user_id": 1,
        "timestamp": "2025-02-18T12:00:00Z"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
        {
        "events": [
            {
                "id": 1,
                "title": "Jilly Choreographer Session",
                "club": 1,
                "description": "description",
                "date": "2025-03-10",
                "time": "18:00:00+00:00",
                "duration_minutes": 90,
                "location": "E7",
                "picture_url": null,
                "video_url": null,
                "created_on": "2025-02-18T12:00:00+00:00"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get All Club Events**
- **URL**: `/club/events`
- **Method**: `POST`
- **Description**: Get all events for a given club
- **Request Body**:
    ```json
    {
        "club_id": 1,
        "timestamp": "2025-02-18T12:00:00Z"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "events": [
            {
                "id": 1,
                "title": "Jilly Choreographer Session",
                "club": 1,
                "description": "description",
                "date": "2025-03-10",
                "time": "18:00:00+00:00",
                "duration_minutes": 90,
                "location": "E7",
                "picture_url": null,
                "video_url": null,
                "created_on": "2025-02-18T12:00:00+00:00"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get All User Interested Events**
- **URL**: `/user/{user_id}/interested`
- **Method**: `GET`
- **Description**: Get all events that a user has indicated interest in
- **Response**:
    - **200 OK**:
    ```json
    {
        "events": [
            {
                "id": 1,
                "title": "Jilly Choreographer Session",
                "club": 1,
                "description": "description",
                "date": "2025-03-10",
                "time": "18:00:00+00:00",
                "duration_minutes": 90,
                "location": "E7",
                "picture_url": null,
                "video_url": null,
                "created_on": "2025-02-18T12:00:00+00:00"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

### **Get All Users Interested in Event**
- **URL**: `/user/{user_id}/interested`
- **Method**: `GET`
- **Description**: Get all users that are interested in a particular event
- **Response**:
    - **200 OK**:
    ```json
    {
        "users": [
            {
                "user_id": 1,
                "username": "jilly"
            }
        ]
    }
    ```
    - **400 Bad Request**: Invalid input.

## Error Codes
Here is a list of possible error codes and their meanings:

- **200 OK**: Request was successful.
- **201 Created**: Resource was successfully created.
- **400 Bad Request**: The request was invalid or malformed.
- **401 Unauthorized**: Authentication is required or failed.
- **403 Forbidden**: You do not have permission to access this resource.
- **404 Not Found**: The requested resource could not be found.
- **500 Internal Server Error**: An unexpected error occurred on the server.