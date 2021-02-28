# IMPORTS
from asyncio.exceptions import TimeoutError
from asyncio import sleep
from contextlib import suppress
from typing import List
from sys import exc_info

from timeit import default_timer
from discord import Webhook, Embed, Status, Message
from discord.errors import Forbidden, NotFound, HTTPException
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

from utils.classes import Bot
from utils.utils import (
    EID_FROM_INT,
    create_engraved_id_from_user,
    get_engraved_id_from_msg,)

class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # Message events
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_message(self, msg: Message):
        # MechHub Bot Status response
        if msg.author.id == 805162807942709268 and \
            msg.content.startswith(f"[{self.bot.user.id}] [MechHub Message Ping]"):
            await msg.channel.send("Pong!")
            return
        
        if msg.author.id == self.bot.user.id:
            return  # Don't respond to bots.

        if msg.author.id == 726313554717835284:  
            # If bot listing supports webhooks
            ids = msg.content.split(";")
            voter = int(ids[0])
            voted_for = int(ids[1])

            if voted_for == self.bot.user.id:
                user = await self.bot.fetch_user(voter)
                try:
                    await user.send("Voting message")

                except HTTPException or Forbidden:
                    print(f"[❌] User \"{user}\" voted for \"{self.bot.user}\". DM Failed.")
                else:
                    print(f"[✅] User \"{user}\" voted for \"{self.bot.user}\".")

                return

        # Check if the message is a command. 
        # Terminates the event if so, so the command can run.
        verify_command = await self.bot.get_context(msg)
        if verify_command.valid:
            self.bot.inactive = 0
            return

        # Support DMs
        if msg.guild is None:
            if msg.author.id != self.bot.owner_ids[0]:
                if msg.content.startswith("> "):
                    if msg.author.id not in self.bot.config['muted_dms']:
                        if msg.author.id in self.bot.waiting:
                            await msg.channel.send(":clock9: Please wait, you already have a question open.\n"
                                                   "You'll get a response from me soon.")

                            return

                        dev_guild = self.bot.get_guild(504090302928125954)
                        user = dev_guild.fetch_member(self.bot.owner_ids[0])
                        if user.status == Status.dnd:
                            await msg.channel.send(":red_circle: The developer currently has "
                                                   "Do Not Disturb on. Please try again later.")
                            return

                        status_msg = await msg.channel.send(":clock9: "
                                                            "I sent your message to the developer.\n"
                                                            "Please stand by for a response or "
                                                            "until **this message is edited**...\n")

                        self.bot.waiting.append(msg.author.id)

                        embed = Embed(color=0xff87a3)
                        embed.title = f"Message from user {msg.author} (ID: {msg.author.id}):"
                        embed.description = f"{msg.content}\n\n" \
                                            f"Replying to this DM **within 120 seconds** " \
                                            f"after accepting **within 10 minutes** " \
                                            f"will relay the message back to the user."

                        dm = await user.send(content="**PENDING**", embed=embed)
                        await dm.add_reaction("✅")
                        await dm.add_reaction("❎")

                        def check(sreaction, suser):
                            if self.bot.thread_active:
                                self.bot.loop.create_task(
                                    reaction.channel.send("There is already an active thread running...\n "
                                                          "Please finish the **`ACTIVE`** one first."))
                                return False
                            else:
                                return sreaction.message.id == dm.id and \
                                    str(sreaction.emoji) in ["✅", "❎"] and \
                                    suser == user
                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", timeout=600, check=check)
                        except TimeoutError:
                            await dm.edit(content="**TIMED OUT**")
                            await status_msg.edit(content=":x: "
                                                          "The developer is unavailable right now. Try again later.")
                            return
                        else:
                            if str(reaction.emoji) == "❎":
                                await dm.edit(content="**DENIED**")
                                await status_msg.edit(content=":information_source: The developer denied your message. "
                                                              "Please make sure you are as detailed as possible.")
                                return
                            elif str(reaction.emoji) == "✅":
                                await dm.edit(content="**ACTIVE**")
                                await status_msg.edit(content=":information_source: "
                                                              "The developer is typing a message back...")
                                self.bot.thread_active = True
                                pass

                        def check(message):
                            return message.author == user and message.channel == dm.channel
                        while True:

                            try:
                                response = await self.bot.wait_for("message", timeout=120, check=check)
                            except TimeoutError:
                                conf = await user.send(":warning: Press the button below to continue typing.")
                                await conf.add_reaction("🔘")

                                def conf_button(b_reaction, b_user):
                                    return str(b_reaction.emoji) == "🔘" and b_user == user \
                                           and b_reaction.message.channel == dm.channel

                                try:
                                    await self.bot.wait_for("reaction_add", timeout=10, check=conf_button)
                                except TimeoutError:
                                    await conf.delete()
                                    await dm.edit(content="**TIMED OUT**")
                                    await dm.channel.send("You timed out. "
                                                          "The user was notified that you are not available right now.")

                                    self.bot.waiting.remove(msg.author.id)
                                    self.bot.thread_active = False
                                    await status_msg.edit(content=":information_source: "
                                                                  "The developer timed out on typing a response. "
                                                                  "Please ask at a later time.\n"
                                                                  "You may also join the support server here: "
                                                                  "https://discord.gg/j2y7jxQ")
                                    return
                                else:
                                    await conf.delete()
                                    continue
                            else:
                                self.bot.waiting.remove(msg.author.id)
                                self.bot.thread_active = False
                                await dm.edit(content="**Answered**")
                                await dm.channel.send(":white_check_mark: Okay, message sent.")
                                await status_msg.edit(content=":white_check_mark: The developer has responded.")
                                await msg.channel.send(f":newspaper: Response from the developer:\n{response.content}")
                                return
                    else:
                        await msg.channel.send("You've been muted by the developer, "
                                               "so you cannot send anything.\n"
                                               "If you believe you were muted by mistake, "
                                               "please join the support server:\n"
                                               "https://discord.gg/j2y7jxQ\n\n"
                                               "**Note that spamming will get you banned without hesitation.**")
                        return
                else:
                    await msg.channel.send("Please start your message with "
                                           "\"`> `\" "
                                           "to ask a question or send compliments.\n"
                                           "This is the markdown feature to create quotes.",
                                           delete_after=5)
                    return
            return
    
        # React with passion
        if self.bot.user.mentioned_in(msg):
            try:
                if msg.author.id in self.bot.owner_ids:
                    await msg.add_reaction("💕")
                else:
                    await msg.add_reaction("👋")
            except Forbidden:
                pass

        # Self-Blacklisted
        try:
            for i in self.bot.user_data["Blacklists"][str(msg.author.id)][1]:
                if msg.content.startswith(i):
                    return

            for i in self.bot.user_data["Blacklists"][str(msg.author.id)][0]:
                if str(msg.channel.id) == i:
                    return

        except KeyError:
            pass

        # Server-Blacklisted
        try:
            for i in self.bot.user_data["ServerBlacklists"][str(msg.guild.id)][1]:
                if msg.content.startswith(i):
                    return

            for i in self.bot.user_data["ServerBlacklists"][str(msg.guild.id)][0]:
                if str(msg.channel.id) == i:
                    return

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
            engravedid = get_engraved_id_from_msg(msg.content)
            if engravedid:
                eid_user = await self.bot.fetch_user(engravedid)
                if eid_user:
                    if self.bot.user_data["VanityAvatars"][str(msg.guild.id)][str(eid_user.id)][3]:
                        with suppress(Forbidden):
                            await msg.add_reaction("❌")
                            await sleep(5)
                            with suppress(NotFound):
                                await msg.remove_reaction("❌", msg.guild.me)

            if str(msg.author.id) in self.bot.user_data["VanityAvatars"][str(msg.guild.id)].keys() and \
                    not msg.author.bot and \
                    self.bot.user_data["VanityAvatars"][str(msg.guild.id)][str(msg.author.id)][0]:

                engravedid = create_engraved_id_from_user(msg.author.id)

                if msg.content != "":
                    new_content = f"{msg.content}  {engravedid}"
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
                    if "Webhooks" not in self.bot.user_data.keys():
                        self.bot.user_data["Webhooks"] = {"channelID": "webhookID"}

                    if str(msg.channel.id) not in self.bot.user_data["Webhooks"]:
                        self.bot.user_data["Webhooks"][str(msg.channel.id)] = 0

                    webhooks: List[Webhook] = await msg.channel.webhooks()
                    webhook: Webhook = get(webhooks, id=self.bot.user_data["Webhooks"].get(str(msg.channel.id)))
                    if webhook is None:
                        webhook: Webhook = await msg.channel.create_webhook(name="Vanity Profile Pics")
                        self.bot.user_data["Webhooks"][str(msg.channel.id)] = webhook.id

                    try:
                        await msg.delete()
                        await webhook.send(
                            new_content,
                            files=attachment_files,
                            avatar_url=self.bot.user_data["VanityAvatars"][str(msg.guild.id)][str(msg.author.id)][0],
                            username=msg.author.display_name)
                    
                    except Exception:
                        await msg.author.send("I failed to transform your message, please use the `var:set` command again with a proper url.")
                        del start
                        return
                    
                    self.bot.inactive = 0
                    stop = default_timer()

                comptime = round(stop - start, 3)
                print(f"[] Response delay {str(comptime).ljust(5)}s from {msg.author} ({msg.author.id})")

                self.bot.inactive = 0

            else:
                return

        except KeyError:
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
        except (NotFound, Forbidden):
            return
        
        if not ctx.guild:
            return

        if user == self.bot.user:
            return

        if str(payload.emoji) == "❌":
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
                    await self.bot.http.delete_message(
                        channel.id,
                        message.id,
                        reason="Deleted on user request.")
                
                except Forbidden:
                    with suppress(HTTPException, Forbidden):
                        await self.bot.http.remove_reaction(
                            channel.id,
                            message.id,
                            payload.emoji,
                            user.id)
                        
                        await user.send('`If you want to do that, this bot needs the "Manage Messages" permission.`')
            else:
                if user != self.bot.user:
                    with suppress(Forbidden):
                        await user.send(f"That's not your message to delete. "
                                        f"Ask {str(identification)} to delete it.\n"
                                        f"The reaction was left unchanged.")

        elif str(payload.emoji) == "❓" and \
            message.author.bot and \
            message.author.discriminator == "0000":
            engravedid = get_engraved_id_from_msg(message.content)
            identification = await self.bot.fetch_user(engravedid)

            with suppress(Forbidden):
                await user.send(
                    f'Unsure who that was?\nTheir username is \"{str(identification)}\".\n'
                    f'The reaction was left unchanged.')
        else:
            return

    # Errors
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        if not isinstance(error, CommandNotFound):
            with suppress(Forbidden):
                await ctx.message.add_reaction("❌")
            
        if not isinstance(error, CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)
            
        if self.bot.config['debug_mode']:
            raise error.original
            
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
                supposed_command = msg.content.split()[0]
                em.description = f"Command \"{supposed_command}\" doesn't exist."
            
            elif isinstance(error, CommandOnCooldown):
                await msg.author.send(embed=Embed(
                    description=f"That command is on a {round(error.cooldown.per)} second cooldown.\n"
                                f"Retry in {round(error.retry_after)} seconds."))
            
            elif isinstance(error, CheckFailure):
                return

            else:
                em.description = f"**{type(error.original).__name__}**: {error.original}\n" \
                                 f"\n" \
                                 f"If you keep getting this error, please join the support server "

                # Raising the exception causes the progam 
                # to think about the exception in the wrong way, so we must 
                # target the exception indirectly.
                if not self.bot.config["debug_mode"]:
                    try:
                        raise error.original
                    except Exception:
                        error = exc_info()

                    await self.bot.errorlog.send(error, event=f"Command: {ctx.command.name}")
                else:
                    try:
                        raise error.original
                    except AttributeError:
                        raise error
            
            await ctx.author.send(embed=em)

def setup(bot):
    bot.add_cog(Events(bot))