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
        await cl.Message(f"{character.name} has joined the chat.").send()

@cl.on_message
async def handle_message(message):
    if message:
        await generate_responses(message)
    else:
        await cl.Message("Please enter a valid message.").send()

async def generate_responses(message):
    for character in characters:
        await cl.Message(f"{character.name} is thinking...").send()
        await cl.sleep(1)  # Simulate thinking time

