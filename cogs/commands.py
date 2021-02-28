# import os
# from asyncio import sleep
# from asyncio.exceptions import TimeoutError
# from textwrap import shorten
# from contextlib import suppress

# from discord import Forbidden
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import (
    has_permissions, 
    bot_has_permissions, 
    command
)

from utils.classes import ModdedEmbed as Embed

class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="command")
    @has_permissions(send_messages=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def command(self, ctx, arg1: str):
        await ctx.send(embed=Embed(description = arg1))


def setup(bot):
    bot.add_cog(Commands(bot))
