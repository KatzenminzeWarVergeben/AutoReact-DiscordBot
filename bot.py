import discord
from discord.ext import commands

import json
import os




BotDir= os.path.dirname(os.path.abspath(__file__))

ServerChecksDir = os.path.join(BotDir, "ServerChecks.json")

if os.path.exists(ServerChecksDir):
    with open(ServerChecksDir, "r", encoding="utf-8") as data:
        BotData = json.load(data)

else:
    BotData = {}



class Client(commands.Bot):
    async def on_ready(self):
        print(f'logged on as {self.user}!')

        #Synchronizes (or tries to) all commands from below to the servers with the bot on it 
        try:
            synced = await self.tree.sync()

            print(f'Synced {len(synced)} commands!')

        except Exception:
            print(f'Error syncing commands: {Exception}')


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)




#define the bots commands:

@client.tree.command(name="add_check", description="Add a new set of Keywords and Reactions to look for")
@discord.app_commands.describe(
            Name="The name of the new Check",
            Keywords="The keywords to filter a message for, seperated by ',' e.g. 'Highway, Street, Road'",
            Reactions="The reactions that should be applied, seperated by ',' e.g. ':thumbsup:, :thumbsdown:'",
            User="Optional: If the keywords should only be looked for in one users messages",
            Channel="Optional: If the keywords should only be looked for in one channel",
            CaseSensitive="Optional: If the keywords should be case sensitive (e.g. 'Street' does not react to 'street'), set to True"
            )
async def addcheck(
        interaction: discord.Interaction,
        Name: str,
        Keywords: str, 
        Reactions: str, 
        User: discord.Member |  None=None, 
        Channel: discord.TextChannel | None=None,
        CaseSensitivity: bool = False
        ):
    
    #add new check 

    serverid = str(interaction.guild_id)

    if Channel != None:
        channelid = str(Channel.id)
    else:
        channelid = "Global"

    KeywordArr=[]
    for word in Keywords.split(","):
        KeywordArr.append(word.strip()) #Adds every word seperated by , without spaces to the KeywordArr

    ReactionArr=[]
    for word in Reactions.split(","):
        ReactionArr.append(word.strip()) #same as KeywordArr

    if User != None:
        userid = User.id
    else:
        userid = -1

    BotData.setdefault(serverid, {}) #Adds a new empty dictionary if the server does not yet have one

    BotData[serverid].setdefault(channelid, {}) #Adds a new empty channel dictionary if the channel/global does not yet have one


    BotData[serverid][channelid][Name] = {
            "Keywords": KeywordArr,
            "Reactions": ReactionArr,
            "User": userid,
            "Casesensitive": CaseSensitivity    
            }

    #save new check into ServerChecks.json
    with open(ServerChecksDir, "w", encoding="utf-8") as data:
        json.dump(BotData, data, indent=4)

    
    #send feedback message
    await interaction.response.send_message(f"Check {Name} was saved!", ephemeral=True)






@client.tree.command(name="list_checks", description="List all checks currently active on the server")
async def listchecks(interaction: discord.Interaction):
    serverid = str(interaction.guild_id)
    output=""

    for channel, checks in BotData[serverid].items():

        if not checks:  #dont write channel names without checks in them into the output
            continue

        if channel == "Global":
            output+= "**Global:**\n"
        
        else:
            output+= f"<#{channel}>:\n" 

        
        for checkname, details in checks.items():
            keywords = ", ".join(details["Keywords"])
            reactions = ", ".join(details["Reactions"])

            output+= f"- {checkname}:\n  - Keywords:{keywords}\n"
            if details["User"] != -1:
                output+=f"  - User: <@{str(details["User"])}\n"
            output+="- - ⇒ {reactions}\n"

        output += "\n"

    await interaction.response.send_message(output, ephemeral=True)



#@client.tree.command(name="view_check", description="View the named checks information")
#@discord.app_commands.describe(
#        Check="The check whichs information should be shown"
#        )
#async def viewcheck(interaction: discord.Interaction, Check: str):
    #implementation




@client.tree.command(name="delete_check", description="Delete the named check")
@discord.app_commands.describe(Checkname="The check which should be deleted")
async def viewcheck(interaction: discord.Interaction, Checkname: str):
    serverid = interaction.guild_id

    deleted = False

    for channel, checks in BotData[serverid].items():
        for checkname in checks.items():
            if checkname == Checkname:
                del BotData[serverid][channel][checkname]
                deleted = True
                break

    if deleted:
        await interaction.response.send_message(f"The check {Checkname} was deleted.")
    else:
        await interaction.response.send_message(f"The check {Checkname} could not be found.")





#look for messages to apply the checks
@client.event
async def on_message(message:discord.Message):
    
    #Bot doesnt check its own messages
    if message.author == client.user:
        return 

    #Bot doesnt react to direct messages
    if message.guild == None: 
        return

    serverid = str(message.guild.id)
    #doesnt continue if server has no checks yet
    if serverid not in BotData:
        return
    channelid = str(message.channel.id)

    for channel, checks in BotData[serverid].items(): 
        if not checks: #dont look for checks in empty channels
            continue

        if channel == "Global" or channel == channelid:
            for check, details in checks.items():
                if message.author.id == details["User"] or details["User"] == -1:
                    react = True
                    for word in details["Keywords"]:
                        if word not in message.content:
                            react = False
                            break

                        if react:
                            for reaction in details["Reactions"]:
                                await message.add_reaction(reaction)


#run the bot:
with open("DiscordBotToken", "r") as token:
    client.run(token.read())
