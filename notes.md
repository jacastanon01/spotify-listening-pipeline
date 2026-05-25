# Spotify Listening History Pipeline

## Process

Spotify listening data was requested from spotify and downloaded onto my machine locally after spotify processed the request after a couple days. Each year of podcast and song listening data lives in its own json file, with a structure that includes a timestamp, what song/episode, how long it was played, etc...

Originally I wanted to include podcast and track data, but decided to simplify it when I was designing the schema. 

### Schema

To avoid over-eningeering, I wanted to use this project to refresh my memory on relational databases using sqlite, cleaning and processing data using python as well as best practices when it came to designing and handling data when building an ETL pipeline.

![Spotify schema](spotify_schema.png)
> The `streams` table contains a foreign key to the `track_uri` creating a many-to-one relationship. There can only be one event in time, but I can listen to the same track over and over. For this reason, `track_uri` is a row in both tables while the `tracks` exist as its own piece of information within the database.

The database consists of two tables: one for what track was listened to and one for the event. Two years ago when I orginally wanted to do this project, I inflicted paralysis by analysis on myself designing the schema and how the data should interact with each other. I knew I wanted to eventually use the spotify API to add songs to the database so the design was paramount in my mind. After some time (and help from Claude AI), I opted for a simplier approach tracking only the what and when. The `tracks` table consists of relevant information related to the song and the `streams` table includes when it was listened to, for how long, was it skipped and why.

Thinking of how data speaks and the ways that language can be used in the future is a very engaging process to me. Using LLM's has been a great resource to explain concepts I thought I knew in more practical terms. I did not want to copy paste the logic of an AI, but I wanted to use its vast resource engine and intelligence to guide me as I built this project.
