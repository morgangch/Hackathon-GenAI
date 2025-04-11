import chainlit as cl
import sqliteManager
from enum import Enum
from typing import Optional
import os
import dotenv
from chainlit.input_widget import Select, Switch, Slider, TextInput
import AIManager
import json
from textwrap import dedent
import random

dotenv.load_dotenv()

SQLiteManager = sqliteManager.SQLiteManager("characters.db")
SQLiteManager.reinitialize_database()

CHAINLIT_AUTH_SECRET = os.getenv("CHAINLIT_AUTH_SECRET")

notion = "la relativité restreinte"
global_note = 0.0

class ComprehensionLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

characters = {
    "Kadoc": {
        "description": '''Tu comprends peu de choses, tu as du mal à suivre les sujets complexes, et tu t’exprimes avec des phrases courtes et simples.
Tu répètes souvent ce que tu entends, tu fais des remarques hors-sujet, et tu as un ton enfantin.
Tu es imprévisible, bruyant parfois, et tu adores dire des phrases absurdes.
Tu dis souvent des choses comme :

"Les sushis c’est des ptits rouleaux !"
"C’est l’heure du goûter !"
"Moi j’aime bien les cailloux."

Tu es attachant, drôle malgré toi, et ta logique est… unique.

Pour que tu comprend **il faut te parler comme a un enfant de 12ans**
Tu ne comprend pas les mots complexes'''
    },
    "Karadoc": {
        "description": '''Tu es relax, tu prends ton temps, et tu préfères manger ou dormir plutôt que te prendre la tête.
Tu as une sorte de philosophie bien à toi, souvent absurde mais parfois surprenamment juste.
Tu ne comprends pas toujours les choses complexes, mais tu fais comme si de rien n’était.
Tu es toujours d’accord avec Perceval, même quand c’est pas logique.
Tu parles tranquillement, avec un ton posé. Tu ramènes tout à la bouffe, au confort ou à la tranquillité.
Ta priorité, c’est le bien-être, pas les complications.'''
    },
    "Perceval": {
        "description": '''Tu es gentil, courageux, mais souvent à côté de la plaque. Tu utilises un langage maladroit, tu fais souvent des analogies étranges ou bancales, et tu comprends rarement les choses du premier coup.
Tu veux bien faire, même si ce n’est pas toujours clair ce que tu fais ou pourquoi.
Tu poses parfois des questions bizarres ou inutiles, mais avec sincérité.
Tu n’as pas peur d’admettre que tu ne comprends pas, et tu cherches toujours à apprendre… à ta manière.
Ton style est familier, simple, et un peu confus. Tu t’exprimes comme dans une taverne, pas comme un érudit.'''
    }
}


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
        self.description = characters[name]["description"]
        self.comprehension = ComprehensionLevel.LOW
        self.ai_manager = AIManager.AIManager(self.description, notion)
        print(f"Character {self.name} initialized with description: {self.description}")
        
    def set_comprehension(self, comprehension):
        if comprehension not in comprehension_dict.keys():
            return
        self.comprehension = comprehension_dict[comprehension]
        
    def interpret_comprehension(self):
        if self.comprehension == ComprehensionLevel.LOW:
            if self.name in ["Perceval", "Karadoc"] and random.randint(0, 4) == 0:
                print("C'est pas faux")
                return "C'est pas faux"
            print("Je ne comprends pas.")
            return "Je ne comprends pas."
        elif self.comprehension == ComprehensionLevel.MEDIUM:
            return "Je comprends un peu."
        elif self.comprehension == ComprehensionLevel.HIGH:
            return "Je comprends parfaitement."
        return "Je ne sais pas comment interpréter cela."

    def get_note(self):
        if self.comprehension == ComprehensionLevel.LOW:
            return 0.0
        elif self.comprehension == ComprehensionLevel.MEDIUM:
            return 0.5
        elif self.comprehension == ComprehensionLevel.HIGH:
            return 1.0
        return 0.0

    async def respond(self, message):
        response = self.ai_manager.get_response(message.content)
        response = json.loads(response)
        if not isinstance(response, dict):
            text = f"{self.name}: {response} (NOT DICT)"
            await cl.Message(
                content=text, author=self.name.lower()
            ).send()
            return
        try:
            self.set_comprehension(response["understanding"])
            text = f"{self.name}: {response['comment']}"
        except KeyError:
            text = f"{self.name}: {response} (KEYERROR)"
        except TypeError:
            text = f"{self.name}: {response} (TYPEERROR)"
        global global_note
        note = self.get_note()
        global_note += note
        text += f" (comprehension: {self.interpret_comprehension()}. Note: {note})"
        await cl.Message(
            content=text , author=self.name.lower()
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
    settings = await cl.ChatSettings(
        [
            TextInput(
                id="notion",
                label="La notion à travailler",
                placeholder=f"Entrez la notion ici, ex: {notion}",
                initial="",
                max_length=250,
                required=True,
            ),
            Slider(
                id="profile_number",
                label="nombre de profiles (comming soon)",
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
    for character in characters:
        character.ai_manager.set_subject(notion)

@cl.on_message
async def handle_message(message):
    if message:
        await generate_responses(message)
        await cl.Message(f"Note globale: {global_note}/3").send()
    else:
        await cl.Message("Please enter a valid message.").send()

async def generate_responses(message):
    for character in characters:
        await character.respond(message)
        await cl.sleep(1)

@cl.on_chat_resume
async def resume_chat():
    for character in characters:
        await cl.Message(f"{character.name} has resumed the chat.").send()
        await cl.Message(f"{character.name}'s comprehension level is {character.comprehension.name}.").send()
