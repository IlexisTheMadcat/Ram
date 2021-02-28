from os import remove

from discord import File, Member
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import has_permissions, bot_has_permissions, command
from discord.user import User
from discord.errors import NotFound
from requests import get
from PIL import Image

from utils.classes import Bot
from utils.classes import ModdedEmbed as Embed

class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    # VANITY AVATAR CONTROL
    @command(aliases=["set"])
    @bot_has_permissions(manage_webhooks=True, send_messages=True, embed_links=True)
    async def set_vanity(self, ctx: Context, url: str = None):

        guild = ctx.guild
        author = ctx.author
        chan = ctx.channel
        msg = ctx.message

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

        user_perms = ctx.channel.permissions_for(ctx.author)
        mode = "an image URL"

        if (str(guild.id) in self.bot.user_data["VanityAvatars"] and
                str(author.id) in self.bot.user_data["VanityAvatars"][str(guild.id)] and
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][2]) and \
                not user_perms.manage_nicknames:
            return await ctx.send(embed=Embed(
                title="Permission Denied",
                description="You are currently blocked from using vanity avatars in this "
                            "server. Contact a moderator with the `Manage Messages` "
                            "permission to unblock you.",
                color=0xff0000))
        
        try:
            if url in self.bot.user_data["Closets"][str(author.id)]:
                check = await self.bot.get_user_vote(str(author.id))

                if not check:
                    return await ctx.send(embed=Embed(
                        title="Vote-Locked!",
                        description=f"Closets are vote-locked. Please go to "
                                    f"{self.bot.dbl_vote} and click on 'Vote'.\nThen come "
                                    f"back and try again. If you just now voted, wait a "
                                    f"few moments.",
                        color=0xff0000))

                elif check:
                    url = self.bot.user_data["Closets"][str(author.id)][url]
                    mode = "closet entry"
            else:
                pass

        except KeyError or IndexError:
            pass
        
        if url is None:
            try:
                url = msg.attachments[0].url
                mode = "attachment"

            except IndexError:
                try:
                    url = self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][1]

                    if url is None:
                        raise KeyError

                    else:
                        mode = "previous avatar"

                except KeyError:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="Not enough parameters!",
                        color=0xff0000))
                    return

        try:
            dummy = await chan.create_webhook(name=author.display_name)
            await dummy.send(embed=Embed(
                title="Success",
                description=f"Vanity successfully created using {mode}.\n"
                            f"Send a message in an unblocked channel to test it out!‎‎\n",),
                avatar_url=url)
            await dummy.delete()

        except Exception as e:
            return await ctx.send(embed=Embed(
                title="URL Error",
                description=f"An error has occurred;\n"
                            f"Try making sure your url is valid and/or the image is a valid resolution.\n"
                            f"`Error: {e}`",
                color=0xff0000))

        else:
            if str(guild.id) not in self.bot.user_data["VanityAvatars"]:
                self.bot.user_data["VanityAvatars"].update({str(guild.id): dict()})

            if str(author.id) not in self.bot.user_data["VanityAvatars"][str(guild.id)]:
                self.bot.user_data["VanityAvatars"][str(guild.id)].update(
                    {str(author.id): [None, None, False, True]}
                )

            if self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][0] is None:
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)] = [url, url,
                                                                            self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][2],
                                                                            self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][3]]

            else:
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)] = [
                    url,
                    self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][0],
                    self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][2],
                    self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][3]
                ]
                
            print(
                f'+ SET/CHANGED vanity avatar for user '
                f'\"{ctx.author}\" in server "{ctx.guild.name}".'
            )

    @command(aliases=["remove"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def remove_vanity(self, ctx: Context):

        guild = ctx.guild
        author = ctx.author

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider "
                            "using it in a private channel in one of your servers.",))
        
        if str(guild.id) in self.bot.user_data["VanityAvatars"] and \
            str(author.id) in self.bot.user_data["VanityAvatars"][str(guild.id)] and \
            self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][0]:
            self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)] = [
                None,
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][0],
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][2],
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][3]]

            await ctx.send(embed=Embed(
                title="Success",
                description="Removed vanity."))
            
            print(
                f'- REMOVED vanity avatar for user \"{ctx.author}\" '
                f'in server "{ctx.guild.name}".')

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You don't have a vanity avatar on right now.",
                color=0xff0000))

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def current(self, ctx: Context, user: User, standard: str = None):

        guild = ctx.guild
        author = ctx.author

        if standard not in ["standard", "standard_url"]:
            standard = None

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider "
                            "using it in a private channel in one of your servers."))
        
        if user.id == self.bot.user.id:
            print(f"[] Sent bot's avatar url to user \"{author}\".")
            return await ctx.send(embed=Embed(
                title="Ram's Avatar",
                description="My avatar is located here:",
            ).set_image(url=self.bot.user.avatar_url))
        
        else:
            async def show_standard():
                if (str(user.avatar_url).endswith(".webp") or str(user.avatar_url).endswith(".webp?size=1024")) and standard != "standard_url":
                    r = get(user.avatar_url, allow_redirects=True)                  # Compatibility for mobile devices unable
                    with open(f"{self.bot.cwd}/avatar{user.id}.webp", "wb") as f:   # to render .webp files, especially iOS
                        f.write(r.content)

                    im = Image.open(f"{self.bot.cwd}/avatar{user.id}.webp")
                    im.save(f"{self.bot.cwd}/avatar{user.id}.png", format="PNG")
                    file = File(f"{self.bot.cwd}/avatar{user.id}.png")
                    im.close()

                    print(
                        f'[] Sent standard avatar url for \"{user}\"'
                        f' to user \"{author}\".'
                    )

                    await ctx.send(embed=Embed(
                        title=f"{user}'s Standard Avatar",
                        description="Their current standard avatar is here:"))
                    await ctx.send(file=file)

                    remove(f"{self.bot.cwd}/avatar{user.id}.webp")
                    remove(f"{self.bot.cwd}/avatar{user.id}.png")

                    return

                else:
                    print(
                        f'[] Sent standard avatar url for \"{user}\"'
                        f' to user \"{author}\".')

                    await ctx.send(embed=Embed(
                        title=f"{user}'s Standard Avatar",
                        description="Their current standard avatar url is located here:",
                    ).set_image(url=user.avatar_url))

                    return

            if not standard:
                if str(guild.id) in self.bot.user_data["VanityAvatars"] and user.id in self.bot.user_data["VanityAvatars"][str(guild.id)] and self.bot.user_data["VanityAvatars"][str(guild.id)][user.id][0]:

                    print(
                        f'[] Sent vanity avatar url for \"{user}\"'
                        f' to user \"{author}\".')

                    return await ctx.channel.send(embed=Embed(
                        title=f"Vanity Avatar: {user}",
                        description="Their current vanity avatar is located here:\n",
                    ).set_image(url=self.bot.user_data['VanityAvatars'][str(guild.id)][user.id][0]))

                else:
                    await show_standard()

            elif standard in ["standard", "standard_url"]:
                await show_standard()

    @command(aliases=["pv"])
    @bot_has_permissions(manage_webhooks=True, send_messages=True, embed_links=True)
    async def preview(self, ctx, url=None):
        try:
            dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
            await dummy.send(embed=Embed(
                title="Preview",
                description=f"{self.bot.user.name}: Preview message.\n",
                ).set_image(url=url),
                avatar_url=url)
            return await dummy.delete()
        except Exception as e:
            return await ctx.send(embed=Embed(
                title="URL Error",
                description=f"An error has occurred;\n"
                            f"Try making sure your url is valid and/or the image is a valid resolution.\n"
                            f"Your channel may also have to many webhooks. Read the error below.\n"
                            f"`Error: {e}`",
                color=0xff0000))

    @command(aliases=["toggle_x", "quick_del"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def toggle_quick_delete(self, ctx):
        guild = ctx.guild
        author = ctx.author
        if str(guild.id) in self.bot.user_data["VanityAvatars"] and str(author.id) in self.bot.user_data["VanityAvatars"][str(guild.id)]:
            self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][3] = not self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][3]
            symbol = self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][3]
            if symbol:
                symbol = "✅"
            elif not symbol:
                symbol = "❎"

            await ctx.send(embed=Embed(
                title="Quick delete",
                description=f"{symbol} Quick delete toggled!\n"))
        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You can't use this feature until you have created your vanity for the first time here.",
                color=0xff0000))

    # BLACKLISTING
    @command(aliases=["bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def blacklist(self, ctx: Context, mode: str, item: str = None):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers.",
                color=0xff0000))
        
        channeladd = ["channel-add", "ch-a"]  # TODO: Maybe `blacklist` should be `group` with `mode`s as subcommands.
        channelremove = ["channel-remove", "ch-r"]  # TODO: Ask me about this.
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if mode in channeladd:
            if not item:
                item = str(ctx.channel.id)
                here = True
            else:
                here = False

            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)

            except ValueError:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`item` needs to be a number and proper channel ID. You can also #mention the channel.\n"
                                f"See `var:help Commands` under `var:blacklist` "
                                f"to see how to get channel ID.",
                    color=0xff0000))
                
                return

            else:
                try:
                    channel = self.bot.get_channel(item)
                except NotFound:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description=f"No channel with that ID exists.\n"
                                    f"See `var:help commands` under `var:blacklist` "
                                    f"to see how to get channel IDs.\nYou can also #mention the channel.",
                        color=0xff0000))

                else:
                    if ctx.author.id not in self.bot.user_data["Blacklists"].keys():
                        self.bot.user_data["Blacklists"][str(ctx.author.id)] = ([], [])

                    if item not in self.bot.user_data["Blacklists"][str(ctx.author.id)][0]:
                        self.bot.user_data["Blacklists"][str(ctx.author.id)][0].append(item)
                        
                        if here:
                            await ctx.send(embed=Embed(
                                title="Success",
                                description=f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                            f'(here) was blacklisted for you.\nYou can still use bot commands here.'))

                        elif not here:
                            await ctx.send(embed=Embed(
                                title="Success",
                                description=f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                            f'was blacklisted for you.\nYou can still use bot commands there.'))
                            
                        print(f'+ Channel "{channel.name}" in server "{channel.guild.name}" '
                              f'was blacklisted for \"{ctx.author}\".')
                        
                    else:
                        if not here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description="That channel is already blacklisted for you.",
                                color=0xff0000))

                        elif here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description="This channel is already blacklisted for you.",
                                color=0xff0000))

                        return

        elif mode in channelremove:
            if not item:
                item = str(ctx.channel.id)
                here = True
            else:
                here = False

            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)
            except ValueError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`channel` needs to be a number and proper channel ID.\n"
                                f"Type and enter `var:see_blacklists` "
                                f"and find the __ID__ of the channel you want to remove from that list.\n"
                                f"You can also \\#mention the channel.",
                    color=0xff0000))

            else:
                if ctx.author.id in self.bot.user_data["Blacklists"].keys():
                    if item in self.bot.user_data["Blacklists"][str(ctx.author.id)][0]:
                        self.bot.user_data["Blacklists"][str(ctx.author.id)][0].remove(item)
                        channel = self.bot.get_channel(item)
                        await ctx.send(embed=Embed(
                            title="Success",
                            description=f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                        f'was removed from your blacklist.'))
                        
                        print(f'- Channel "{channel.name}" in server "{channel.guild.name}" '
                              f'was removed from blacklisted items for user \"{ctx.author}\".')
                    
                    else:
                        if not here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description=f"That channel isn't in your blacklist.\n"
                                            f"Type `var:see_blacklists` to see your "
                                            f"blacklisted channels and prefixes.",
                                color=0xff0000))

                        elif here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description=f"This channel isn't in your blacklist.\n"
                                            f"Type `var:see_blacklists` to see your "
                                            f"blacklisted channels and prefixes.",
                                color=0xff0000))
                        
                        return
                else:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="You have nothing to remove from your blacklist.",
                        color=0xff0000))
                    
                    return

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="Your prefix can only be up to 5 characters long.",
                    color=0xff0000))

            if ctx.author.id not in self.bot.user_data["Blacklists"].keys():
                self.bot.user_data["Blacklists"][str(ctx.author.id)] = ([], [])

            if item not in self.bot.user_data["Blacklists"][str(ctx.author.id)][1]:
                self.bot.user_data["Blacklists"][str(ctx.author.id)][1].append(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Added "{item}" to blacklisted prefixes for you.'))

                print(f'+ Added "{item}" to blacklisted prefixes for user \"{ctx.author}\"')
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for you.",
                    color=0xff0000))

        elif mode in prefixremove:
            if ctx.author.id in self.bot.user_data["Blacklists"].keys():
                if item in self.bot.user_data["Blacklists"][str(ctx.author.id)][1]:
                    self.bot.user_data["Blacklists"][str(ctx.author.id)][1].remove(item)
                    await ctx.send(embed=Embed(
                        title="Success",
                        description=f'Removed "{item}" from blacklisted prefixes for you.'))

                    print(f'- Removed "{item}" from blacklisted prefixes for user \"{ctx.author}\".')

                    return
                else:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"`{item}` isn't in your blacklist.\n"
                                    f"Type `var:see_blacklists` to see your "
                                    f"blacklisted channels and prefixes.",
                        color=0xff0000))
            
            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing to remove from your blacklist.",
                    color=0xff0000))

        else:
            await ctx.send(embed=Embed(
                title="Argument Error",
                description=f'Invalid mode passed: `{mode}`; Refer to `var:help commands blacklist`.',
                color=0xff0000))

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["see_bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def see_blacklists(self, ctx: Context):
        if ctx.author.id in self.bot.user_data["Blacklists"].keys():
            if self.bot.user_data["Blacklists"][str(ctx.author.id)] == ([], []):
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You haven't blacklisted anything yet.",
                    color=0xff0000))

            message_part = []

            async def render():
                message_part.append("Here are your blacklisted items:\n")
                if not len(self.bot.user_data["Blacklists"][str(ctx.author.id)][0]) == 0:
                    message_part.append("**Channels:**\n")
                    for n in self.bot.user_data["Blacklists"][str(ctx.author.id)][0]:
                        try:
                            channel = self.bot.get_channel(n)
                        except NotFound:
                            self.bot.user_data["Blacklists"][str(ctx.author.id)][0].remove(n)
                            return False
                        else:
                            message_part.append(
                                f"-- Server: `{channel.guild.name}`; Name: {channel.mention}; ID: {channel.id}\n")
                            
                    return True

            while True:
                result = await render()
                if result is False:
                    message_part = list()
                    message_part.append("Here are your blacklisted items:\n```")
                    continue
                else:
                    break

            if not len(self.bot.user_data["Blacklists"][str(ctx.author.id)][1]) == 0:
                message_part.append("**Prefixes:**\n")
                for i in self.bot.user_data["Blacklists"][str(ctx.author.id)][1]:
                    message_part.append(f'-- `"{i}"`\n')

            message_full = ''.join(message_part)
            await ctx.send(embed=Embed(
                tile="Blacklist",
                description=message_full))
            
        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You haven't blacklisted anything yet.",
                color=0xff0000))

        print(f'[] Sent blacklisted items for user \"{ctx.author}\".')

    # CLOSETS
    @command(aliases=["cl_add"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def add_to_closet(self, ctx: Context, *, name: str):
        check = await self.bot.get_user_vote(ctx.author.id)
    
        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "[Top.gg](https://top.gg/bot/687427956364279873/vote) "
                            "and click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000))

        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

        if not ctx.message.attachments and \
                not self.bot.user_data["VanityAvatars"][str(ctx.guild.id)][str(ctx.author.id)][0]:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You don't have a vanity equipped.\n"
                            "You can attach a file to add without a vanity.",
                color=0xff0000))

        else:
            try:
                if str(ctx.author.id) not in self.bot.user_data["Closets"].keys():
                    self.bot.user_data["Closets"][str(ctx.author.id)] = {}

                if name in self.bot.user_data["Closets"][str(ctx.author.id)].keys():
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"A closet entry with that name already exists.\n"
                                    f"See your closet entries with this command: "
                                    f"`var:see_closet`.",
                        color=0xff0000))

                if len(self.bot.user_data["Closets"][str(ctx.author.id)].keys()) >= 10:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description="You've reached (or somehow exceeded) the max "
                                    "number of vanities allowed in your closet.\n"
                                    "Consider removing one of them.",
                        color=0xff0000))

                if len(name) > 20:
                    return await ctx.send(embed=Embed(
                        title="Name Error",
                        description="Your name can't be longer than 20 characters.",
                        color=0xff0000))

                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                    self.bot.user_data["Closets"][str(ctx.author.id)].update({name: url})
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added attached file to your closet with name `{name}`."))

                elif self.bot.user_data["VanityAvatars"][str(ctx.guild.id)][str(ctx.author.id)][0] is not None:
                    url = self.bot.user_data["VanityAvatars"][str(ctx.guild.id)][str(ctx.author.id)][0]
                    self.bot.user_data["Closets"][str(ctx.author.id)].update({name: url})
                    
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added current vanity avatar to closet with name `{name}`."))

            except KeyError or IndexError:
                self.bot.user_data["Closets"][str(ctx.author.id)] = {}

                try:
                    self.bot.user_data["Closets"][str(ctx.author.id)].update(
                        {name: self.bot.user_data["VanityAvatars"][str(ctx.guild.id)][str(ctx.author.id)][0]})
                
                except IndexError or KeyError:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"You don't have a vanity equipped. This particular error was caused because you haven't created your closet yet.\n"
                                    f"First, set your vanity using the `var:set_vanity <url>` command and try again.",
                        color=0xff0000))
                
                else:
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added with closet entry \"{name}\"."))

    @command(aliases=["cl_remove"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def remove_from_closet(self, ctx: Context, name: str):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "[Top.gg](https://top.gg/bot/687427956364279873/vote) "
                            "and click on 'Vote'.\n"
                            "Then come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000))
        
        if str(ctx.author.id) not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][str(ctx.author.id)] = {}

        try:
            if name not in self.bot.user_data["Closets"][str(ctx.author.id)].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{name}` doesn't exist.\n"
                                f"See your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

            else:
                self.bot.user_data["Closets"][str(ctx.author.id)].pop(name)

        except KeyError:
            self.bot.user_data["Closets"][str(ctx.author.id)] = dict()
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with the name `{name}` doesn't exist.\n"
                            f"See your closet entries with this command: "
                            f"`var:see_closet`.",
                color=0xff0000))
        
        else:
            await ctx.send(embed=Embed(
                title="Success",
                description=f"Removed closet entry \"{name}\"."))

    @command(aliases=["cl_rename"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def rename_closet_entry(self, ctx: Context, name: str, rename: str):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "[Top.gg](https://top.gg/bot/687427956364279873/vote) and "
                            "click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000))
        
        if str(ctx.author.id) not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][str(ctx.author.id)] = dict()
            
        try:
            if len(rename) > 20:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Your name can't be longer than 20 characters.",
                    color=0xff0000))

            if name == rename:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Both names are the same.",
                    color=0xff0000))

            elif name not in self.bot.user_data["Closets"][str(ctx.author.id)].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{name}` doesn't exist.\n"
                                f"See your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

            elif rename in self.bot.user_data["Closets"][str(ctx.author.id)].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{rename}` already exists.\n"
                                f"See your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

            else:
                orig_url = self.bot.user_data["Closets"][str(ctx.author.id)].pop(name)
                self.bot.user_data["Closets"][str(ctx.author.id)].update({rename: orig_url})

        except KeyError:
            self.bot.user_data["Closets"][str(ctx.author.id)] = dict()
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with with the name `{name}` doesn't exist.\n"
                            f"See your closet entries with this command: "
                            f"`var:see_closet`.",
                color=0xff0000))

        else:
            await ctx.send(embed=Embed(
                title="Success",
                description=f"Renamed closet entry \"{name}\" to \"{rename}\"."))

    @command(aliases=["cl", "closet"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def see_closet(self, ctx: Context, name: User = None):
        if not name:
            name = ctx.author
            if str(name.id) not in self.bot.user_data["Closets"].keys():
                self.bot.user_data["Closets"][str(name.id)] = {}

            check = await self.bot.get_user_vote(name.id)
                
            if not check:
                return await ctx.send(embed=Embed(
                    title="Vote-Locked!",
                    description="Closets are vote-locked. Please go to "
                                "[Top.gg](https://top.gg/bot/687427956364279873/vote) and "
                                "click on 'Vote'.\nThen come back and try again.\n"
                                "If you just now voted, wait a few moments."))

            message_part = list()
            try:
                message_part.append(
                    f"Here is your closet. You can use these anywhere. Used "
                    f"{len(self.bot.user_data['Closets'][str(name.id)].keys())}"
                    f"/10 slots.```\n")
                
                if self.bot.user_data["Closets"][str(name.id)]:
                    for i, url in self.bot.user_data["Closets"][str(name.id)].items():
                        message_part.append(
                            f"▛▚ Name: {i}\n"
                            f"▙▞ URL: ({url})\n"
                            f"\n")
                else:
                    raise KeyError
                
            except KeyError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing in your closet.",
                    color=0xff0000))

        else:
            if str(name.id) not in self.bot.user_data["Closets"].keys():
                self.bot.user_data["Closets"][str(name.id)] = dict()
    
            check = await self.bot.get_user_vote(name.id)

            if not check:
                return await ctx.send(embed=Embed(
                    title="Vote-Locked!",
                    description=f"Closets are vote-locked. Tell {name.name} to go to "
                                f"[Top.gg](https://top.gg/bot/687427956364279873/vote) "
                                f"and click on 'Vote'.\nThen come back and try again.\n"
                                f"If you just now voted, wait a few moments.",
                    color=0xff0000))
        
            message_part = list()
            try:
                message_part.append(
                    f"Here is their closet. Used "
                    f"{len(self.bot.user_data['Closets'][str(name.id)].keys())}"
                    f"/10 slots.```\n")
                
                if self.bot.user_data["Closets"][str(name.id)] != dict():
                    for i, url in self.bot.user_data["Closets"][str(name.id)].items():
                        message_part.append(
                            f"▛▚ Name: {i}\n"
                            f"▙▞ URL: ({url})\n"
                            f"\n")

                else:
                    raise KeyError

            except KeyError:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="They have nothing in their closet.",
                    color=0xff0000))
                return

        message_part.append("```")
        message = ''.join(message_part)

        await ctx.send(embed=Embed(
            title=f"{name}'s Closet",
            description=message))

    @command(aliases=["cl_preview", "cl_pv"])
    @bot_has_permissions(send_messages=True, embed_links=True, manage_webhooks=True)
    async def preview_closet_entry(self, ctx, name):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "[Top.gg](https://top.gg/bot/687427956364279873/vote) "
                            "and click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000))

        if str(ctx.author.id) not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][str(ctx.author.id)] = dict()

        try:
            if name in self.bot.user_data["Closets"][str(ctx.author.id)].keys():
                dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
                await dummy.send(embed=Embed(
                    title="Preview",
                    description=f"{self.bot.user.name}: Preview message.\n",
                    color=0xff87a3
                ).set_image(url=self.bot.user_data['Closets'][str(ctx.author.id)][name]),
                    avatar_url=self.bot.user_data["Closets"][str(ctx.author.id)][name])
                return await dummy.delete()

            else:
                await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with that name doesn't exist. "
                                f"See your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

        except KeyError or IndexError:
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with that name doesn't exist. "
                            f"See your closet entries with this command: "
                            f"`var:see_closet`.",
                color=0xff0000))
    
    # MODERATION
    @command(aliases=["s_bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    @has_permissions(manage_channels=True)
    async def server_blacklist(self, ctx: Context, mode: str, item: str = None):

        guild = ctx.guild
        author = ctx.author
        chan = ctx.channel

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider using "
                            "it in a private channel in one of your servers.",
                color=0xff0000))

        channeladd = ["channel-add", "ch-a"]  # TODO: Make commands group
        channelremove = ["channel-remove", "ch-r"]
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if (not item) and (mode in channeladd or mode in channelremove):
            item = str(chan.id)
        
        if mode in channeladd:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)

            except ValueError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`channel` needs to be a number and proper channel ID. "
                                f"You can also #mention the channel.",
                    color=0xff0000))

            else:
                channel = await self.bot.get_channel(item)

                if channel is None:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description=f"No channel with that ID exists. Try to #mention the channel instead.",
                        color=0xff0000))

                else:
                    if channel not in guild.channels:
                        return await ctx.send(embed=Embed(
                            title="Access Denied",
                            description="The channel has to be in this server. I wouldn't "
                                        "just let you cheese your friends like that in "
                                        "another server.",
                            color=0xff0000))
                    
                    if guild.id not in self.bot.user_data["ServerBlacklists"]:
                        self.bot.user_data["ServerBlacklists"][str(guild.id)] = (list(), list())

                    if item not in self.bot.user_data["ServerBlacklists"][str(guild.id)][0]:
                        self.bot.user_data["ServerBlacklists"][str(guild.id)][0].append(item)
                        print(
                            f'+ Channel "{channel.name}" in server '
                            f'"{channel.guild.name}" was server-blacklisted.'
                        )
                        return await ctx.send(embed=Embed(
                            title="Success",
                            description=f'Channel "{channel.name}" in server '
                                        f'"{channel.guild.name}" was blacklisted for this '
                                        f'server.\nYou can still use bot commands there.'))

                    else:
                        return await ctx.send(embed=Embed(
                            title="Error",
                            description="You already blacklisted that channel for this "
                                        "server.",
                            color=0xff0000))

        elif mode in channelremove:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")
                
            try:
                item = int(item)

            except ValueError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`channel` needs to be a number and proper channel ID. Please #mention the channel instead.",
                    color=0xff0000))

            if guild.id in self.bot.user_data["ServerBlacklists"]:
                if item in self.bot.user_data["ServerBlacklists"][str(guild.id)][0]:
                    self.bot.user_data["ServerBlacklists"][str(guild.id)][0].remove(item)
                    channel = await self.bot.fetch_channel(item)
                    print(
                        f'- Channel "{channel.name}" in server '
                        f'"{channel.guild.name}" was removed from '
                        f'server-blacklisted items.'
                    )
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f'Channel "{channel.name}" in server '
                                    f'"{channel.guild.name}" was removed from your '
                                    f'server\'s blacklist.',
                        color=0xff87a3))

                else:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"That channel isn't in your server's blacklist.\n"
                                    f"Type `{self.bot.command_prefix}see_server_blacklists` "
                                    f"to see your blacklisted channels "
                                    f"and prefixes.",
                        color=0xff0000))

            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing to remove from your server's "
                                "blacklist yet.",
                    color=0xff0000))

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Your prefix can only be up to 5 characters long.",
                    color=0xff0000))
        
            if guild.id not in self.bot.user_data["ServerBlacklists"]:
                self.bot.user_data["ServerBlacklists"][str(guild.id)] = (list(), list())

            if item not in self.bot.user_data["ServerBlacklists"][str(guild.id)][1]:
                self.bot.user_data["ServerBlacklists"][str(guild.id)][1].append(item)
                print(
                    f'+ Added \"{item}\" to blacklisted prefixes for user '
                    f'"{author}"'
                )
                return await ctx.send(embed=Embed(
                    title="Success",
                    description=f"Added \"{item}\" to blacklisted prefixes for this server."))

            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for this server.",
                    color=0xff0000))

        elif mode in prefixremove:
            if guild.id in self.bot.user_data["ServerBlacklists"]:
                if item in self.bot.user_data["ServerBlacklists"][str(guild.id)][1]:
                    self.bot.user_data["ServerBlacklists"][str(guild.id)][1].remove(item)
                    print(
                        f'- Removed "{item}" from blacklisted prefixes for '
                        f'user "{ctx.author}".'
                    )
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f'Removed "{item}" from blacklisted prefixes for this server.'))

                else:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"`{item}` isn't in your blacklist.\nType "
                                    f"`{self.bot.command_prefix}see_server_blacklists` "
                                    f"to see your blacklisted channels and prefixes.",
                        color=0xff0000))

            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing to remove from your blacklist.",
                    color=0xff0000))

        else:
            return await ctx.send(embed=Embed(
                title="Argument Error",
                description=f'Invalid mode passed: `{mode}`; Refer to '
                            f'`{self.bot.command_prefix}help commands blacklist`.',
                color=0xff0000))

    @command(aliases=["see_s_bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def see_server_blacklists(self, ctx: Context):

        guild = ctx.guild

        if guild.id not in self.bot.user_data["ServerBlacklists"]:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You haven't blacklisted anything for this server yet.",
                color=0xff0000))

        message_part = list()

        def render():
            if self.bot.user_data["ServerBlacklists"][str(guild.id)] == (list(), list()):
                message_part.append(
                    "You haven't blacklisted anything for this server yet.")
                
                return True

            message_part.append(
                "Here are this server's blacklisted items:")
            if len(self.bot.user_data["ServerBlacklists"][str(guild.id)][0]) != 0:
                message_part.append("**Channels:**")
                for c_id in self.bot.user_data["ServerBlacklists"][str(guild.id)][0]:
                    channel = guild.get_channel(c_id)
                    if channel:
                        message_part.append(
                            f"-- Name: {channel.mention}; ID: {channel.id}")
                    else:
                        self.bot.user_data["ServerBlacklists"][str(guild.id)][0].remove(i)
                        return False

                return True

        while True:
            result = render()
            if result is False:
                message_part = list()
                message_part.append("Here are your blacklisted items:```")
                continue
            else:
                break

        if len(self.bot.user_data["ServerBlacklists"][str(guild.id)][1]) != 0:
            message_part.append("**Prefixes:**")
            for i in self.bot.user_data["ServerBlacklists"][str(guild.id)][1]:
                message_part.append(f'-- `"{i}"`')

        message_full = "\n".join(message_part)
        await ctx.send(embed=Embed(
            title="Server Blacklist",
            description=message_full))

        print(
            f'[] Sent server-blacklisted items for user '
            f'"{ctx.author}" in server "{guild.name}".')

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def list(self, ctx: Context):
        guild = ctx.guild
        message = list()
        if guild.id in self.bot.user_data["VanityAvatars"] and \
                self.bot.user_data["VanityAvatars"][str(guild.id)] != dict():
            message.append(
                "Here are users using vanities in this server; "
                "The list may contain members who have left:\n```")

            show_list = False
            for u_id in self.bot.user_data["VanityAvatars"][str(guild.id)]:
                user = self.bot.get_user(u_id)
                if user and self.bot.user_data["VanityAvatars"][str(guild.id)][u_id][0]:
                    message.append(
                        f"{user} - URL: \n"
                        f"{self.bot.user_data['VanityAvatars'][str(guild.id)][u_id][0]}\n\n")
                    show_list = True

            if not show_list:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="This server has no users with equipped vanities.",
                    color=0xff0000
                ))

            message.append("```")
            await ctx.send(embed=Embed(
                title="Server Equipped Vanities",
                description=''.join(message)))

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="This server has no users with equipped vanities.",
                color=0xff0000))

    @bot_has_permissions(send_messages=True, embed_links=True)
    @has_permissions(manage_nicknames=True)
    @command(aliases=["manage", "user"])
    async def manage_user(self, ctx: Context, mode: str, user: Member):

        guild = ctx.guild
        author = ctx.author
        author_role = author.top_role
        
        if not (guild.id in self.bot.user_data["VanityAvatars"] and
                user.id in self.bot.user_data["VanityAvatars"][str(guild.id)]):
            return await ctx.send(embed=Embed(
                title="Error",
                description="That user has no information linked with this server.",
                color=0xff0000))

        if user.id == author.id and author.id != guild.owner.id:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You cannot use this command on yourself.",
                color=0xff0000))

        if author.id != guild.owner.id and guild.id in self.bot.user_data["VanityAvatars"] and author.id \
                in self.bot.user_data["VanityAvatars"][str(guild.id)] and \
                self.bot.user_data["VanityAvatars"][str(guild.id)][str(author.id)][2]:
            return await ctx.send(embed=Embed(
                title="Permission Error",
                description="You cannot use this command because you were blocked "
                            "from using vanity avatars by another user.",
                color=0xff0000))

        if user is None:
            return await ctx.send(embed=Embed(
                title="Error",
                description="That user is not a part of this server or does not exist.",
                color=0xff0000))

        if author != guild.owner and author_role <= user.top_role:
            return await ctx.send(embed=Embed(
                title="Permission Error",
                description="You cannot manage this user because they have an "
                            "equal or higher role than you.",
                color=0xff0000))

        if mode == "block":
            if self.bot.user_data["VanityAvatars"][str(guild.id)][user.id][2]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That user is already blocked.",
                    color=0xff0000))

            else:
                self.bot.user_data["VanityAvatars"][str(guild.id)][user.id][0] = None
                self.bot.user_data["VanityAvatars"][str(guild.id)][user.id][2] = True
                return await ctx.send(embed=Embed(
                    title="Success",
                    description="User vanity avatar removed and blocked for this server."))

        elif mode == "unblock":
            if not self.bot.user_data["VanityAvatars"][str(guild.id)][user.id][2]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That user is already unblocked.",
                    color=0xff0000))

            else:
                self.bot.user_data["VanityAvatars"][str(guild.id)][user.id][2] = False
                return await ctx.send(embed=Embed(
                    title="Success",
                    description="User unblocked for this server."))

        elif mode == "get_info":
            return await ctx.send(embed=Embed(
                title="Info",
                description=f"**Vanity status for user {str(user)}:**\n"
                            f"Vanity url: {self.bot.user_data['VanityAvatars'][str(guild.id)][user.id][0]}\n"
                            f"Previous url: {self.bot.user_data['VanityAvatars'][str(guild.id)][user.id][1]}\n"
                            f"Is blocked:  {self.bot.user_data['VanityAvatars'][str(guild.id)][user.id][2]}"))

def setup(bot):
    bot.add_cog(Commands(bot))
