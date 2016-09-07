import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from .utils.dataIO import fileIO
from .utils import checks
import re
import datetime
import time
import os
import asyncio


class chan_op:
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/channel_operator/settings.json", "load")
        self.wait_thing()

        self.server = None
        self.ow_status = True
        self.channel_names = None

    def wait_thing(self):
        self.server_id = "177855243231428608" #"184694956131221515" 
        self.server = self.bot.get_server(self.server_id)

    @commands.group(pass_context = True)
    @checks.mod_or_permissions(administrator = True, moderator = True)
    async def destruct(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = "```\n"
            for k, v in self.settings.items():
                msg += "{}: {} \n".format(k, v)
            msg += "```"
            await self.bot.say(msg)

    @checks.mod_or_permissions(administrator=True)
    @destruct.command()
    async def set_destruct(self, minutes : int):
        self.settings["destruct_time"] = minutes
        fileIO("data/channel_operator/settings.json", "save", self.settings)
        await self.bot.say("Self destruct time set to {} seconds".format(str(minutes)))

    @commands.command(pass_context = True)    
    async def ch(self, ctx, *text): 
        if self.server == None:
            self.wait_thing()
        #await self.bot.say("ch_command_")
        chans = self.server.channels #fetches all channels from server
        len_chans = sum(1 for _ in chans)
        voice_chan = await self.bot.create_channel(self.server, " ".join(text), type=discord.ChannelType.voice)
        await self.bot.say("Created {}".format(" ".join(text)))
        self.bot.edit_channel(voice_chan, position = len_chans - 1)
        timer_obj = time.perf_counter()
        await self.wait_for_destruction(voice_chan, voice_chan, timer_obj)

    async def ow_chans(self, member, whatever):
        #Matches any string formatted like: [OW] NA Quick #1  with groups = [region, gametype, number]

        self.redx = re.compile("(?:\[)(?:OW)(?:\])(?:\s)?(EU|NA)(?:\s)?(Comp|Quick)(?:\s)?(?:\S)([0-9]+)", re.I)
        self.server = member.server
        self.speak_chan = self.bot.get_channel("213000596930691072")
        await self.bot.send_message(self.speak_chan, (member.name, whatever.name))

        chans = self.server.channels #fetches all channels from server
        len_chans = sum(1 for _ in chans)
        chans = [chan for chan in chans] #saves all channel objects in a list - will be differently ordered for each iteraton because dictionaries. 
        self.channel_names = []
        list_of_toups = []
        made_chan = False
        ind_made = None
        sort_list = None
        
        for chan in chans: 
            #If condition to store all channel names that match the regular expression to help ensure that channels do not get doubly made
            evald = self.redx.match(chan.name)
            if evald is not None:
                self.channel_names.append(evald)

        sort_list = await self.sort(chans)
        await self.bot.send_message(self.speak_chan, sort_list)

        if sort_list is not None:
            for i in range(len(sort_list)): 
                m = self.redx.match(sort_list[i].name) #invocation of compiled regex 
                if m is not None:

                    chan_pos = sort_list[i].position #position of channel in list of channels
                    #await self.bot.say((sort_list[i].name, chan_pos))
                    next_name = m.group(0)[:-1] + "{}".format(str(int(m.group(3))+1)) #generates a string with an incremented number in the channel name
                    #await self.bot.say(next_name)
                    m_next = self.redx.match(next_name) # regex match off the next channels name

                    if len(sort_list[i].voice_members) >= 1:
                        await self.bot.send_message(self.speak_chan, ("Has member(s):", sort_list[i].name))
                        #await self.bot.say((next_name, sort_list[i].name, next_name in self.channel_names))
                        name_exists = []

                        for reg_chan in self.channel_names:
                            #Attempts to identify if channel name exists allready and ensures false if it does.
                            name_exists.append(await self.reg_comp(reg_chan, m_next))

                        #await self.bot.say("Should create {}? {}".format(next_name, name_exists))
                        #await self.bot.say(("Is there two channels with the same name?", name_exists))

                        if True in name_exists:
                            continue
                        else:
                            made_chan = True
                            ind_made = i
                            voice_chan = await self.bot.create_channel(self.server, next_name, type=discord.ChannelType.voice)
                            await self.bot.send_message(self.speak_chan,"Created channel: {}".format(next_name))
                            await self.bot.edit_channel(voice_chan, position = chan_pos + 1 )
                            await self.reorder(sort_list, i)
                            timer_obj = time.perf_counter()

                            self.channel_names.append(m_next)
                    else:
                        if int(m.group(3)) != 1:
                            await self.bot.send_message(self.speak_chan, (sort_list[i].created_at, datetime.utcnow()))
                        continue

    async def reg_comp(self, one, two):
        if (one.group(1) == two.group(1)) and ((one.group(2) == two.group(2)) and (one.group(3) == two.group(3))):
            #await self.bot.say(("These regexes were found equal:",one.group(0), two.group(0)))
            return True
        else:
            return False

    async def compare(self, chan1, chan2):
        #returns True if chan2 should have a higher index than chan1
        org_x = await self.prio( self.redx.match(chan1.name) )
        comp_x = await self.prio( self.redx.match(chan2.name) )

        if org_x[0] < comp_x[0] and org_x[1] < comp_x[1] and (org_x[2] < comp_x[2]):
            return True
        else:
            return False

    def sort(self, chans):
        #dumb-sort
        new_list = list(chans)
        sorted_list = []
        i = 0

        while i <= len(chans):
            for chan in new_list:
                comp_list = []
                for other in new_list:
                    comp_bool = await self.compare(chan, other)
                    comp_list.append(comp_bool)
                if not any(comp):
                    sort_list.append(chan)
                    new_list.remove(chan)
                    i+=1

        return sorted_list

    async def prio(self, regd):
        x = []
        if regd is not None:
            if regd.group(1) == "EU":
                x.append(1)
            elif regd.group(1) == "NA":
                x.append(2)
            else:
                x.append(3)

            if regd.group(2) == "Quick":
                x.append(1)
            else:
                x.append(2)

            x.append(int(regd.group(3)))

            await asyncio.sleep(1)
            return x 
        else:
            await asyncio.sleep(1)
            return [0, 0 ,0]

    @commands.command()        
    async def stop_ow(self):
        self.ow_status = False

def check_folders():
    folders = ("data", "data/channel_operator/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    settings = {"destruct_time": 60}

    if not os.path.isfile("data/channel_operator/settings.json"):
        print("Creating empty settings.json...")
        fileIO("data/channel_operator/settings.json", "save", settings)


def setup(bot):
    check_folders()
    check_files()
    n = chan_op(bot)
    bot.add_listener(n.ow_chans, "on_voice_state_update")
    bot.add_cog(n)