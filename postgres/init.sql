-- Table keeping track of all the users registered
CREATE TABLE public.users (
    "id" SERIAL PRIMARY KEY,
    "username" VARCHAR(50) UNIQUE NOT NULL,
    "password" BYTEA NOT NULL,
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50) NOT NULL,
    "total_dance_time" INTEGER NOT NULL,
    "sessions_attended" INTEGER NOT NULL,
    "followers" INTEGER NOT NULL,
    "following" INTEGER NOT NULL
);

-- Table keeping track of which other users a user follows
CREATE TABLE public.user_following(
    "id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES users (id) ON DELETE CASCADE,
    "following_id" INTEGER REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE (user_id, following_id)
);

-- Table keeping track of all posts made by USERS
CREATE TABLE public.user_posts(
    "id" SERIAL PRIMARY KEY,
    "title" VARCHAR(500),
    "owner" INTEGER REFERENCES users (id) ON DELETE CASCADE,
    "description" VARCHAR(500),
    "video_url" VARCHAR(500),
    "picture_url" VARCHAR(500),
    "created_on" TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table keeping track of all the clubs that exist
-- TODO: should club be deleted if owner is deleted?
CREATE TABLE public.clubs(
    "id" SERIAL PRIMARY KEY,
    "owner" INTEGER REFERENCES users (id),
    "name" VARCHAR(50) UNIQUE NOT NULL,
    "description" VARCHAR(500),
    "club_tag" VARCHAR(15)
);

-- Table keeping track of all events made by clubs
CREATE TABLE public.events(
    "id" SERIAL PRIMARY KEY,
    "title" VARCHAR(500),
    "club" INTEGER REFERENCES clubs (id) ON DELETE CASCADE,
    "description" VARCHAR(500),
    "date" date NOT NULL,
    "time" time with time zone,
    "duration_minutes" INTEGER,
    "location" VARCHAR(1000),
    "latitude" NUMERIC(9, 6),
    "longitude" NUMERIC(9, 6),
    "picture_url" VARCHAR(500),
    "video_url" VARCHAR(500),
    "created_on" TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table keeping track of all posts made by clubs
CREATE TABLE public.club_posts(
    "id" SERIAL PRIMARY KEY,
    "title" VARCHAR(500),
    "club" INTEGER REFERENCES clubs (id) ON DELETE CASCADE,
    "description" VARCHAR(500),
    "video_url" VARCHAR(500),
    "picture_url" VARCHAR(2000),
    "event_id" INTEGER REFERENCES events (id),
    "created_on" TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table keeping track of the comments on CLUB POSTS
CREATE TABLE public.club_post_comments(
    "id" SERIAL PRIMARY KEY,
    "owner" INTEGER REFERENCES users (id),
    "comment" VARCHAR(500),
    "post_id" INTEGER REFERENCES club_posts (id) ON DELETE CASCADE,
    "created_on" TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table keeping track of what events users are interested in going to
CREATE TABLE public.event_interest(
    "user_id" INTEGER REFERENCES users (id),
    "event_id" INTEGER REFERENCES events (id),
    PRIMARY KEY ("user_id", "event_id")
);

-- Table to show what clubs users are part of
CREATE TABLE public.membership(
    "id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES users (id) ON DELETE CASCADE,
    "club_id" INTEGER REFERENCES clubs (id) ON DELETE CASCADE,
    UNIQUE (user_id, club_id)
);

-- Track the last timestamp of posts the user viewed 
CREATE TABLE public.post_latest_timestamp(
    "user_id" INTEGER PRIMARY KEY REFERENCES users (id),
    "time" TIMESTAMP WITH TIME ZONE NOT NULL,
    "last_viewed" TIMESTAMP WITH TIME ZONE NOT NULL
);
