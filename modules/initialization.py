import discord
from discord.ext import commands
from SQLconnector import SQLPool as SQLc

class initialization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Joined Servers: ")
        for guild in self.bot.guilds:
            selected_channel = guild.name
            print(selected_channel)
        dbRef = await SQLc.connect()
        collections = dbRef.collection("Server").document("785260019209863220").collections()
        for collection in collections:
            for doc in collection.stream():
                print(f"{doc.id} => {doc.to_dict()}")


async def setup(bot):
    await bot.add_cog(initialization(bot))