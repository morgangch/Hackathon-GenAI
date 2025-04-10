import chainlit as cl
import sqliteManager
from enum import Enum
from typing import Optional
import os
import dotenv
from chainlit.input_widget import Select, Switch, Slider, TextInput

dotenv.load_dotenv()

SQLiteManager = sqliteManager.SQLiteManager("characters.db")
SQLiteManager.reinitialize_database()

CHAINLIT_AUTH_SECRET = os.getenv("CHAINLIT_AUTH_SECRET")

notion = "la relativité restreinte"

class ComprehensionLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


comprehension_dict = {
        "low": ComprehensionLevel.LOW,
        "medium": ComprehensionLevel.MEDIUM,
        "high": ComprehensionLevel.HIGH
    }

class Character:
    def __init__(self, name):
        self.name = name
        desc = SQLiteManager.fetch_one("SELECT description FROM characters WHERE name = ?", (name,))
        self.description = desc["description"] if desc else "Pas de description disponible."
        self.comprehension = ComprehensionLevel.LOW
        
    def set_comprehension(self, comprehension):
        if comprehension not in comprehension_dict.keys():
            return
        self.comprehension = comprehension_dict[comprehension]
        
    def interpret_comprehension(self):
        if self.comprehension == ComprehensionLevel.LOW:
            return "Je ne comprends pas très bien."
        elif self.comprehension == ComprehensionLevel.MEDIUM:
            return "Je comprends un peu."
        elif self.comprehension == ComprehensionLevel.HIGH:
            return "Je comprends parfaitement."
        return "Je ne sais pas comment interpréter cela."

    async def respond(self, message):
        await cl.Message(
            content=f"{self.name}: {message}.\n{self.interpret_comprehension()}", author=self.name.lower()
        ).send()
        
characters = [Character("Kadoc"), Character("Karadoc"), Character("Perceval")]

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
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"starting chat using the {chat_profile} chat profile"
    ).send()
    settings = await cl.ChatSettings(
        [
            TextInput(
                id="notion",
                label="La notion à travailler",
                placeholder=f"Entrez la notion ici, ex: {notion}",
                initial="",
                max_length=100,
                required=True,
            ),
            Slider(
                id="profile_number",
                label="nombre of profile (comming soon)",
                initial=3,
                min=1,
                max=10,
                step=1,
            ),
        ]
    ).send()

@cl.on_settings_update
async def setup_agent(settings):
    global notion
    notion = settings["notion"]

@cl.on_message
async def handle_message(message):
    if message:
        await generate_responses(message)
    else:
        await cl.Message("Please enter a valid message.").send()

async def generate_responses(message):
    for character in characters:
        await character.respond(f"{character.name} is thinking about {notion}...")
        await cl.sleep(1)  # Simulate thinking time

@cl.on_chat_resume
async def resume_chat():
    for character in characters:
        await cl.Message(f"{character.name} has resumed the chat.").send()
        await cl.Message(f"{character.name}'s comprehension level is {character.comprehension.name}.").send()
