# IMPORTS
from os.path import exists
from sys import exc_info
from copy import deepcopy
from json import load

from discord import __version__, Activity, ActivityType, Intents
from discord.enums import Status
from discord.permissions import Permissions
from discord.utils import oauth_url

from utils.classes import Bot
from utils.errorlog import ErrorLog
from utils.FirebaseDB import FirebaseDB

# NOTES

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
            "Blacklists": ([0], ["placeholder"]),  # ([int(channelID)], [str(prefix)])

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
            "ServerBlacklists": ([0], ["placeholder"]),  # ([int(channelID)], [str(prefix)])
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
        
        "first_time_tip": "👋 It appears to be your first time using this bot!\n"
                          "ℹ️ For more information and help, please visit [this GitHub README](https://github.com/SUPERMECHM500/MWSRam-Outdated#vanity-profile-pics--ram).\n"
                          "ℹ️ For brief legal information, please use the `var:legal` command.\n"
                          "||(If you are recieving this notification again, your data has been reset due to storage issues. Join the support server if you have previous data you want to retain.)||",
        
        "quick_delete_tip": "You just sent your first vanity message!\n"
                            "As you most likely have already seen, the 🗑 emoji appeared under your message for a few seconds. This is for quickly deleting your message.\n"
                            "You may toggle this behavior by running the command `var:quick_del`."
    }
}

INIT_EXTENSIONS = [
    "admin",
    "background",
    "commands",
    "events",
    "help",
    "repl",
    "web"
]

if exists("Workspace/Files/ServiceAccountKey.json"):
    with open("Workspace/Files/ServiceAccountKey.json", "r") as f:
        key = load(f)
else:  # If it doesn't exists assume running on replit
    try:
        from replit import db
        key = dict(db)["SAK"]
    except Exception:
        raise FileNotFoundError("Could not find ServiceAccountKey.json.")

db = FirebaseDB(
    "https://mwsram-database-default-rtdb.firebaseio.com/", 
    fp_accountkey_json=key)

user_data = db.copy()
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

db.update(user_data)

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
)

# If a custom help command is created:
bot.remove_command("help")

print(f"[BOT INIT] Running in: {bot.cwd}\n"
      f"[BOT INIT] Discord API version: {__version__}")

@bot.event
async def on_ready():
    await bot.connect_dbl(autopost=True)

    app_info = await bot.application_info()
    bot.owner = bot.get_user(app_info.owner.id)

    permissions = Permissions()
    permissions.update(
        send_messages=True,
        embed_links=True,
        manage_messages=True,
        manage_webhooks=True,
        add_reactions=True,
        attach_files=True
    )

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
        except Exception as e:
            try:
                print(f"| Failed to load extension {cog}\n|   {type(e.original).__name__}: {e.original}")
            except AttributeError:
                print(f"| Failed to load extension {cog}\n|   {type(e).__name__}: {e}")
            error = exc_info()
            if error:
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