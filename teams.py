import random
import discord
from discord.ext import commands

class teams:
	"""Randomly generates two teams from a voice channel."""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def teamgen(self, ctx):
		#just a random comment yo
		"""This generates the teams"""
		players = [member.name for member in ctx.message.author.voice_channel.voice_members]
		random.shuffle(players)
		n = len(players)//2
		team1 = players[:n]
		team2 = players[n:]
		await self.bot.say("```Team 1: \n" + "\n".join(team1) + "\n\nTeam 2: \n" + "\n".join(team2) + "```")
		

def setup(bot):
	bot.add_cog(teams(bot))
