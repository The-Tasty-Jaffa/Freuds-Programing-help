from discord.ext import commands
from discord.utils import get
from .utils.dataIO import dataIO 
from .utils import checks
from .utils.chat_formatting import pagify, box
import os
import discord, asyncio

class Hunt:
    def __init__(self, bot):
        self.bot = bot
        self.owner = get(self.bot.get_all_members(), id=self.bot.settings.owner)
        self.answers = dataIO.load_json("data/Tasty/Hunt/answers.json")
        self.riddles = dataIO.load_json("data/Tasty/Hunt/riddles.json")

        #scores start at 0 but "hunt" is also inculded in the "sethunt" cos it is for now
        self.scores = dataIO.load_json("data/Tasty/Hunt/score.json")     

        for users in set(self.bot.get_all_members()):
            try:
                self.scores[users.id]
            except:
                self.scores[users.id] = 0


    async def hunt (self, message):
        #This abuses that lists start at 0
        current_question_index = self.scores[message.author.id]
        if message.content[1:] == self.answers[current_question_index]:
            await self.bot.delete_message(message)
            self.scores[message.author.id]+=1
            await self.bot.send_message(message.author, self.riddles[current_question_index].format(message.author.mention, message.author, self.scores[message.author.id]-1))

        if self.scores[message.author.id]-1 == 10:
            role = discord.utils.get(server.roles, name="Puzzle King/Queen")
            await self.bot.add_roles(member, role)

        if self.scores[message.author.id]-1 == 5:
            role = discord.utils.get(server.roles, name="Puzzle Hunter")
            await self.bot.add_roles(member, role)

        dataIO.save_json("data/Tasty/Hunt/score.json", self.scores)

    @commands.command(name="huntlist", pass_context=True)
    async def hunt_all_users_list(self,ctx):
        user_score_list = []
        for user in set(self.bot.get_all_members()):
            #await self.bot.say(self.scores[user.id]-1)
            user_score_list.append("{}:{}".format(user.name, self.scores[user.id]-1))
            
        msg = "+ User:Score \n {}".format(",\n".join(user_score_list))

        for page in pagify(msg, [" "], shorten_by=21):
            await self.bot.say(box(page.lstrip(" "), lang="diff"))

    @commands.command(name="huntreset", pass_context=True)
    @checks.is_owner()
    async def hunt_reset(self, ctx):
        for user in set(self.bot.get_all_members()):
            self.scores[user.id] = 0
        
        await self.bot.say("Done! reset all")

    @commands.command(name="huntscore", pass_context=True)
    async def hunt_score(self, ctx, member: discord.User):
        await self.bot.say("{}s' score is {}".format(member.name, self.scores[member.id]-1))

    @commands.command(name="huntscoreset", pass_context=True)
    @checks.is_owner()
    async def hunt_score_set(self,ctx, member: discord.user, score):
        await self.bot.say("If this person does not exist someone else with that id will end up with that score")
        try:
            self.scores[member.id] = int(score)+1
            await self.bot.say("Done!")
        except:
            await self.bot.say("An error occurred, Does that person exist? Is that score Valid?")

    @checks.is_owner()
    @commands.command(hidden=True, pass_context=True)
    async def sethunt(self, ctx): #This is a cheat method because the bot will only do it for one 
        await self.bot.send_message(ctx.message.channel, "Re-setting the hunt... please wait")
        await self.bot.send_message(ctx.message.channel, "__**READ CAREFULLY**__ \n\nPlease type `-done` to finish, each message YOU send will be treated as a response.")
        await self.bot.send_message(ctx.message.channel, "")

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

    async def member_join(member):
        self.scores[users.id] = 0
        #This is here to prevent erroring


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

    if not dataIO.is_valid_json("data/Tasty/Hunt/score.json"):
        print("Creating empty score.json...")    
        dataIO.save_json("data/Tasty/Hunt/score.json", {})

def setup(bot):
    check_folders()
    check_files()
    cog = Hunt(bot)
    bot.add_listener(cog.hunt, "on_message")
    bot.add_listener(cog.member_join, "on_member_join")
    bot.add_cog(Hunt(bot))

