from discord import AppInfo, Permissions
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command
from discord.utils import oauth_url

from utils.classes import ModdedEmbed as Embed

class MiscCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def invite(self, ctx: Context):
        """Sends an OAuth bot invite URL"""

        app_info: AppInfo = await self.bot.application_info()
        permissions = Permissions()
        permissions.update(
            # Permission kwargs
        )

        emb = Embed(
            title=f'Invite {self.bot.user.name}',
            description=f'[Click Here]({oauth_url(app_info.id, permissions)}) '
                        f'to invite this bot to your server.\n'
        ).set_author(
            name=self.bot.user.name,
            url=None,
            icon_url=self.bot.user.avatar_url
        ).set_footer(
            text="Provided by MechHub Bot Factory")
        
        await ctx.send(embed=emb)

    @command(name="help", aliases=["h"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def bhelp(self, ctx):
        emb = Embed(
            description="""
**Bot Overview.**
**Support server: [MechHub/DJ4wdsRYy2](https://discord.gg/DJ4wdsRYy2)**

__`command/alias <arg> [opt]`__
*Command Description.*
ー Notes
"""
        ).add_field(
            inline=False,
            name="Misc Commands",
            value="""
__`help`__
*Shows this message.*

__`privacy/pcpl/terms/tos/legal`__
*Shows the Privacy Policy and Terms of Service for Mechhub Bot Factory.*

__`invite`__
*Sends this bot's invite url with all permissions listed under Required Permissions.*
"""
        ).add_field(
            inline=False,
            name="Required Permissions",
            value="""
\- Permission 
\- *Key Permission
"""
        ).set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar_url
        ).set_footer(
            text="Provided by MechHub Bot Factory")
        
        await ctx.send(embed=emb)
    
    @command(name="privacy", aliases=["pcpl", "terms", "tos", "legal"])
    @bot_has_permissions(
        send_messages=True, 
        embed_links=True)
    @bot_has_permissions(
        send_messages=True, 
        embed_links=True)
    async def legal(self, ctx):
        # Fetch document from one location
        channel = await self.bot.fetch_channel(815473015394926602)
        message = await channel.fetch_message(815473545307881522)
        await ctx.send(embed=Embed(
            title="Legal Notice",
            description=message.content
        ).set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        ).set_footer(
            text="Provided by MechHub Bot Factory"
        ))

def setup(bot):
    bot.add_cog(MiscCommands(bot))
