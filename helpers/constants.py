from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO="mongodb+srv://kayle:kaylebetter@cluster0.s0wqa.mongodb.net/discord?retryWrites=true&w=majority"
    KEY="c8b299ee91msha4c1921cebbedabp1f70a0jsnc4c1cc4b9c5c"
    HOST="mashape-community-urban-dictionary.p.rapidapi.com"
    TOKEN="ODg4MzA5OTE1NjIwMzcyNDkx.YUQ1Ew.W_7Ts_-tZTnQc4nMbzn8jHnht8Q"

REPLIES = [ 
    "Noooooo!!",
    "Nope.",
    "I'm sorry Dave, I'm afraid I can't do that.",
    "I don't think so.",
    "Not gonna happen.",
    "Out of the question.",
    "Huh? No.",
    "Nah.",
    "Naw.",
    "Not likely.",
    "No way, José.",
    "Not in a million years.",
    "Fat chance.",
    "Certainly not.",
    "NEGATORY.",
    "Nuh-uh.",
    "Not in my house!",
]

FAIL_REPLIES = (
    "I looked far and wide but nothing was found.",
    "I could not find anything related to your query.",
    "Could not find anything. Sorry.",
    "I didn't find anything related to your query.",
)
