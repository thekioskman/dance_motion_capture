CREATE TABLE public.users (
    "id" SERIAL PRIMARY KEY,
    "username" VARCHAR(50) UNIQUE NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "total_dance_time" INTEGER NOT NULL,
    "sessions_attended" INTEGER NOT NULL,
    "followers" INTEGER NOT NULL
);

CREATE TABLE public.friends(
    "id" SERIAL PRIMARY KEY,
    "user" INTEGER REFERENCES users (id),
    "following" INTEGER REFERENCES users (id)
);

CREATE TABLE public.user_posts(
    "id" SERIAL PRIMARY KEY,
    "owner" INTEGER REFERENCES users (id),
    "description" VARCHAR(500),
    "video_url" VARCHAR(500),
    "picture_url" VARCHAR(500)
);

CREATE TABLE public.club_posts(
    "id" SERIAL PRIMARY KEY,
    "owner" INTEGER REFERENCES users (id),
    "description" VARCHAR(500),
    "video_url" VARCHAR(500),
    "picture_url" VARCHAR(500),
    "event_id" INTEGER REFERENCES events (id)
);

CREATE TABLE public.post_comments(
    "id" SERIAL PRIMARY KEY,
    "owner" INTEGER REFERENCES users (id),
    "comment" VARCHAR(500),
    "post_id" INTEGER REFERENCES posts (id)
);

CREATE TABLE public.clubs(
    "id" SERIAL PRIMARY KEY,
    "owner" VARCHAR(50) NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "description" VARCHAR(500),
    "club_tag" VARCHAR(15)
);

CREATE TABLE public.events(
    "id" SERIAL PRIMARY KEY,
    "club" INTEGER REFERENCES clubs (id) ON DELETE CASCADE,
    "name" VARCHAR(50) UNIQUE NOT NULL,
    "date" date NOT NULL,
    "time" time with time zone,
    "duration_minutes" INTEGER,
    "location" VARCHAR(50) NOT NULL,
    "picture_url" VARCHAR(500)
);

CREATE TABLE public.event_interest(
    "user_id" INTEGER REFERENCES users (id),
    "event_id" INTEGER REFERENCES events (id),
    PRIMARY KEY ("user_id", "event_id")
);

CREATE TABLE public.membership(
    "id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES users (id),
    "club_id" INTEGER REFERENCES clubs (id)
);