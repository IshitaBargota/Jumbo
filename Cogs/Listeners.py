import discord
from discord.ext import commands
import asyncio
from Database.db_files import firebase
from helpEmbeds import HelpEmbeds
from datetime import datetime
default_prefix = "j!"

class CommandDisabled(commands.CheckFailure):
    pass
class AllListeners(commands.Cog):
    def __init__(self,bot,difficulty,lvl_add):
        self.bot = bot
        self.difficulty = difficulty
        self.lvl_add = lvl_add
    
    def check_enabled(ctx):
        db = firebase.database()
        isEnabled = db.child('Disabled').child(str(ctx.guild.id)).child(ctx.command).get()
        if isEnabled.val() is None:
            return isEnabled.val() is None
        else:
            raise CommandDisabled
            return isEnabled.val() is None
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Everyone Fight"))
        print('Logged in as {0.user}'.format(self.bot))
        await self.bot.get_channel(826719835630338058).send('Logged in as {0.user}'.format(self.bot))
     
    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        db = firebase.database()
        db.child('Prefixes').child(str(guild.id)).set({'Prefix':default_prefix})
        em = discord.Embed(title="Hola Nabs, I am Jumbo",description="""
        **Jumbo is a fun bot... use it to have fun with ur friends in the same server.**

        It also has many utility commands such as afk,dm,autreact. There are also fun commands.
        Don't forget levelling.... Jumbo also has a levelling system to check who's active or who's not.

        Default Prefix : `j!` (Mention to know the prefix of your server)
    
        Use *help <command> for extended information on a command
    
        [** •Invite me**](https://discord.com/api/oauth2/authorize?client_id=805430097426513941&permissions=469822528&scope=bot "Add the bot to your server")
        
        """,color=discord.Color.random()
        
        )

        for channel in guild.text_channels:
            if "general" in channel.name:
                await channel.send(embed=em)
                break
        emb = discord.Embed(title='Jumbo joined a guild.',color=discord.Color.random(),thumbnail=f'{guild.icon_url}')
        emb.add_field(name='Guild Name',value=f'`{guild.name}`')
        emb.add_field(name='Guild ID',value=f'`{guild.id}`')
        emb.add_field(name='Guild owner',value=f'`{guild.owner}`')
        emb.add_field(name='No. of members',value=f'`{guild.member_count}`')
        emb.add_field(name='Joined on',value=f'`{datetime.utcnow()}`')
        emb.add_field(name='Guild created at',value=f'{guild.created_at}')
        await self.bot.get_channel(826719835630338058).send(embed=emb)
    @commands.Cog.listener()
    async def on_member_join(self,member):
        #print('yes')
        for channel in member.server.channels:
            if str(channel) == "general":
                await client.send_message(f'Hello {member.mention}')
                break
    @commands.Cog.listener()
    async def on_message(self,message):
        db = firebase.database()
        try:
            prefix_data = db.child('Prefixes').child(str(message.guild.id)).get()
        except:
            pass
        nsfw = ['fuck off','fk',"fuck u","fk u","f","fuck","wtf"]
        if str(message.content).lower() in nsfw and message.author != self.bot.user:
            await message.channel.send(f"**{message.author.mention} U Fuck off BITCH........smh** :face_with_symbols_over_mouth:")
        if "shit" in str(message.content).lower():
            await message.channel.send(f"**{message.author.mention} :poop: Put it in your mouth..... LMAO**")
        if message.author != self.bot.user:
            if message.raw_mentions:
                for i in message.raw_mentions:
                    afk_data = db.child("AFK").child(str(message.guild.id)).child(str(i)).get()

            try:
                for i in message.raw_mentions:
                    reaction_data =  db.child('Reactions').child(str(message.guild.id)).child(str(i)).get()
                    await message.add_reaction(reaction_data.val()['Reaction'])
            except:
                pass
            try:
                reason = afk_data.val()["reason"]
                em = discord.Embed(title=f"User AFK",description=f"The Mentioned user is AFK....... **Reason: {reason}**",color=discord.Color.from_rgb(255,20,147))
                await message.channel.send(message.author.mention,embed=em)
            except:
                pass
            if message.content.startswith(prefix_data.val()['Prefix']):
                return
            elif str(self.bot.user.id) in message.content:
                em = (discord.Embed(description=f"Yo! My prefix here is `{prefix_data.val()['Prefix']}`. You can use `{prefix_data.val()['Prefix']}help` for more information",color=discord.Color.random()))
                await message.channel.send(embed = em)
            else:
                if not message.author.bot:
                    data = db.child("Levels").child(str(message.guild.id)).child(str(message.author.id)).get()
                    
                            
                    if data.val() is None:
                        newUser = {"userName":str(message.author),"lvl":1,"exp":1}
                        db.child("Levels").child(str(message.guild.id)).child(str(message.author.id)).set(newUser)
                    elif data.val() is not None:
                        exp = data.val()['exp']
                        lvl = data.val()['lvl']
                        exp += self.lvl_add
                        
                        a = self.difficulty+(lvl-1)*self.difficulty
                        mention = message.author.mention
                        if exp >= a:
                            lvl += 1
                            lvl_embed = (discord.Embed(title="**Level Up**",
                            description= f"Congratulations {mention}. You just reached level {lvl}",
                            color = discord.Color.from_rgb(0,255,185)
                            )
                            .set_thumbnail(url=f"{message.author.avatar_url}")
                            )
                            await message.channel.send(mention,embed=lvl_embed)
                        db.child("Levels").child(str(message.guild.id)).child(str(message.author.id)).update({"exp":exp,"lvl":lvl})
                    await asyncio.sleep(2)
                else:
                    pass
        await self.bot.process_commands(message)
    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        db = firebase.database()
        prefix_data = db.child('Prefixes').child(str(ctx.guild.id)).get()
        pre = prefix_data.val()["Prefix"]
        if isinstance(error,commands.CommandNotFound):
            em = discord.Embed(title="Command not found",description=f"{error}..... use `{pre}help` for info on commands.")
            await ctx.send(embed=em)
        elif isinstance(error,commands.BotMissingPermissions):
            pass
        elif isinstance(error, CommandDisabled):
            em = discord.Embed(description="This command is disabled in your server. Ask admin to enable it",color=discord.Color.random())
            await ctx.send(embed=em)
        else:
            pass
            # if 'The check functions for command failed.' in str(error):
            #     #print('yes')
            #     em = discord.Embed(description="This command is disabled in your server. Ask admin to enable it",color=discord.Color.random())
            #     await ctx.send(embed=em)