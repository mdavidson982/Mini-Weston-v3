import discord, requests, json, aiohttp
from discord.ext import commands
import Private as p
from SQLconnector import SQLPool as sql
import firebase_admin


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
    
    async def addRoleToDatabase(self, ctx,  guildID, messageID, roleData):
        db = await sql.connect()
        db.close()
        #first check if the server is in the list
        serverRef = db.collection("Server")
        
        serverDoc = serverRef.document(str(guildID))
        print(guildID)
        if not serverDoc.get().exists:
           serverDoc.set({
               "name" : ctx.guild.name,
               "serverID" : str(guildID)
           })
        

        rolesRef = serverDoc.collection("roles")
        roleDoc = rolesRef.document(str(roleData.id))

        if not roleDoc.get().exists:
            if roleDoc.get() != str(messageID.id):
                roleDoc.set({
                    "messageID": str(messageID.id),
                    "name": roleData.name,
                    "roleID": str(roleData.id)
                })
                await ctx.send(f"Role '{roleData.name}':'{roleData.id}' document with messageID '{messageID.id}' created!")
                
            else:
                await ctx.send(f"Role '{roleData}':'{roleData.id}' document with messageID '{messageID.id}' already exist.")
                
        else:
            roleDoc.set({
                "messageID": str(messageID.id),
                "name": roleData.name,
                "roleID": str(roleData.id)
            })
            await ctx.send(f"Role '{roleData}':'{roleData.id}' document with messageID '{messageID.id}' updated!")
        app = firebase_admin.get_app()
        firebase_admin.delete_app(app)
        
        
        

    
    @commands.command()
    async def addrole(self, ctx, roleData:discord.Role, channelID):
        channel = self.bot.get_channel(int(channelID))
        message = await channel.send(roleData.mention)
        await self.addRoleToDatabase(ctx, message.guild.id, message, roleData)
        await message.add_reaction(p.EMOJI_CONFIRM)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        channel = self.bot.get_channel(dataCache[1])
        #await channel.send("Bing Bong!")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        channel = self.bot.get_channel(dataCache[1])
        #await channel.send("Bong Bing!")

    


async def setup(bot):
    await bot.add_cog(reactClass(bot))