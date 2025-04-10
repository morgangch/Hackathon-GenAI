import chainlit as cl
import sqliteManager
from enum import Enum
from typing import Optional
import os
import dotenv

dotenv.load_dotenv()

SQLiteManager = sqliteManager.SQLiteManager("characters.db")
SQLiteManager.reinitialize_database()

CHAINLIT_AUTH_SECRET = os.getenv("CHAINLIT_AUTH_SECRET")

class enum(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Characters:
    def __init__(self, name):
        self.name = name
        self.description = SQLiteManager.fetch_one("SELECT description FROM characters WHERE name = ?", (name,))
        self.comprehension = enum.LOW
        
    def set_comprehension(self, comprehension):
        comprehension_dict = { "low": enum.LOW, "medium": enum.MEDIUM, "high": enum.HIGH }
        if comprehension not in comprehension_dict.keys():
            return
        self.comprehension = comprehension_dict[comprehension]

    async def respond(self, message):
        reponse = {"response": "Je suis un personnage fictif.", "comprehension": self.comprehension}
        
characters = [Characters("Kadoc"), Characters("Karadoc"), Characters("Perceval")]

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    elif (username, password) in [("user1", "user1"), ("user2", "user2")]:
        return cl.User(
            identifier=username, metadata={"role": "user", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_start
async def start_chat():
    app_user = cl.user_session.get("user")
    await cl.Message(f"Hello {app_user.identifier}").send()
    for character in characters:
        await profil_manager(character.name)

@cl.on_message
async def handle_message(message):
    if message:
        await generate_responses(message)
    else:
        await cl.Message("Please enter a valid message.").send()

async def generate_responses(message):
    for character in characters:
        await cl.Message(content=f"{character.name} is thinking...", author=character.name.lower()).send()
        await cl.sleep(1)  # Simulate thinking time

@cl.on_chat_resume
async def resume_chat():
    for character in characters:
        await cl.Message(f"{character.name} has resumed the chat.").send()
        await cl.Message(f"{character.name}'s comprehension level is {character.comprehension.name}.").send()

async def profil_manager(name):
    await cl.Message(content=f"{name} has joined the chat.", author=name.lower()).send()
