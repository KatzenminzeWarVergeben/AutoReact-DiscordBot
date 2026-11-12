import discord
from discord.ext import commands

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
            Channel="Optional: If the keywords should only be looked for in one channel"
            )
async def addcheck(
        interaction: discord.Interaction,
        Name: str,
        Keywords: str, 
        Reactions: str, 
        User: discord.Member |  None, 
        Channel: discord.TextChannel | None
        ):
    #implementation




@client.tree.command(name="list_checks", description="List all checks currently active on the server")
async def listchecks(interaction: discord.Interaction):
        #implementation




@client.tree.command(name="view_check", description="View the named checks information")
@discord.app_commands.describe(
        Check="The check whichs information should be shown"
        )
async def viewcheck(interaction: discord.Interaction, Check: str):
    #implementation




@client.tree.command(name="delete_check", description="Delete the named check")
@discord.app_commands.describe(Check="The check which should be deleted")
async def viewcheck(interaction: discord.Interaction, Check: str):
    #implementation





#look for messages to apply the checks
@client.event
async def on_message(message):
    #implementation




#run the bot:
with open("DiscordBotToken", "r") as token:
    client.run(token.read())
