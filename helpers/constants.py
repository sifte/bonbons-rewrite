from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = environ["TOKEN"]
    HOST = environ["DEFINE_API_URI"]
    MONGO = environ["MONGO_URI"]
    KEY = environ["API_KEY"]


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
