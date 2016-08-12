import discord
import json
import requests
from discord.ext import commands
from cogs.utils import checks

class countrycode:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def location(self, ctx, country: str):
        """Example: -location GB"""
        server = ctx.message.server
        user = ctx.message.author
        perms = discord.Permissions.none()

        response = requests.get("https://restcountries.eu/rest/v1/alpha/" + country)
        result = response.json()
        easter = "shithole";

        if response.status_code != 404:
            msg = "All members for " + result['name'] + " :flag_"+ result['alpha2Code'].lower() +":\n```"
            try:
                for member in server._members:
                    for role in server._members[member].roles:
                        if result['name'] == role.name:
                            msg = msg + "\n• " + server._members[member].name
                msg = msg + "```"
                if msg != "All members for " + result['name'] + " :flag_"+ result['alpha2Code'].lower() +":\n``````":
                    await self.bot.say(msg)
                else:
                    await self.bot.say("No one found in " + result['name'] + " :flag_"+ result['alpha2Code'].lower() +": :(")
            except:
                await self.bot.say("w00ps, something went wrong! :( Please try again.")
        else:
            if country.lower() == easter:
                msg = "All members for SHITHOLE :poop: : \n```•SpiritoftheWest#4290```"
                await self.bot.say(msg)
            else:
                await self.bot.say("Sorry I don't know your country! Did you use the correct ISO countrycode? \nExample: `-location GB`")
def setup(bot):
    bot.add_cog(countrycode(bot))
