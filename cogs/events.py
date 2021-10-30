# IMPORTS
from asyncio import sleep, TimeoutError
from contextlib import suppress
from sys import exc_info
from copy import deepcopy

import topgg
from timeit import default_timer
from discord import Webhook, Message
from discord.errors import Forbidden, NotFound, HTTPException, DiscordServerError
from discord.utils import get
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.errors import (
    BotMissingPermissions,
    CommandNotFound,
    MissingPermissions,
    MissingRequiredArgument,
    NotOwner, BadArgument,
    CheckFailure, CommandOnCooldown)

from utils.classes import Bot, ModdedEmbed as Embed
from utils.utils import (
    EID_FROM_INT,
    create_engraved_id_from_user,
    get_engraved_id_from_msg)


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # Message events
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_dbl_vote(data):
        """An event that is called whenever someone votes for the bot on Top.gg."""
        if data["type"] == "test":
            # this is roughly equivalent to
            # `return await on_dbl_test(data)` in this case
            print(data)

        print(f"Received a vote:\n{data}")

    @Cog.listener()
    async def on_message(self, msg: Message):
        # Cooldown
        if msg.author.id in self.bot.global_cooldown or msg.author.id in self.bot.pause_on_message: return
        else: self.bot.global_cooldown.update({msg.author.id:"placeholder"})
        
        # Vanity message
        if msg.author.bot and msg.author.discriminator == "0000":
            engravedid = get_engraved_id_from_msg(msg.content)
            if engravedid:
                eid_user = await self.bot.fetch_user(engravedid)
                if eid_user:
                    if self.bot.user_data["UserData"][str(eid_user.id)]["Settings"]["QuickDelete"]:
                        with suppress(Forbidden):
                            await msg.add_reaction("<:delete_message_icon:850772261773770782>")
                        
                        if not self.bot.user_data["UserData"][str(eid_user.id)]["Settings"]["NotificationsDue"]["QuickDeleteTip"]:
                            with suppress(Forbidden):
                                await eid_user.send(embed=Embed(
                                    title="Quick Delete Notification",
                                    description=self.bot.config["quick_delete_tip"]))
                        
                        self.bot.user_data["UserData"][str(eid_user.id)]["Settings"]["NotificationsDue"]["QuickDeleteTip"] = True

                        await sleep(5)
                        with suppress(NotFound):
                            await msg.remove_reaction("<:delete_message_icon:850772261773770782>", msg.guild.me)
            return

        # Don't respond to bots.
        if msg.author.bot:
            return

        verify_command = await self.bot.get_context(msg)
        if msg.guild and not verify_command.valid:
            # Self-Blacklisted
            try:
                try:
                    for i in self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][1]:
                        if msg.content.startswith(i):
                            return

                    if msg.channel.id in self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][0]:
                        return

                    if msg.channel.category and msg.channel.category.id in self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][0]:
                        return

                except IndexError:
                    if isinstance(self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][0][0], int):
                        self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"].update({
                            str(msg.guild.id):[self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][0], ["placeholder"]]
                        })

                    elif isinstance(self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][0][0], str):
                        self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"].update({
                            str(msg.guild.id):[[0], self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"][str(msg.guild.id)][0]]
                        })
                    else:
                        self.bot.user_data["UserData"][str(msg.author.id)]["Blacklists"].update({
                            str(msg.guild.id):[[0], ["placeholder"]]
                        })

            except KeyError:
                pass

            # Server-Blacklisted
            try:
                try:
                    for i in self.bot.user_data["GuildData"][str(msg.guild.id)]["ServerBlacklists"][1]:
                        if msg.content.startswith(i):
                            return

                    if msg.channel.id in self.bot.user_data["GuildData"][str(msg.guild.id)]["ServerBlacklists"][0]:
                        return
                
                    if msg.channel.category and msg.channel.category.id in self.bot.user_data["GuildData"][str(msg.guild.id)]["ServerBlacklists"][0]:
                        return
                
                except KeyError:
                    if isinstance(self.bot.user_data["GuildData"][str(msg.author.id)]["ServerBlacklists"][0], int):
                        self.bot.user_data["GuildData"][str(msg.author.id)].update({
                            "ServerBlacklists":[self.bot.user_data["GuildData"][str(msg.author.id)]["ServerBlacklists"][0], ["placeholder"]]
                        })

                    elif isinstance(self.bot.user_data["GuildData"][str(msg.author.id)]["ServerBlacklists"][0], str):
                        self.bot.user_data["GuildData"][str(msg.author.id)].update({
                            "ServerBlacklists":[[0], self.bot.user_data["GuildData"][str(msg.author.id)]["ServerBlacklists"][0]]
                        })
                    else:
                        self.bot.user_data["GuildData"][str(msg.author.id)].update({
                            "ServerBlacklists":[[0], ["placeholder"]]
                        })

            except KeyError:
                pass

            # Get attachments
            start = default_timer()
            attachment_files = []
            for i in msg.attachments:
                try:
                    dcfileobj = await i.to_file()
                    attachment_files.append(dcfileobj)
                except Exception as e:
                    print("[Error while getting attachment]", e)
                    continue

            try:
                if not msg.author.bot and self.bot.user_data["UserData"][str(msg.author.id)]["VanityAvatars"][str(msg.guild.id)][0]:
                    engravedid = create_engraved_id_from_user(msg.author.id)

                    if msg.content != "":
                        new_content = f"{msg.content}{engravedid}"
                    else:
                        new_content = EID_FROM_INT[10] + engravedid

                    bot_perms = msg.channel.permissions_for(msg.guild.me)
                    if not all((
                        bot_perms.manage_messages,
                        bot_perms.manage_webhooks)):
                        await msg.author.send(
                            f"Your message couldn't be transformed because I am "
                            f"missing 1 or more permissions listed in "
                            f"`{self.bot.command_prefix}help` under `Required Permissions`.\n"
                            f"If you keep getting this error, remove your "
                            f"vanity avatar or blacklist the channel you are "
                            f"trying to use it in.")

                        del start
                        return
                    
                    else:
                        webhooks = await msg.channel.webhooks()
                        webhook = get(webhooks, id=self.bot.user_data["Webhooks"].get(str(msg.channel.id)))
                        if webhook is None:
                            webhook: Webhook = await msg.channel.create_webhook(name="Vanity Profile Pics")
                            self.bot.user_data["Webhooks"][str(msg.channel.id)] = webhook.id

                        try:
                            await msg.delete()
                            await webhook.send(
                                new_content,
                                files=attachment_files,
                                avatar_url=self.bot.user_data["UserData"][str(msg.author.id)]["VanityAvatars"][str(msg.guild.id)][0],
                                username=msg.author.display_name)
                        
                        except Exception:
                            await msg.author.send("I failed to transform your message, please use the `var:set` command again with a proper url.")
                            del start
                            return

                        if not self.bot.user_data["UserData"][str(msg.author.id)]["Settings"]["NotificationsDue"]["FirstTime"]:
                            with suppress(Forbidden):
                                await msg.author.send(embed=Embed(
                                    title="First Time Interaction Notification",
                                    description=self.bot.config["first_time_tip"]))
                        
                        self.bot.inactive = 0
                        stop = default_timer()

                    comptime = round(stop-start, 3)
                    print(f"[VAR] Response delay {str(comptime).ljust(5)}s from {msg.author} ({msg.author.id}).")

                    self.bot.inactive = 0

                else:
                    return

            except KeyError:
                return

        # Checks if the message is any attempted command.
        if msg.content.startswith(self.bot.command_prefix) and not msg.content.startswith(self.bot.command_prefix+" "):
            if str(msg.author.id) not in self.bot.user_data["UserData"]:
                self.bot.user_data["UserData"][str(msg.author.id)] = deepcopy(self.bot.defaults["UserData"]["UID"])
            if "GuildData" in self.bot.defaults and msg.guild and str(msg.guild.id) not in self.bot.user_data["GuildData"]:
                self.bot.user_data["GuildData"][str(msg.guild.id)] = deepcopy(self.bot.defaults["GuildData"]["GID"])

            if not self.bot.user_data["UserData"][str(msg.author.id)]["Settings"]["NotificationsDue"]["FirstTime"]:
                with suppress(Forbidden):
                    await msg.author.send(embed=Embed(
                        title="First Time Interaction Notification",
                        description=self.bot.config["first_time_tip"]))
                
                self.bot.user_data["UserData"][str(msg.author.id)]["Settings"]["NotificationsDue"]["FirstTime"] = True

            self.bot.inactive = 0
        
            await self.bot.process_commands(msg)
            return

    # Deleting/Inquiring a message
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)
            ctx = await self.bot.get_context(message)
        except (NotFound, Forbidden, DiscordServerError):
            return
        
        if not ctx.guild:
            return

        if user == self.bot.user:
            return

        if str(payload.emoji) in ["❌", "<:delete_message_icon:850772261773770782>"] and \
            ctx.author.bot and \
            ctx.author.discriminator == "0000":
            engravedid = get_engraved_id_from_msg(message.content)
            if engravedid:
                identification = await self.bot.fetch_user(engravedid)
            else:
                return

            member = await ctx.guild.fetch_member(user.id)
            permissions = member.permissions_in(channel)

            # Check if the message belongs to the reaction user, or if they have `Manage Messages` permission.
            if (identification == user or permissions.manage_messages) and user.id != self.bot.user.id:
                try:
                    await ctx.message.delete()
                    return
                
                except Forbidden:
                    with suppress(HTTPException, Forbidden):
                        await user.send('If you want to do that, this bot needs the "Manage Messages" permission.')
                        return
        
        elif str(payload.emoji) == "📝" and \
            ctx.author.bot and \
            ctx.author.discriminator == "0000":
            userid = get_engraved_id_from_msg(message.content)
            if userid:
                identification = await self.bot.fetch_user(userid)
            else:
                return

            webhooks = await ctx.channel.webhooks()
            webhook = get(webhooks, id=self.bot.user_data["Webhooks"].get(str(ctx.channel.id)))
            if not webhook:
                return

            # Check if the message belongs to the reaction user.
            if identification == user and user.id != self.bot.user.id:
                engravedid = create_engraved_id_from_user(identification.id)
                original_content = ctx.message.content.strip(engravedid)
                original_content = original_content.strip(EID_FROM_INT[10])

                try:
                    conf = await identification.send(embed=Embed(
                        title=f"Editing Message",
                        description=f"Server: {ctx.guild.name}\n"
                                    f"Channel: {ctx.channel.mention}\n"
                                    f"Original content to copy: ```{original_content}```"
                    ).set_footer(text="Your next message you send here will edit the target message."))
                
                except Forbidden:
                    conf = await ctx.send(embed=Embed(
                        title=f"Editing Message",
                        description=f"Server: {ctx.guild.name}\n"
                                    f"Channel: {ctx.channel.mention}\n"
                                    f"Original content to copy: ```{original_content}```"
                    ).set_footer(text="Your next message you send here will edit the target message."))
                
                except Exception:
                    return

                while True:
                    try:
                        msg = await self.bot.wait_for("message", timeout=30, bypass_cooldown=True,
                            check=lambda m: m.channel.id == conf.channel.id and \
                                m.author.id == identification.id)

                    except TimeoutError:
                        await conf.edit(embed=Embed(
                            title=f"Editing Message",
                            description=f"Server: {ctx.guild.name}\n"
                                        f"Channel: {ctx.channel.mention}\n"
                                        f"Original content to copy: ```{original_content}```"
                        ).set_footer(text="Timed out."))
                        return

                    else:
                        if not msg.content or msg.content == original_content:
                            continue

                        await ctx.message.remove_reaction("📝", identification)
                        await webhook.edit_message(ctx.message.id, content=f"{msg.content}{engravedid}")

                        await conf.edit(embed=Embed(
                            title=f"Editing Message",
                            description=f"Server: {ctx.guild.name}\n"
                                        f"Channel: {ctx.channel.mention}\n"
                                        f"Original content to copy: ```{original_content}```\n"
                                        f"New content: ```{msg.content}```"
                        ).set_footer(text=Embed.Empty))
                        return

        elif str(payload.emoji) == "❓" and \
            message.author.bot and \
            message.author.discriminator == "0000":
            engravedid = get_engraved_id_from_msg(message.content)
            if engravedid:
                identification = await self.bot.fetch_user(engravedid)
            else:
                return
            
            if user != identification:
                with suppress(Forbidden):
                    await user.send(
                        "Unsure who that was? It was you, of course!\n"
                        "The reaction was left unchanged.")
            else:
                with suppress(Forbidden):
                    await user.send(
                        f"Unsure who that was? Their username is {str(identification)} (UID: {str(identification.id)}).\n"
                        f"The reaction was left unchanged.")
        else:
            return

    # Errors
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        if not isinstance(error, CommandNotFound):
            with suppress(Forbidden):
                await ctx.message.add_reaction("❌")
            
        if ctx.command and not isinstance(error, CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)
            
        if self.bot.config['debug_mode']:
            try:
                raise error.original
            except AttributeError:
                raise error
            
        if not self.bot.config['debug_mode']:
            msg = ctx.message
            em = Embed(title="Error", color=0xff0000)
            if isinstance(error, BotMissingPermissions):
                em.description = f"This bot is missing one or more permissions listed in `{self.bot.command_prefix}help` " \
                                 f"under `Required Permissions` or you are trying to use the command in a DM channel." \

            elif isinstance(error, MissingPermissions):
                em.description = "You are missing a required permission, or you are trying to use the command in a DM channel."

            elif isinstance(error, NotOwner):
                em.description = "That command is not listed in the help menu and is to be used by the owner only."

            elif isinstance(error, MissingRequiredArgument):
                em.description = f"\"{error.param.name}\" is a required argument for command " \
                                 f"\"{ctx.command.name}\" that is missing."

            elif isinstance(error, BadArgument):
                em.description = f"You didn't type something correctly. Details below:\n" \
                                 f"{error}"

            elif isinstance(error, CommandNotFound):
                return
                        
            elif isinstance(error, CommandOnCooldown):
                await msg.author.send(embed=Embed(
                    description=f"That command is on a {round(error.cooldown.per)} second cooldown.\n"
                                f"Retry in {round(error.retry_after)} seconds."))
            
            elif isinstance(error, CheckFailure):
                return

            else:
                try:
                    em.description = f"**{type(error.original).__name__}**: {error.original}\n" \
                                    f"\n" \
                                    f"If you keep getting this error, please join the support server."
                except AttributeError:
                    em.description = f"**{type(error).__name__}**: {error}\n" \
                                    f"\n" \
                                    f"If you keep getting this error, please join the support server."
                
                # Raising the exception causes the progam 
                # to think about the exception in the wrong way, so we must 
                # target the exception indirectly.
                if not self.bot.config["debug_mode"]:
                    try:
                        try:
                            raise error.original
                        except AttributeError:
                            raise error
                    except Exception:
                        error = exc_info()

                    await self.bot.errorlog.send(error, ctx=ctx, event=f"Command: {ctx.command.name}")
                else:
                    try:
                        raise error.original
                    except AttributeError:
                        raise error
            
            try:
                await ctx.send(embed=em)
            except Forbidden:
                with suppress(Forbidden):
                    await ctx.author.send(
                        content="This error was sent likely because I "
                                "was blocked from sending messages there.",
                        embed=em)

def setup(bot):
    bot.add_cog(Events(bot))