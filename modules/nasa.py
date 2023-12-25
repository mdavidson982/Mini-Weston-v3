import discord, requests, json, aiohttp
from discord.ext import commands
import Private as p

#NASA Buttons
"""
class ReturntoImage(discord.ui.View):
    def __init__(self, json, timeout = 180):
        super().__init__(timeout=timeout)
        self.js = json

    @discord.ui.button(label="Return to Image", style=discord.ButtonStyle.green,)
    async def viewImage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if(self.js["media_type"] == "image"):
                apodImageEmbed = discord.Embed(title = "**" + self.js["title"] + "**", color = discord.Color.teal()  , url = self.js["url"])

                if("hdurl" in self.js):
                    apodImageEmbed.set_image(url = self.js["hdurl"])
                    apodImageEmbed.set_footer(text = "NASA Astronomy Picture of the Day | Date: {date}".format(date = self.js["date"]), icon_url= "https://cdn.discordapp.com/attachments/849172801076199495/1049776014131200021/nasa-logo-web-rgb.png")
                else:
                    apodImageEmbed.set_image(self.js["url"])
                    apodImageEmbed.set_footer(text = "NASA Astronomy Picture of the Day | Date: {date} |".format(date = self.js["date"]), icon_url= "https://cdn.discordapp.com/attachments/849172801076199495/1049776014131200021/nasa-logo-web-rgb.png")

        await interaction.response.edit_message(embed=apodImageEmbed, view = ReadDescription(self.js))
        

class ReadDescription(discord.ui.View):
    def __init__(self, json, timeout = 180):
        super().__init__(timeout=timeout)
        self.js = json

    
    @discord.ui.button(label='Read Description', style=discord.ButtonStyle.green, )
    async def viewDescription(self, interaction: discord.Interaction, button: discord.ui.Button):
        apodDescriptionEmbed = discord.Embed(title = "**" + self.js["title"] + "**", color = discord.Color.teal()  , url = self.js["url"])
        apodDescriptionEmbed.set_footer(text=self.js["explanation"])
        apodDescriptionEmbed.set_thumbnail(url= "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/NASA_Worm_logo.svg/2560px-NASA_Worm_logo.svg.png")
        await interaction.response.edit_message(embed = apodDescriptionEmbed, view = ReturntoImage(self.js))

"""

class linkedButton(discord.ui.View):
    def __init__(self, json, timeout = 180):
        super().__init__(timeout=timeout)
        self.js = json
        button = discord.ui.Button(label= "View Full Image", style = discord.ButtonStyle.link,url= self.js["url"] )
        self.add_item(button)


class nasa(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def apod(self,ctx):
        base_url = "https://api.nasa.gov/planetary/apod?api_key="
        
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url + p.NASA_API_KEY) as r:
                self.js = await r.json()
                print(base_url + p.NASA_API_KEY)
        
        if(self.js["media_type"] == "image"):
            apodImageEmbed = discord.Embed(title = "**" + self.js["title"] + "**", color = discord.Color.teal()  , url = self.js["url"], description=self.js["explanation"])

            if("hdurl" in self.js):
                apodImageEmbed.set_image(url = self.js["hdurl"])
                apodImageEmbed.set_footer(text = "NASA Astronomy Picture of the Day | Date: {date}".format(date = self.js["date"]), icon_url= "https://cdn.discordapp.com/attachments/849172801076199495/1049776014131200021/nasa-logo-web-rgb.png")
            else:
                apodImageEmbed.set_image(self.js["url"])
                apodImageEmbed.set_footer(text = "NASA Astronomy Picture of the Day | Date: {date} |".format(date = self.js["date"]), icon_url= "https://cdn.discordapp.com/attachments/849172801076199495/1049776014131200021/nasa-logo-web-rgb.png")
            await ctx.send(embed=apodImageEmbed, view = linkedButton(self.js))
        elif(self.js["media_type"] == "video"):
            apodImageEmbed = discord.Embed(title="**" + self.js["title"] + "**", color = discord.Color.teal()  , url = self.js["url"], description=self.js["explanation"])
            apodImageEmbed.set_footer(text = "NASA Astronomy Picture of the Day | Date: {date}".format(date = self.js["date"]), icon_url= "https://cdn.discordapp.com/attachments/849172801076199495/1049776014131200021/nasa-logo-web-rgb.png")
            await ctx.send(embed=apodImageEmbed, view = linkedButton(self.js))
            await ctx.send(self.js["url"])


async def setup(bot):
    await bot.add_cog(nasa(bot))