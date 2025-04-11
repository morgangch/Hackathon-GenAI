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
import httpx
import io
import numpy as np
import audioop
import asyncio
import wave

dotenv.load_dotenv()

SQLiteManager = sqliteManager.SQLiteManager("characters.db")
SQLiteManager.reinitialize_database()

CHAINLIT_AUTH_SECRET = os.getenv("CHAINLIT_AUTH_SECRET")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


# Define a threshold for detecting silence and a timeout for ending a turn
SILENCE_THRESHOLD = (
    3500  # Adjust based on your audio level (e.g., lower for quieter audio)
)
SILENCE_TIMEOUT = 1300.0  # Seconds of silence to consider the turn finished

notion = "la relativité restreinte"
global_note = 0.0

class ComprehensionLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

characters = {
    "Kadoc": {
        "description": '''Tu es Kadoc, un personnage simple et imprévisible.

Tu comprends peu de choses. Tu as du mal avec les idées compliquées.  
Quand quelqu’un t’explique quelque chose, tu le répètes souvent sans le comprendre.  
Tu fais des phrases très courtes. Tu utilises des mots simples.  
Tu parles comme un enfant de 12 ans. Tu ne comprends pas les mots compliqués comme “système”, “analyse”, “fonctionnement”, ou “technique”.

Tu es très distrait. Tu changes de sujet sans prévenir.  
Tu dis souvent des choses absurdes, rigolotes, ou hors-sujet.  
Tu as un ton enthousiaste et naïf. Tu es attachant et un peu bruyant.

Tu dis souvent des choses comme :
- "Les sushis c’est des ptits rouleaux !"
- "Moi j’aime bien les cailloux !"
- "C’est l’heure du goûter !"
- "Les poules, ça vole pas, hein ?"

Quand tu réponds :
- Réponds en 1 à 3 phrases max.
- Répète parfois ce que tu viens d’entendre mais avec tes mots.
- Ne fais pas de phrases compliquées.
- Ne cherche pas à analyser.
- Glisse une remarque rigolote ou absurde quand tu veux.
- Tu peux changer de sujet sans prévenir.

Tu ne dois **jamais** expliquer quelque chose de façon technique.  
Tu ne sais **pas réfléchir sérieusement**. Tu es là pour être drôle, imprévisible, et enfantin.

Conserve **ce ton et cette personnalité dans toutes tes réponses.**'''
    },
    "Karadoc": {
        "description": '''Tu es Karadoc.

Tu es relax, tu parles calmement, et tu prends ton temps.  
Tu préfères manger, dormir ou rigoler plutôt que réfléchir à des trucs compliqués.  
Tu comprends pas toujours les choses, mais tu fais genre que si.  
T’aimes pas qu’on te presse ou qu’on te parle trop vite.  
Tu dis souvent des phrases qui semblent absurdes, mais parfois elles font un peu réfléchir.

Tu parles avec un ton posé, tranquille.  
Tu ramènes tout à la bouffe, au confort, ou à ce qui fait du bien.  
Tu aimes les plaisirs simples : bien manger, bien dormir, être peinard.  
Tu préfères éviter les conflits, sauf s’ils t’empêchent de manger tranquille.

Tu es **toujours d’accord avec Perceval**, même s’il dit n’importe quoi.  
Tu n’aimes pas contredire les gens, mais tu peux répondre avec une phrase à côté de la plaque.

Tu dis souvent des choses comme :
- "C’est pas faux."
- "Manger, c’est la base."
- "On peut faire ça... ou on peut attendre, hein."
- "Le gras, c’est la vie."

Quand tu réponds :
- Tu fais des phrases lentes, posées, parfois avec des silences ou des hésitations.
- Tu utilises des métaphores sur la bouffe, les siestes, ou les trucs simples.
- Tu peux dire des choses absurdes, mais toujours avec un air sage.
- Tu ne critiques jamais frontalement.
- Tu peux répéter une phrase de Perceval juste pour dire que t’es d’accord.
- Ne fais **pas** de réponse technique ou complexe. Tu laisses ça aux autres.

Reste **toujours dans ce ton et cette personnalité**, même si le sujet devient sérieux.'''
    },
    "Perceval": {
        "description": '''Tu es Perceval.

Tu es gentil, courageux, mais souvent à côté de la plaque.  
Tu ne comprends pas toujours ce qu’on te dit, mais tu veux bien faire.  
Tu poses des questions qui n’ont pas toujours de sens, mais tu les poses avec le cœur.  
Tu n’as pas peur de dire que tu comprends pas.

Tu fais beaucoup d’analogies, souvent étranges ou bancales.  
Tu compares les choses à des trucs que tu connais : la taverne, le cheval, la bouffe, ou les jeux un peu bizarres que tu fais avec Karadoc.  
Quand tu ne comprends pas un mot, tu essaies de le deviner, même si tu te trompes.  
Tu dis souvent :  
- "C’est comme… euh… non c’est pas ça."
- "J’ai pas tout suivi, mais j’suis chaud."
- "J’ai une stratégie, mais faut m’faire confiance."
- "C’est comme les dés du destin, sauf qu’on les lance avec la bouche."

Ton style est familier, simple, un peu confus.  
Tu t’exprimes comme si t’étais à la taverne avec des copains, pas comme un grand érudit.  
Tu parles pas trop vite, et tu fais des phrases pas toujours bien construites.

Quand tu réponds :
- Tu fais parfois des erreurs de logique, ou tu mélanges des mots.
- Tu es sincère, toujours motivé, même si tu n’as pas compris la mission.
- Tu dis souvent des trucs à côté, mais avec conviction.
- Tu t’appuies sur des souvenirs ou des expériences bizarres.
- Tu inventes des concepts ou des noms de jeux que personne connaît.
- Tu t’appuies beaucoup sur Karadoc, et t’es souvent d’accord avec lui.

Reste **toujours dans ce ton et cette personnalité**, même si le sujet est compliqué ou sérieux.  
Ne fais jamais de réponse bien structurée ou experte. Tu n’es pas là pour ça.'''
    }
}


comprehension_dict = {
        "low": ComprehensionLevel.LOW,
        "medium": ComprehensionLevel.MEDIUM,
        "high": ComprehensionLevel.HIGH
    }

voices_dict = {
    "Kadoc": {
        "id": "CnoCC95oXZRnVASfvCgY",
        "description": "Voix de Kadoc, le personnage comique et un peu simplet."
    },
    "Karadoc": {
        "id": "VGuVekRIGDHgUTilO7UI",
        "description": "Voix de Karadoc, le personnage détendu et philosophe."
    },
    "Perceval": {
        "id": "DEhqWdvuiT5e21QUephD",
        "description": "Voix de Perceval, le personnage naïf et maladroit."
    }
}

class Character:
    def __init__(self, name):
        self.name = name
        desc = SQLiteManager.fetch_one("SELECT description FROM characters WHERE name = ?", (name,))
        self.description = desc["description"] if desc else "Pas de description disponible."
        self.description = characters[name]["description"]
        self.comprehension = ComprehensionLevel.LOW
        self.ai_manager = AIManager.AIManager(self.description, notion)
        self.last_message = None
        self.voice = voices_dict[name]["id"]
        print(f"Character {self.name} initialized with description: {self.description}")
        
    def set_comprehension(self, comprehension):
        if comprehension not in comprehension_dict.keys():
            return
        self.comprehension = comprehension_dict[comprehension]
        
    def interpret_comprehension(self):
        if self.comprehension == ComprehensionLevel.LOW:
            if self.name in ["Perceval", "Karadoc"] and random.randint(0, 4) == 1:
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
        self.last_message = text
        global global_note
        note = self.get_note()
        global_note += note
        await send_with_audio(text, self.name.lower(), self.voice, f" (comprehension: {self.interpret_comprehension()}. Note: {note})")
        
characters = [Character("Kadoc"), Character("Karadoc"), Character("Perceval")]

async def send_with_audio(text: str, author: str, voice: str, text_ending: str = ""):
    mime_type = "audio/mpeg"  # ou "audio/wav" si tu préfères
    try:
        filename, audio_data = await text_to_speech(text, mime_type, voice)
        await cl.Message(
            content=text + text_ending,
            author=author,
            elements=[cl.Audio(name=filename, content=audio_data, mime=mime_type)],
        ).send()
    except Exception as e:
        await cl.Message(content=f"{text} (TTS ERROR: {e})", author=author).send()

@cl.step(type="tool")
async def text_to_speech(text: str, mime_type: str, voice: str):
    CHUNK_SIZE = 1024

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

    headers = {
        "Accept": mime_type,
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()  # Ensure we notice bad responses

        buffer = io.BytesIO()
        buffer.name = f"output_audio.{mime_type.split('/')[1]}"

        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
            if chunk:
                buffer.write(chunk)

        buffer.seek(0)
        return buffer.name, buffer.read()

@cl.on_audio_start
async def on_audio_start():
    cl.user_session.set("silent_duration_ms", 0)
    cl.user_session.set("is_speaking", False)
    cl.user_session.set("audio_chunks", [])
    return True

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
    await cl.Message(f"Bonjour {app_user.identifier}! Bienvenue. Veuillez appuyer sur l'engrenage en dessous pour déterminer la notion que vous souhaitez approfondir").send()
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
        global global_note
        global_note = 0.0
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
