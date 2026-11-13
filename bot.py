import discord
from discord.ext import commands

import json
import os




BotDir = os.path.dirname(os.path.abspath(__file__))

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

        except Exception as e:
            print(f'Error syncing commands: {e}')


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)





#define the bots commands:

@client.tree.command(name="add_check", description="Add a new set of Keywords and Reactions to look for")
@discord.app_commands.describe(
            name="The name of the new Check",
            keywords="The keywords to filter a message for, seperated by ',' e.g. 'Highway, Street, Road'",
            reactions="The reactions that should be applied, seperated by ',' e.g. ':thumbsup:, :thumbsdown:'",
            user="Optional: If the keywords should only be looked for in one users messages",
            channel="Optional: If the keywords should only be looked for in one channel",
            casesensitivity="Optional: If the keywords should be case sensitive (e.g. 'Street' does not react to 'street'), set to True"
            )
async def addcheck(
        interaction: discord.Interaction,
        name: str,
        keywords: str, 
        reactions: str, 
        user: discord.Member |  None=None, 
        channel: discord.TextChannel | None=None,
        casesensitivity: bool = False
        ):
    

    serverid = str(interaction.guild_id)

    #check if a check of this name already exists:
    if interaction.guild_id is None:
        return

    replaced = False

    if serverid in BotData:

        for channeldata, checks in BotData[serverid].items():
            if not checks:
                continue

            #if a check of the name does exist it is deleted and then replaced by the newly added one.
            if name in checks: 
                del BotData[serverid][channeldata][name]
                replaced = True
                break #Since there can only be one check of a name, the loop can end after finding the check


    #add new check:
    if channel != None:
        channelid = str(channel.id)
    else:
        channelid = "Global"

    KeywordArr=[]
    for word in keywords.split(","):
        KeywordArr.append(word.strip()) #Adds every word seperated by , without spaces to the KeywordArr

    ReactionArr=[]
    for word in reactions.split(","):
        ReactionArr.append(word.strip()) #same as KeywordArr

    if user != None:
        userid = user.id
    else:
        userid = -1

    BotData.setdefault(serverid, {}) #Adds a new empty dictionary if the server does not yet have one

    BotData[serverid].setdefault(channelid, {}) #Adds a new empty channel dictionary if the channel/global does not yet have one


    BotData[serverid][channelid][name] = {
            "Keywords": KeywordArr,
            "Reactions": ReactionArr,
            "User": userid,
            "Casesensitive": casesensitivity    
            }

    #save new check into ServerChecks.json
    with open(ServerChecksDir, "w", encoding="utf-8") as data:
        json.dump(BotData, data, indent=4)

    
    if replaced:
        string = "edited"
    else:
        string = "created"

    #send feedback message
    await interaction.response.send_message(f"Check {name} was {string}!")






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

            if details["Casesensitive"]:
                output += "  - case sensitive: yes\n"
            else:
                output += "  - case sensitive: no\n"

            if details["User"] != -1:
                output+=f"  - User: <@{str(details["User"])}>\n"
            output+=f"  - ⇒ {reactions}\n"

        output += "\n"

    await interaction.response.send_message(output, ephemeral=True)



#@client.tree.command(name="view_check", description="View the named checks information")
#@discord.app_commands.describe(
#        Check="The check whichs information should be shown"
#        )
#async def viewcheck(interaction: discord.Interaction, Check: str):
    #implementation




@client.tree.command(name="delete_check", description="Delete the named check")
@discord.app_commands.describe(checkname="The check which should be deleted")
async def viewcheck(interaction: discord.Interaction, checkname: str):
    serverid = str(interaction.guild_id)

    deleted = False

    for channel, checks in BotData[serverid].items():
        for check_name, details in checks.items():
            if check_name == checkname:
                del BotData[serverid][channel][checkname]
                deleted = True
                break

    if deleted:
        await interaction.response.send_message(f"The check {checkname} was deleted.")
    else:
        await interaction.response.send_message(f"The check {checkname} could not be found.")


@client.tree.command(name="help", description="List commands and their descriptions")
async def help(interaction: discord.Interaction):

    await interaction.response.send_message("Currently, the bot supports 4 commands:\n\n### /add_check\nAdds a new check to the bot. If a check of this name already exists on the server, it will be overwritten.\n\nNeeded arguments:\n\nName: The checks name is an arbitrary text string, shown to the user in /list_checks and needed to delete a check in /delete_check.\n\nKeywords: The keywords should include a text of all the words the check is looking for in messages. A check is successfull if all keywords are found. Keywords should be seperated by commas and, optionally spaces, e.g. 'keyword1, keyword2,keyword3'\n\nReactions: The reactions should include a text of all the reactions that should be applied to a message if the check was successfull. Like Keywords, the reactions should be seperated by commas and optionally spaces, e.g. ':wave:,:thumbsup:, :thumbsdown:'\n\n\nOptional arguments:\n\nUser: By default a check is applied to all users of a server. If reactions should only be added to a specific users messages, this user can be chosen here.\n\nChannel: By default a check is applied to all channels of a server the ReactBot can see. If the check should only be applied to a specific channel, this channel can be chosen here.\n\nCaseSensitivity: By default keywords are not case sensitive. This means that a check with the keyword 'keyword1' will still count as successfull if a message includes 'kEywOrD1'. If a checks keywords should be case sensitive, this option can be set to True.\n\n\n### /list_checks\nLists all of the servers currently active checks and what they do. This list is only visible to the commands user.\n\n\n### /delete_check\nDeletes the named check from the server. If no check of this name is found, it will return an error. Otherwise a message visible to everyone will be shown in the channel in which the command was used.\n\nNeeded argument:\nCheckname: The name of the check which should be deleted.\n\n\n### /help\nShows the commands user these descriptions of the commands.", ephemeral=True)



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
                    if details["Casesensitive"]:
                        for word in details["Keywords"]:
                            if word not in message.content:
                                react = False
                            break

                        if react:
                            for reaction in details["Reactions"]:
                                await message.add_reaction(reaction)
                    else:
                        for word in details["Keywords"]:
                            if word.lower() not in message.content.lower():
                                react = False
                            break

                        if react:
                            for reaction in details["Reactions"]:
                                await message.add_reaction(reaction)



#run the bot:
TokenDir = os.path.join(BotDir, "DiscordBotToken")

with open(TokenDir, "r") as token:
    client.run(token.read())
