import discord
import requests
from discord.ext import commands
from cogs.utils import checks


class countrycode:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def country(self, ctx, country: str):

        server = ctx.message.server
        user = ctx.message.author
        perms = discord.Permissions.none()

        response = requests.get("https://restcountries.eu/rest/v1/alpha/" + country)
        result = response.json()

        if response.status_code != 404:
            try:
                if result['name'] not in [r.name for r in server.roles]:
                    await self.bot.create_role(server, name=result['name'], permissions=perms)
                    await self.bot.say("Added " + result['name'] + " to country list!")
                role = discord.utils.get(ctx.message.server.roles, name=result['name'])
                if result['name'] not in [r.name for r in user.roles]:
                    await self.bot.add_roles(user, role)
                    await self.bot.say("Greetings from " + result['name'] + " by " + user.mention)
                else:
                    await self.bot.say("You already set your country origin to that country!")
            except AttributeError:
                await self.bot.say("w00ps, something went wrong! :( Please try again.")
        else:
            await self.bot.say("Sorry, I don't know your country! Did you use the correct ISO countrycode?\nExample: `-addcountry GB`")

    @commands.command(pass_context=True, no_pm=True)
    async def removecountry(self, ctx, country: str):

        server = ctx.message.server
        user = ctx.message.author
        perms = discord.Permissions.none()

        response = requests.get("https://restcountries.eu/rest/v1/alpha/" + country)
        result = response.json()
        try:
            if response.status_code != 404:
                if result['name'] not in [r.name for r in server.roles]:
                    await self.bot.create_role(server, name=result['name'], permissions=perms)
                r = discord.utils.get(ctx.message.server.roles, name=result['name'])
                if result['name'] in [r.name for r in user.roles]:
                    await self.bot.remove_roles(user, r)
                    await self.bot.say(
                        "The boys and girls from " + result['name'] + " will miss you " + user.mention + "! :(")
                else:
                    await self.bot.say("You already removed that country as your country origin!")
            else:
                await self.bot.say("Sorry, I don't know your country! Did you use the correct ISO countrycode?\nExample: `-addcountry GB`")
        except:
            await self.bot.say("w00ps, something went wrong! :( (Module: Countrycode)")


def setup(bot):
    bot.add_cog(countrycode(bot))
