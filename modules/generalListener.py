import discord, requests, json, aiohttp
from discord.ext import commands
import Private as p
import firebase_admin


class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Hell Yeah Brother")
            break
        db = self.bot.client
        #first check if the server is in the list
        serverRef = db.collection("Server")
        
        serverDoc = serverRef.document(str(guild.id))
        if not serverDoc.get().exists:
           serverDoc.set({
               "name" : guild.name,
               "serverID" : str(guild.id)
           })
           print(f"Server '{guild.name}':'{str(guild.id)}' created!")


async def setup(bot):
    await bot.add_cog(Listener(bot))
