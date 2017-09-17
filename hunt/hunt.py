from discord.ext import commands
from discord.utils import get
from .utils.dataIO import dataIO 
from .utils import checks
import os
import discord

class Hunt:
    def __init__(self, bot):
        self.bot = bot
        self.owner = get(self.bot.get_all_members(), id=self.bot.settings.owner)
        self.answers = dataIO.load_json("data/Tasty/Hunt/answers.json")
        self.riddles = dataIO.load_json("data/Tasty/Hunt/riddles.json")
        self.settings = dataIO.load_json("data/Tasty/Hunt/settings.json")
            
    
    @commands.command(pass_context=True, no_pm=True)
    async def hunt(self, ctx):
        server = ctx.message.server
        member = ctx.message.author
        score = 0
        role = discord.utils.get(server.roles, name="Puzzle Hunter")

        await self.bot.send_message(ctx.message.author, "Welcome {} to the treasure hunt! Can you find the final hidden command and claim your reward? \nEach riddle will get harder and harder so good luck!\n**Write the answer to the riddles as a command in any channel (-[answer])**".format(ctx.message.author.mention))
        await self.bot.add_roles(member, role)
        
        for index, question in enumerate(self.riddles):
            await self.bot.send_message(member, question)
            msg = await self.bot.wait_for_message(author=ctx.message.author)
            if isinstance(msg.channel.type, type(discord.ChannelType.private)):
                pass
            else:
                await self.bot.delete_message(msg)

            if msg.content[1:-1] == self.answers[index]:
                score += 1
                await self.bot.delete_message(ctx.message)
	   
        if score >= 10:
          role = discord.utils.get(server.roles, name="Puzzle King/Queen")
          await self.bot.add_roles(member, role)


    @checks.is_owner()
    @commands.command(hidden=True, pass_context=True)
    async def sethunt(self, ctx): #This is a cheat method because the bot will only do it for one 
        await self.bot.send_message(ctx.message.channel, "Re-setting the hunt... please wait")
        await self.bot.send_message(ctx.message.channel, "__**READ CAREFULLY**__ \n\nPlease type `-done` to finish, each message YOU send will be treated as a response.")

        while True:
            await self.bot.send_message(ctx.message.channel, "\n\n**Please enter a Riddle**")
            msg = await self.bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)

            if msg.content == "-done":
                break #Ik, ik **shush**
            else:
                self.riddles.append(msg.content)

            await self.bot.send_message(ctx.message.channel, "\n\n**Please enter the Answer**")
            msg = await self.bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)

            if msg.content == "-done":
                del self.riddles[-1]
                break #... quiet
            
            else:
                self.answers.append(msg.content)

        dataIO.save_json("data/Tasty/Hunt/answers.json", self.answers)
        dataIO.save_json("data/Tasty/Hunt/riddles.json", self.riddles)
            
            
                
        pass #Some loop here to get the admin to add stuff (riddles and answers and then store it in the file)

    async def add_role(self, ctx, role):
        try:
            await self.bot.add_roles(ctx.message.author, role)
        except:
            await self.bot.send_message(ctx.message.channel, "Woops! I need the `manage roles` permission.")


def check_folders(): #Creates a folder
    if not os.path.exists("data/Tasty/Hunt"):
        print("Creating data/Tasty/Hunt folder...")
        os.makedirs("data/Tasty/Hunt")

def check_files(): #Creates json files in the folder
    if not dataIO.is_valid_json("data/Tasty/Hunt/riddles.json"):
        print("Creating empty riddles.json...")
        dataIO.save_json("data/Tasty/Hunt/riddles.json", [])

    if not dataIO.is_valid_json("data/Tasty/Hunt/answers.json"):
        print("Creating empty answers.json...")    
        dataIO.save_json("data/Tasty/Hunt/answers.json", [])

    if not dataIO.is_valid_json("data/Tasty/Hunt/settings.json"):
        print("Creating empty settings.json...")    
        dataIO.save_json("data/Tasty/Hunt/settings.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Hunt(bot))
