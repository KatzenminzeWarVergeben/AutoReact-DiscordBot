# AutoReact-DiscordBot
A Bot allowing you to specify a set of Keywords and Reactions (A "Check"). If a message includes all keywords of a check, the checks reactions will be applied. Optionally checks can also be limited to channels, users and case sensitivity of the keywords.

## Setup
### 1. Download this repository
Specifically, you'll need the bot.py and a "DiscordBotToken" file in the same directory.

A ServerChecks.json should be added automatically on startup of the bot.

### 2. Create a discord application
Go to https://discord.com/developers/applications

Click on "New Application" and give it a name of your liking

In the "Overview" Tab on the left, go to "Installation"

Under "Installation Contexts" check "Guild Install", uncheck "User Install"

Under "Bot" click "Reset Token", then save the newly created token into the DiscordBotToken file from step 1. 

Go to "Privileged Gateway Intents" and check "Message Content Intent"

Lastly, invite the created bot to your server.


To function, the bot needs the following Bot Permissions: View Channels, Send Messages, Read Message History, Add Reactions


### 3. Run the Bot
Run the bot in a python environment including discord.py: https://pypi.org/project/discord.py/

Alternatively, discord.py can also be downloaded using Anaconda: https://anaconda.org/channels/conda-forge/packages/discord.py/overview


## Usage
Currently, the bot supports 4 commands:

### /add_check
Adds a new check to the bot. If a check of this name already exists on the server, it will be overwritten.

Needed arguments:

Name: The checks name is an arbitrary text string, shown to the user in /list_checks and needed to delete a check in /delete_check.

Keywords: The keywords should include a text of all the words the check is looking for in messages. A check is successfull if all keywords are found. Keywords should be seperated by commas and, optionally spaces, e.g. "keyword1, keyword2,keyword3". 
If the keyword text field only includes commas, like "," or ",,,", the check will always be successfull, meaning that the checks reactions are applied to every message.

Reactions: The reactions should include a text of all the reactions that should be applied to a message if the check was successfull. Like Keywords, the reactions should be seperated by commas and optionally spaces, e.g. ":wave:,:thumbsup:, :thumbsdown:"


Optional arguments:

User: By default a check is applied to all users of a server. If reactions should only be added to a specific users messages, this user can be chosen here.

Channel: By default a check is applied to all channels of a server the ReactBot can see. If the check should only be applied to a specific channel, this channel can be chosen here.

CaseSensitivity: By default keywords are not case sensitive. This means that a check with the keyword "keyword1" will still count as successfull if a message includes "kEywOrD1". If a checks keywords should be case sensitive, this option can be set to True.

ReactPerKeyword: By default, all keywords of a check must be true to make the check successfull. If this option is set to true, this is instead changed to reactions per keyword, meaning using the keywords "street, highway" will react if either street or highway or both are part of the message.


### /list_checks
Lists all of the servers currently active checks and what they do. This list is only visible to the commands user.

Optional Argument:
Channel: If a channel is given, the list will only include global checks and the given channels checks.


### /delete_check
Deletes the named check from the server. If no check of this name is found, it will return an error. Otherwise a message visible to everyone will be shown in the channel in which the command was used.

Needed argument:
Checkname: The name of the check which should be deleted.

### /delete_all_checks
Deletes all global checks of the server. After entering the command it will ask for comfirmation to make sure that it wasn't executed accidentally. 

Optional Argument:
Channel: If a channel is given, the command will delete all checks of this channel instead of deleting all global checks.
