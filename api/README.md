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
            "followers": 0
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
        "following": [
            1,
            2
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
        "message": "johndoe successfully unfollowed brian"
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