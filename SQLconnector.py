import os
from discord.ext import commands
import Private as p
import firebase_admin
from firebase_admin import credentials, db
from google.cloud import firestore



class SQLPool(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def connect():
        cred = credentials.Certificate("./serviceAccountKey.json")
        app = firebase_admin.initialize_app(cred, {"databaseURL": "https://mini-weston-v3-7fb89.firebaseio.com"})
        client = firestore.Client(credentials=app.credential.get_credential(), project= app.project_id)
        return client

async def setup(bot):
    await bot.add_cog(SQLPool(bot))