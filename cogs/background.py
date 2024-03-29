from asyncio import sleep
from datetime import datetime

from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.ext.commands.cog import Cog
from discord.ext.tasks import loop


class BackgroundTasks(Cog):
    """Background loops"""

    def __init__(self, bot):
        self.bot = bot
        self.save_data.start()
        self.status_change.start()

    @loop(seconds=60)
    async def status_change(self):
        time = datetime.utcnow().strftime("%H:%M")

        if self.bot.inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.config['debug_mode']:
            activity = Activity(
                type=ActivityType.playing,
                name="in DEBUG MODE")

        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{time}/UTC | {self.bot.command_prefix} | {len(self.bot.guilds)}")

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=297.5)
    async def save_data(self):
        print("[VAR: ... Saving, do not quit...", end="\r")
        await sleep(2)
        print("[VAR: !!! Saving, do not quit...", end="\r")

        if self.bot.use_firebase:
            self.bot.database.update(self.bot.user_data)

        else:
            with open("Files/user_data.json", "w") as f:
                user_data = dump(self.bot.user_data, f)

        self.bot.inactive = self.bot.inactive + 1
        time = datetime.now().strftime("%H:%M, %m/%d/%Y")
        print(f"[VAR: {time}] Running.")

    @status_change.before_loop
    async def sc_wait(self):
        await self.bot.wait_until_ready()
        await sleep(30)

    @save_data.before_loop
    async def sd_wait(self):
        await self.bot.wait_until_ready()
        await sleep(15)
    
    def cog_unload(self):
        self.status_change.cancel()
        self.save_data.cancel()


def setup(bot):
    bot.add_cog(BackgroundTasks(bot))