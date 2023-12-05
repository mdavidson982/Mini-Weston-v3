import discord, requests, json, aiohttp
from discord.ext import commands
import Private as p

class reactClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
        guildID = payload.guild_id
        channelID = payload.channel_id
        messageID = payload.message_id
        userID = payload.user_id
        reaction = payload.emoji
        return guildID, channelID, messageID, userID, reaction
    
    @commands.command()
    async def addrole(self, roleData, channelID):
        channel = self.bot.get_channel(int(channelID))
        message = await channel.send(roleData)
        await message.add_reaction(p.EMOJI_CONFIRM)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        channel = self.bot.get_channel(dataCache[1])
        await channel.send("Bing Bong!")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        channel = self.bot.get_channel(dataCache[1])
        await channel.send("Bong Bing!")

    


async def setup(bot):
    await bot.add_cog(reactClass(bot))