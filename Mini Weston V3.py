import discord
from discord.ext import commands
import sys, traceback, os
import Private as p
import firebase_admin
from firebase_admin import credentials, db
from google.cloud import firestore

class MiniWeston(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.members = True
        intents.guild_scheduled_events = True
        intents.guild_messages = True
        self.client = None
        super().__init__(command_prefix=commands.when_mentioned_or('-'), intents=intents)


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        cred = credentials.Certificate("./serviceAccountKey.json")
        app = firebase_admin.initialize_app(cred, {"databaseURL": "https://mini-weston-v3-7fb89.firebaseio.com"})
        client = firestore.Client(credentials=app.credential.get_credential(), project= app.project_id)
        self.client = client


    async def setup_hook(self):
        for filename in os.listdir('./modules'):
            if filename .endswith('.py'):
                await self.load_extension(f'modules.{filename[:-3]}')

bot = MiniWeston()
bot.run(p.DISCORD_API_KEY)