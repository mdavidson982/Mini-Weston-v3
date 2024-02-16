import discord, requests, json, aiohttp
from discord.ext import commands
import Private as p
import firebase_admin
from google.cloud import firestore


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
                    userDocRoles[str(serverID.id)].append(str(roleID))
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
                

        
    async def removeRoleToDatabase(self, member, roleID, serverID):
        db = self.bot.client
        userDoc = db.collection("User").document(str(member.id))
        if userDoc.get().exists:
            #print("User Doc Found!")
            userDocData = userDoc.get().to_dict()
            userDocRoles = userDocData.get("roles")
            userDocServers = userDocData.get("servers")
            #print(userDocRoles)
            #print(userDocServers)
            if str(serverID) in userDocServers and str(serverID) in userDocRoles:
                #print("User In Server!")
                UsersRoleInServer = userDocRoles[str(serverID)]
                if roleID in UsersRoleInServer:
                    #print("Adding Role to User!")
                    userDocRoles[str(serverID)].remove(str(roleID))
                    userDoc.set({
                    "name":member.name,
                    "roles":userDocRoles,
                    "servers":userDocServers,
                    "userID":str(member.id)
                })
                    print(f"Updated {member.name}:{member.id} document in User collection. Removed {roleID} to {serverID} key")
                else:
                    print("User shouldn't have this role to begin with?")
                    
            else:
                print(f"User isn't in server. Adding server ID. BUT The user shouldn't have this role?")
                userDocServers.append(str(serverID))
                userDocRoles[str(serverID)] = []
                userDoc.set({
                "name":member.name,
                "roles":userDocRoles,
                "servers":userDocServers,
                "userID":str(member.id)
            })
                print(f"Updated {member.name}:{member.id} document in User collection. Added {serverID} ignored {roleID}")
        else:
            userDoc.set({
                "name":member.name,
                "roles":{str(serverID) : []},
                "servers":[str(serverID)],
                "userID":str(member.id)
            })
            print(f"Added {member.name}:{member.id} document to User collection")

    
    @commands.command()
    async def addrole(self, ctx, roleData:discord.Role, channelID):
        channel = self.bot.get_channel(int(channelID))
        message = await channel.send(roleData.mention)
        await self.addRoleToDatabase(ctx, message.guild.id, message, roleData)
        await message.add_reaction(p.EMOJI_CONFIRM)

    @commands.command()
    async def removerole(self, ctx, messageID):
        db = self.bot.client
        serverDoc = db.collection("Server").document(str(ctx.guild.id)).collection("roles").document(str(messageID))
        if serverDoc.get().exists:
            serverDoc.delete()


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def addAdminRoles(self, ctx):
        db = self.bot.client
        serverRef = db.collection("User")
        membersList = ctx.message.mentions
        rolesList = ctx.message.role_mentions
        rolesIDList = []
        for role in rolesList:
            rolesIDList.append(str(role.id))
        dataToAdd = {
            str(ctx.guild.id):rolesIDList
        }
        for members in membersList:
            userDoc = serverRef.document(str(members.id))
            if userDoc.get().exists:
                userDoc.update({"adminRoles":{str(ctx.guild.id):rolesIDList}})
            else:
                print("Adding User to table via addAdminRoles")
                await self.removeRoleToDatabase(members, 0, ctx.guild)
                userDoc.update({"adminRoles":{str(ctx.guild.id):rolesIDList}})
            print(type(rolesList))
            await members.add_roles(*rolesList)    
               

    @commands.command()
    async def reinstate(self, ctx):
        user = ctx.message.author
        userID = user.id
        db = self.bot.client
        guild = ctx.guild
        guildID = ctx.guild.id
        userDoc = db.collection("User").document(str(userID))

        if userDoc.get().exists:
            userDocData = userDoc.get().to_dict()
            userDocRoles = userDocData.get("roles")
            userDocServers = userDocData.get("servers")
            

            
            if str(ctx.guild.id) in userDocServers:
                usersRoleInServer = userDocRoles[str(guildID)]
                roles = guild.roles
                admin = False
                adminRolesInServer = None
                if "adminRoles" in userDocData and str(guildID) in userDocData["adminRoles"]:
                    adminRolesInServer = userDocData["adminRoles"][str(ctx.guild.id)]
                    admin = True
                for role in roles:
                    if str(role.id) in usersRoleInServer:
                        await ctx.author.add_roles(role)
                    if admin and str(role.id) in adminRolesInServer:
                        await ctx.author.add_roles(role)
                    

            else:
                print("Reinstate user wasn't in the server. Ignoring command and adding user to database")
                userDoc.set({
                    "name":user.name,
                    "roles":userDocRoles,
                    "servers":userDocServers.append(guildID),
                    "userID":str(user.id)
                })
        else:
            await ctx.send("You new here?") #add the user to the firebase server. If the user isn't in the doc it uses the bottom condition
            await self.removeRoleToDatabase(user,0, guildID)


    @commands.command(name="_registerAll")
    @commands.has_permissions(administrator=True)
    async def _registerAll(self, ctx):
        guild = ctx.guild
        db = self.bot.client
        user_collection = db.collection("User")

        print("Command Start")

        for member in guild.members:
            # Skip bot accounts
            if not member.bot:
                    
                
                # Check if user is already in the database
                userDoc = user_collection.document(str(member.id))
                if not userDoc.get().exists:
                    # Create a new user document if not existing
                    print("Create User Doc")
                    userDoc.set({
                        "name": member.name,
                        "roles": {},
                        "adminRoles": {},
                        "servers": [str(ctx.guild.id)],
                        "userID": str(member.id)
                    })

                # Fetch or create the roles and adminRoles maps
                user_data = userDoc.get().to_dict()
                roles = user_data.get("roles", {})
                admin_roles = user_data.get("adminRoles", {})

                # Iterate through member's roles
                non_admin_roles = []
                admin_role_ids = []
                for role in member.roles:
                    if role.permissions.administrator:
                        admin_role_ids.append(str(role.id))
                    else:
                        if role.id != guild.id:
                            non_admin_roles.append(str(role.id))

                # Update roles and adminRoles in the user document
                roles[str(guild.id)] = non_admin_roles
                admin_roles[str(guild.id)] = admin_role_ids
                userDoc.update({
                    "roles": roles,
                    "adminRoles": admin_roles
                })
    
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
        
        

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        dataCache = self.parse_reaction_payload(payload)
        guild = self.bot.get_guild(dataCache[0])
        member = await guild.fetch_member(payload.user_id)
        if not member.bot:
            db = self.bot.client
            #print(dataCache[2])
            serverDoc = db.collection("Server").document(str(dataCache[0])).collection("roles").document(str(dataCache[2]))
            if serverDoc.get().exists: #if a document with that message id exist
                serverDocData = serverDoc.get().to_dict()
                server = self.bot.get_guild(dataCache[0])
                roleID = serverDocData.get('roleID')
                if roleID:
                    role = server.get_role(int(roleID))
                    await member.remove_roles(role)
                    await self.removeRoleToDatabase(member, roleID, server)

                else:
                    print("Not In Document")
            else:
                print("Message ID not found in role subcollection")
        else:
            print("Bot Removed Emoji")

        

    


async def setup(bot):
    await bot.add_cog(reactClass(bot))