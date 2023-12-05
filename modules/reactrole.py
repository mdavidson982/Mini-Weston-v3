import discord, requests, json, aiohttp
from discord.ext import commands
import Private as p
import firebase_admin


class reactClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
        guildID = payload.guild_id
        channelID = payload.channel_id
        messageID = payload.message_id
        member = payload.member
        reaction = payload.emoji
        return guildID, channelID, messageID, member, reaction
    
    async def addRoleToDatabase(self, ctx,  guildID, messageID, roleData):
        db = self.bot.client
        #first check if the server is in the list
        serverRef = db.collection("Server")
        
        serverDoc = serverRef.document(str(guildID))
        if not serverDoc.get().exists:
           serverDoc.set({
               "name" : ctx.guild.name,
               "serverID" : str(guildID)
           })
           print(f"Server '{ctx.guild.name}':'{str(guildID)}' created!")
        

        rolesRef = serverDoc.collection("roles")
        roleDoc = rolesRef.document(str(messageID.id))

        if not roleDoc.get().exists:
            if roleDoc.get() != str(messageID.id):
                roleDoc.set({
                    "messageID": str(messageID.id),
                    "name": roleData.name,
                    "roleID": str(roleData.id)
                })
                print(f"Role '{roleData.name}':'{roleData.id}' document with messageID '{messageID.id}' created!")
                
            else:
                print(f"Role '{roleData}':'{roleData.id}' document with messageID '{messageID.id}' already exist.")
                
        else:
            roleDoc.set({
                "messageID": str(messageID.id),
                "name": roleData.name,
                "roleID": str(roleData.id)
            })
            print(f"Role '{roleData}':'{roleData.id}' document with messageID '{messageID.id}' updated!")
        
        
    async def addRoleToUserDatabase(self, member, roleID, serverID): 
        db = self.bot.client
        userDoc = db.collection("User").document(str(member.id))
        if userDoc.get().exists:
            #print("User Doc Found!")
            userDocData = userDoc.get().to_dict()
            userDocRoles = userDocData.get("roles")
            userDocServers = userDocData.get("servers")
            #print(userDocRoles)
            #print(userDocServers)
            if str(serverID.id) in userDocServers:
                #print("User In Server!")
                UsersRoleInServer = userDocRoles[str(serverID.id)]
                if roleID in UsersRoleInServer:
                    print("User Should Already Have The Role Assigned? Perchance the left and rejoined?")
                else:
                    #print("Adding Role to User!")
                    userDocRoles[serverID.id].extend(roleID)
                    userDoc.set({
                    "name":member.name,
                    "roles":userDocRoles,
                    "servers":userDocServers,
                    "userID":str(member.id)
                })
                    print(f"Updated {member.name}:{member.id} document in User collection. Added {roleID} to {serverID.id} key")
            else:
                #print(f"User isn't in server. Adding server id to list")
                userDocServers.append(str(serverID.id))
                userDocRoles[str(serverID.id)] = [str(roleID)]
                userDoc.set({
                "name":member.name,
                "roles":userDocRoles,
                "servers":userDocServers,
                "userID":str(member.id)
            })
                print(f"Updated {member.name}:{member.id} document in User collection. Added {serverID.id} and new KeyPair {serverID.id}:{roleID}")
        else:
            userDoc.set({
                "name":member.name,
                "roles":{str(serverID.id) : [str(roleID)]},
                "servers":[str(serverID.id)],
                "userID":str(member.id)
            })
            print(f"Added {member.name}:{member.id} document to User collection")
                

        


    
    @commands.command()
    async def addrole(self, ctx, roleData:discord.Role, channelID):
        channel = self.bot.get_channel(int(channelID))
        message = await channel.send(roleData.mention)
        await self.addRoleToDatabase(ctx, message.guild.id, message, roleData)
        await message.add_reaction(p.EMOJI_CONFIRM)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        if not dataCache[3].bot:
            db = self.bot.client
            #print(dataCache[2])
            serverDoc = db.collection("Server").document(str(dataCache[0])).collection("roles").document(str(dataCache[2]))
            if serverDoc.get().exists: #if a document with that message id exist
                serverDocData = serverDoc.get().to_dict()
                server = self.bot.get_guild(dataCache[0])
                roleID = serverDocData.get('roleID')
                if roleID:
                    role = server.get_role(int(roleID))
                    await dataCache[3].add_roles(role)
                    await self.addRoleToUserDatabase(dataCache[3], roleID, server)

                else:
                    print("Not In Document")
            else:
                print("Message ID not found in role subcollection")
        else:
            print("Reaction added to react role")
        
        #await channel.send("Bing Bong!")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        channel = self.bot.get_channel(dataCache[1])
        #await channel.send("Bong Bing!")

    


async def setup(bot):
    await bot.add_cog(reactClass(bot))