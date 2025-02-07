# Scripts Guide (for testing + debugging!)
This guide is to explain how to use the scripts for testing your changes don't break existing code + how to run
scripts to help you populate databases for debugging purposes

## Scripts
The following scripts are available to use:
- register_users.py [main! always run this first]
    - Adds new users
        - Edit users array to make changes
        - `register_users()` will register the users
        - `login_users()` will make sure all new users can be successfully authenticated
        - Edit the `follow_relationships` array within `follow_users()` to add new follow relationships (first is follower, second is following)
        - `check_followings()` will print out all users and list of all other users that they follow
- add_clubs_events.py
    - something....
- run_tests.py
    - See section on tests below

> Note: Make sure you always run register users first to add basic users to the 'users' table. When editing the scripts, ensure
that users used in other scripts reference the same users you created in the main register_users script

## Tests
The `tests` folder contains unit tests that should be run after every time you make changes to the api code. You can invoke and run all tests by simply running the `run_tests.py` script. Make sure that when you add a new test, you are naming the file in the format: test_{insert_test_name_here}.py