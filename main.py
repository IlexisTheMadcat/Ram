# IMPORTS
from os.path import exists
from sys import exc_info
from copy import deepcopy
from json import load

from discord import __version__, Activity, ActivityType, Intents
from discord.enums import Status
from discord.permissions import Permissions
from discord.utils import oauth_url
from discord.ext.commands import ExtensionAlreadyLoaded

from utils.classes import Bot
from utils.errorlog import ErrorLog
from utils.FirebaseDB import FirebaseDB

# Using discord.py==1.7.x


DATA_DEFAULTS = {
    "UserData": {
        "UID": {
            "Settings": {  # User Settings dict
                "NotificationsDue": {
                    "FirstTime": False,
                    "QuickDeleteTip": False
                },  # {str(name):bool}
                # A notification sent to users when they use a command for the first time.
                # These are set to true after being executed. Resets by command.

                # Whether or not the user wants to use the quick delete feature.
                "QuickDelete": True
            },
            "VanityAvatars": {
                "guildID": [
                    "https://example.com/image2.png",  # str(imageURL) or None ; Current vanity
                    "https://example.com/image1.png",  # str(imageURL) or None ; Previous vanity 
                ]
            },

            # Messages sent in channels whose IDs are in the first list are ignored.
            # Messages sent that start with any element in the second list are ignored.
            "Blacklists": {
                "guildID": [[0], ["placeholder"]]  # ([int(channelID)], [str(prefix)])
            },

            # A library of up to 10 closet entries locked by top.gg voting.
            # These are global and can be accessed cross-server.
            "Closet": {"placeholder":"placeholder"}  # {str(name): str(imageURL)}
        }
    },
    
    # Only users with certain permissions may modify this.
    "GuildData": {
        "GID": {
            "Settings": {
                
            },
            "ServerBlacklists": [[0], ["placeholder"]],  # ([int(channelID)], [str(prefix)])
            "BlockedUsers": [0]  # [int(userID)]
        }
    },

    # Stores webhooks and respective channel IDs for easy access.
    "Webhooks": {"placeholder":"placeholder"},  # {str(channelID): str(webhookID)}

    "Tokens": {
        "BOT_TOKEN":"xxx",
        "DBL_TOKEN":"xxx"
    },
    
    "config": {
        "debug_mode": False, 
        # Print exceptions to stdout.
        
        "error_log_channel": 734499801697091654,
        # The channel that errors are sent to. 
        
        "first_time_tip": 
"""👋 It appears to be your first time using this bot, but I have bad news. I won't live much longer. Here's the developer's note:
---
@everyone I have decided on `Vanity Avatars || Ram`'s fate.
Her functions are vastly superseded by the default Discord client and Tupperbox's abilities. Not only can it "autoproxy", which runs every message as a specific tupper, it can have multiple tuppers, completely eliminating the need for a `var:closet`. And that command requires voting, some people would just find that annoying when a better bot is available for free. Also, I created the bot before "autoproxy" and "server profiles" were available, and I am not known widely enough to keep this bot running.
That all being said, Ram will remain online for a little bit longer to allow people to migrate their data to Tupperbox.

The date that Ram will become permanently offline will be on November 7th, 2021.

With that all being said, I am still actively updating `NReader` when there are issues and things I want to add, since no other bot exists like it. I want to thank Alexandre Ramos for making the project possible.
If you are a person that enjoys reading hentai, but don't want to visit any sketchy websites, this bot is for you. To put it in laymen's terms, I'm basically doing all that work over the internet to bring that content to you, in a more customizable way. You can look up doujins by ID, search doujins using specific terms, read them IN DISCORD, and even add doujins to your own customizable library. If you have questions, don't hesitate to ask. 
---
You can join the support server here to check out NReader: [MechHub](https://discord.gg/DJ4wdsRYy2)
""",
        "quick_delete_tip": "You just sent your first vanity message!\n"
                            "As you most likely have already seen, the <:delete_message_icon:850772261773770782> emoji appeared under your message for a few seconds. This is for quickly deleting your message.\n"
                            "You may toggle this behavior by running the command `var:quick_del`. To delete your message after this short period, react with :x:."
    }
}

INIT_EXTENSIONS = [
    "admin",
    "background",
    "commands",
    "events",
    "help",
    "repl",
    # "web"
]

# 0 = use JSON
# 1 = use Firebase
DATA_CLOUD = 1

if DATA_CLOUD:
    if exists("Files/ServiceAccountKey.json"):
        key = load(open("Files/ServiceAccountKey.json", "r"))
    else:  # If it doesn't exists assume running on replit
        try:
            from replit import db
            key = dict(db["SAK"])
        except Exception:
            raise FileNotFoundError("Could not find ServiceAccountKey.json.")

    db = FirebaseDB(
        "https://mwsram-database-default-rtdb.firebaseio.com/", 
        fp_accountkey_json=key)

    user_data = db.copy()

else:
    with open("Files/user_data.json", "r") as f:
        db = None
        user_data = load(f)


# Check the database
for key in DATA_DEFAULTS:
    if key not in user_data:
        user_data[key] = DATA_DEFAULTS[key]
        print(f"[MISSING VALUE] Data key '{key}' missing. "
              f"Inserted default '{DATA_DEFAULTS[key]}'")
found_data = deepcopy(user_data)  # Duplicate to avoid RuntimeError exception
for key in found_data:
    if key not in user_data:
        user_data.pop(key)  # Remove redundant data
        print(f"[REDUNDANCY] Invalid data \'{key}\' found. "
              f"Removed key from file.")
del found_data  # Remove variable from namespace

config_data = user_data["config"]
# Check the bot config
for key in DATA_DEFAULTS['config']:
    if key not in config_data:
        config_data[key] = DATA_DEFAULTS['config'][key]
        print(f"[MISSING VALUE] Config '{key}' missing. "
              f"Inserted default '{DATA_DEFAULTS['config'][key]}'")
found_data = deepcopy(config_data)  # Duplicate to avoid RuntimeError exception
for key in found_data:
    if key not in DATA_DEFAULTS['config']:
        config_data.pop(key)  # Remove redundant data
        print(f"[REDUNDANCY] Invalid config \'{key}\' found. "
              f"Removed key from file.")
del found_data  # Remove variable from namespace

if DATA_CLOUD:
    db.update(user_data)
else:
    with open("Files/user_data.json", "w") as f:
        dump(user_data, f)

intents = Intents.default()
intents.presences = True

bot = Bot(
    description="Create server-specific avatars.",
    owner_ids=[331551368789622784],  # Ilexis
    status=Status.idle,
    activity=Activity(type=ActivityType.playing, name="with the mirror."),
    command_prefix="var:",
    
    config=config_data,
    database=db,
    user_data=user_data,   
    defaults=DATA_DEFAULTS,
    auth=db["Tokens"],
    use_firebase=DATA_CLOUD
)

# If a custom help command is created:
bot.remove_command("help")

print(f"[BOT INIT] Running in: {bot.cwd}\n"
      f"[BOT INIT] Discord API version: {__version__}")

@bot.event
async def on_ready():
    await bot.connect_dbl(autopost=True)

    app_info = await bot.application_info()
    bot.owner = app_info.owner

    permissions = Permissions()
    permissions.update(
        send_messages=True,
        embed_links=True,
        manage_messages=True,
        manage_webhooks=True,
        add_reactions=True)

    # Add the ErrorLog object if the channel is specified
    if bot.config["error_log_channel"]:
        error_channel = await bot.fetch_channel(bot.config["error_log_channel"])
        bot.errorlog = ErrorLog(bot, error_channel)

    print("\n"
          "#-------------------------------#\n"
          "| Loading initial cogs...\n"
          "#-------------------------------#")

    for cog in INIT_EXTENSIONS:
        try:
            bot.load_extension(f"cogs.{cog}")
            print(f"| Loaded initial cog {cog}")
        except ExtensionAlreadyLoaded:
            continue
        
        except Exception as e:
            if hasattr(e, "original"):
                print(f"| Failed to load extension {cog}\n|   {type(e.original).__name__}: {e.original}")
            else:
                print(f"| Failed to load extension {cog}\n|   {type(e).__name__}: {e}")
            
            error = exc_info()
            if e:
                await bot.errorlog.send(error, event="Load Initial Cog")

    print(f"#-------------------------------#\n"
          f"| Successfully logged in.\n"
          f"#-------------------------------#\n"
          f"| User:      {bot.user}\n"
          f"| User ID:   {bot.user.id}\n"
          f"| Owner:     {bot.owner}\n"
          f"| Guilds:    {len(bot.guilds)}\n"
          f"| OAuth URL: {oauth_url(app_info.id, permissions)}\n"
          f"#------------------------------#\n")

if __name__ == "__main__":
    bot.run()