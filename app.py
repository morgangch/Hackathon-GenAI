import chainlit as cl

class Agent:
    def __init__(self, name):
        self.name = name

    def respond(self, message):
        return f"{self.name} says: {message.content}"

@cl.on_chat_start
async def start_chat():
    await cl.Message("Welcome to the chat! Please enter your message below.").send()

@cl.on_message
async def handle_message(message):
    if message:
        await generate_responses(message)
    else:
        await cl.Message("Please enter a valid message.").send()

async def generate_responses(message):
    # Simulate generating responses
    agents = [Agent("Agent 1"), Agent("Agent 2")]
    for agent in agents:
        await cl.Message(f"{agent.name} is thinking...").send()
        await cl.sleep(1)  # Simulate thinking time
