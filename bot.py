import discord
import os
import asyncio
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER_URL = "http://localhost:5000/log"
START_TIME_FILE = "server/start_time.json"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

log_buffer = []

def load_start_time():
    try:
        with open(START_TIME_FILE, "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["start_time"])
    except:
        print("⚠️ Impossible de charger start_time.json")
        return datetime.now()

@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")
    client.loop.create_task(batch_sender())

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    if not message.author.bot:
        return

    print(f"📩 Message reçu :\n{message.content}")

    start_time = load_start_time()
    if message.created_at.replace(tzinfo=None) < start_time:
        print("⏳ Message ignoré : trop ancien")
        return

    content = message.content.lower()
    if "jus" not in content and "juice" not in content:
        print("❌ Pas de mot-clé 'jus' ou 'juice' dans le message")
        return

    lines = message.content.splitlines()
    name = None
    quantity = 0

    for line in lines:
        match = re.search(r"(\d+)x\s+Jus.*?par\s+([^.]+)", line, re.IGNORECASE)
        if match:
            try:
                quantity = int(match.group(1))
                name = match.group(2).strip()
            except Exception as e:
                print(f"❌ Erreur de parsing : {e}")
                return

    if name and quantity:
        log_buffer.append({"name": name, "quantity": quantity})
        print(f"🧃 Log capté : {name} - {quantity} jus")

async def batch_sender():
    await client.wait_until_ready()
    while not client.is_closed():
        if log_buffer:
            data = log_buffer.copy()
            print(f"📤 Envoi au serveur: {data}")
            try:
                response = requests.post(SERVER_URL, json=data)
                print(f"🌐 Réponse serveur: {response.status_code}")
                if response.status_code == 200:
                    print(f"🚀 {len(data)} ventes envoyées")
                    log_buffer.clear()
            except Exception as e:
                print(f"❌ Erreur d'envoi au serveur: {e}")
        await asyncio.sleep(600)

def start_bot():
    client.run(TOKEN)