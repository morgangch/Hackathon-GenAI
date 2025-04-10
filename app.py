import chainlit as cl 

class Characters:
    def __init__(self, name):
        self.name = name

    def respond(self, message):
        return f"{self.name} says: {message.content}"
    
characters = [Characters("Kadoc"), Characters("Karadoc"), Characters("Perceval")]


@cl.on_chat_start
async def start_chat():
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

async def profil_manager(name):
    await cl.Message(content=f"{name} has joined the chat.", author=name.lower()).send()