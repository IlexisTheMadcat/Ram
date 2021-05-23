from discord import Member
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import has_permissions, bot_has_permissions, command
from discord.user import User
from discord.errors import NotFound

from utils.classes import Bot, ModdedEmbed as Embed

newline = "\n"


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(name="test")
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def test(self, ctx):
        try:
            await ctx.send("Done (1/2).")
        except Exception:
            await ctx.author.send("(1/2) I can't send messages there.")
        
        try:
            await ctx.send(embed=Embed(title="Done (2/2)."))
        except Exception:
            await ctx.send("(2/2) I can't send embeds in here.")
    
    # VANITY AVATAR CONTROL
    @command(aliases=["set"])
    @bot_has_permissions(manage_webhooks=True, send_messages=True, embed_links=True)
    async def set_vanity(self, ctx: Context, url: str = None):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

        user_perms = ctx.channel.permissions_for(ctx.author)
        mode = "an image URL"

        if ctx.author.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"] and \
            not user_perms.manage_messages:
            await ctx.send(embed=Embed(
                title="Permission Denied",
                description="You are currently blocked from using vanity avatars in this "
                            "server. Contact a moderator with the `Manage Messages` "
                            "permission to unblock you.",
                color=0xff0000))
            
            return
        
        try:
            if url in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"]:
                check = await self.bot.get_user_vote(ctx.author.id)

                if not check:
                    return await ctx.send(embed=Embed(
                        title="Vote-Locked!",
                        description=f"Closets are vote-locked. Please go to "
                                    f"{self.bot.dbl_vote} and click on 'Vote'."
                                    f"Then come back and try again.\n"
                                    f"If you just now voted, wait a few moments.",
                        color=0xff0000))

                elif check:
                    url = self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"][url]
                    mode = "closet entry"
            else:
                pass

        except KeyError or IndexError:
            pass
        
        if url is None:
            try:
                url = ctx.message.attachments[0].url
                mode = "attachment"

            except IndexError:
                try:
                    url = self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][1]

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
            dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
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
            if str(ctx.guild.id) not in self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"]:
                self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)] = [url, url]

            else:
                self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)] = [
                    url, self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]]
                
            print(
                f'+ SET/CHANGED vanity avatar for user '
                f'{ctx.author} ({ctx.author.id}) in server {ctx.guild.name} ({ctx.guild.id}).')

    @command(aliases=["remove"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def remove_vanity(self, ctx: Context):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider "
                            "using it in a private channel in one of your servers.",))
        
        if str(ctx.guild.id) in self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"]:
            self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)] = [
                None, self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]]

            await ctx.send(embed=Embed(
                title="Success",
                description="Removed vanity."))
            
            print(
                f'- REMOVED vanity avatar for user '
                f'{ctx.author} ({ctx.author.id}) in server {ctx.guild.name} ({ctx.guild.id}).')

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You don't have a vanity avatar on right now.",
                color=0xff0000))

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def current(self, ctx: Context, user: User, standard: str = None):
        if standard not in ["standard", "standard_url"]:
            standard = None

        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider "
                            "using it in a private channel in one of your servers."))
        
        if user.id == self.bot.user.id:
            print(f"[] Sent bot's avatar url to user \"{ctx.author}\".")
            await ctx.send(embed=Embed(
                title="Ram's Avatar",
                description="My avatar is located here:",
            ).set_image(url=self.bot.user.avatar_url))
            return

        else:
            async def show_standard():
                await ctx.send(embed=Embed(
                    title=f"{user}'s Standard Avatar",
                    description="Their current standard avatar is here:"
                ).set_image(url=user.avatar_url))
                
                print(
                    f'[] Sent standard avatar url for {user} ({user.id}'
                    f' to user {ctx.author} ({ctx.author.id}).')
                
                return


            if not standard:
                if str(ctx.guild.id) in self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"] and \
                    self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][0]:

                    return await ctx.channel.send(embed=Embed(
                        title=f"Vanity Avatar: {user}",
                        description="Their current vanity avatar is located here:\n",
                    ).set_image(url=self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]))

                    print(
                        f'[] Sent vanity avatar url for {user} ({user.id}'
                        f' to user {ctx.author} ({ctx.author.id}).')
                
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
        self.bot.user_data["UserData"][str(ctx.author.id)]["Settings"]["QuickDelete"] = \
            not self.bot.user_data["UserData"][str(ctx.author.id)]["Settings"]["QuickDelete"]
        
        symbol = self.bot.user_data["UserData"][str(ctx.author.id)]["Settings"]["QuickDelete"]
        if symbol:
            symbol = "✅"
        elif not symbol:
            symbol = "❎"

        await ctx.send(embed=Embed(
            title="Quick delete",
            description=f"{symbol} Quick delete toggled!\n"))

    # BLACKLISTING
    @command(aliases=["bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def blacklist(self, ctx: Context, mode: str = "view", item: str = None):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))
        
        channeladd = ["channel-add", "ch-a"]
        channelremove = ["channel-remove", "ch-r"]
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
                    description="`item` for mode `channel-add` needs to be a number and proper channel ID.\n"
                                "See `var:help Commands` under `var:blacklist` "
                                "to see how to get channel ID. You can also #mention the channel.",
                    color=0xff0000))
                
                return

            else:
                channel = self.bot.get_channel(item)
                if not channel:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="No channel with that ID exists.\n"
                                    "See `var:help commands` under `var:blacklist` "
                                    "to see how to get channel IDs. You can also #mention the channel.",
                        color=0xff0000))

                else:
                    if item not in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0]:
                        self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0].append(item)
                        
                        if here:
                            await ctx.send(embed=Embed(
                                title="Success",
                                description=f'{channel.mention} (here) was blacklisted for you.\nYou can still use bot commands here.'))

                        elif not here:
                            await ctx.send(embed=Embed(
                                title="Success",
                                description=f'{channel.mention} (here) was blacklisted for you.\nYou can still use bot commands here.'))

                        print(f'+ Channel "{channel.name}" ({channel.id}) '
                              f'was blacklisted for {ctx.author} ({ctx.author.id}).')
                        
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
                    description="`item` for mode `channel-remove` needs to be a number and proper channel ID.\n"
                                "Type and enter `var:see_blacklists` "
                                "and find the __ID__ of the channel you want to remove from that list.\n"
                                "You can also \\#mention the channel.",
                    color=0xff0000))

            else:
                if item in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0]:
                    self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0].remove(item)
                    channel = self.bot.get_channel(item)
                    await ctx.send(embed=Embed(
                        title="Success",
                        description=f'{channel.mention} was removed from your blacklist.'))
                    
                    print(f'- Channel "{channel.name}" ({channel.id}) '
                          f'was unblacklisted for {ctx.author} ({ctx.author.id}).')
                
                else:
                    if not here:
                        await ctx.send(embed=Embed(
                            title="Error",
                            description="That channel isn't in your blacklist.\n"
                                        "Type `var:see_blacklists` to see your "
                                        "blacklisted channels and prefixes.",
                            color=0xff0000))

                    elif here:
                        await ctx.send(embed=Embed(
                            title="Error",
                            description="This channel isn't in your blacklist.\n"
                                        "Type `var:see_blacklists` to see your "
                                        "blacklisted channels and prefixes.",
                            color=0xff0000))
                    
                    return

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="Your prefix can only be up to 5 characters long.",
                    color=0xff0000))

            if item not in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][1]:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][1].append(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Added "{item}" to blacklisted prefixes for you.'))

                print(f'+ Added "{item}" to blacklisted prefixes for user {ctx.author} ({ctx.author.id}).')
            
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for you.",
                    color=0xff0000))

        elif mode in prefixremove:
            if item in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][1]:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][1].remove(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Removed "{item}" from blacklisted prefixes for you.'))

                print(f'- Removed "{item}" from blacklisted prefixes for user {ctx.author} ({ctx.author.id}).')

                return
            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`{item}` isn't in your blacklist.\n"
                                f"Type `var:see_blacklists` to see your "
                                f"blacklisted channels and prefixes.",
                    color=0xff0000))

        elif mode == "view":
            if self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"] == ([], []):
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You haven't blacklisted anything yet.",
                    color=0xff0000))

            message_part = []

            async def render():
                message_part.append("Here are your blacklisted items:\n")
                if len(self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0]):
                    message_part.append("**Channels:**\n")
                    for n in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0]:
                        try:
                            channel = await self.bot.fetch_channel(n)
                        except NotFound:
                            self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][0].remove(n)
                            return False
                        else:
                            message_part.append(
                                f"-- {channel.mention} ({channel.id})\n")
                            
                    return True

            while True:
                result = await render()
                if not result:
                    message_part = []
                    continue
                else:
                    break

            if not len(self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][1]) == 0:
                message_part.append("**Prefixes:**\n")
                for i in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][1]:
                    message_part.append(f'-- `{i}`\n')

            message_full = ''.join(message_part)
            await ctx.send(embed=Embed(
                tile="Blacklist",
                description=message_full))

            print(f'[] Sent blacklisted items for user {ctx.author} ({ctx.author.id}).')

        else:
            await ctx.send(embed=Embed(
                title="Argument Error",
                description=f'Invalid mode passed: `{mode}`; Refer to `var:help commands blacklist`.',
                color=0xff0000))

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
        
        # Small utility
        def check_vanity():
            if str(ctx.guild.id) not in self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"]:
                return None
            
            return self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]

        if not ctx.message.attachments and not check_vanity():
            await ctx.send(embed=Embed(
                title="Error",
                description="You need to equip a vanity avatar or attach an image.",
                color=0xff0000))

            return
        
        else:
            try:
                if name in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys():
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"A closet entry with that name already exists.\n"
                                    f"See your closet entries with this command: "
                                    f"`var:see_closet`.",
                        color=0xff0000))

                if len(self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys()) >= 10:
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
                    self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].update({name: url})
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added attached file to your closet with name `{name}`."))

                elif self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]:
                    url = self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]
                    self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].update({name: url})
                    
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added current vanity avatar to closet with name `{name}`."))

            except KeyError or IndexError:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"] = {}

                try:
                    self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].update(
                        {name: self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]})
                
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
        
        try:
            if name not in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{name}` doesn't exist.\n"
                                f"View your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

            else:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].pop(name)

        except KeyError:
            self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"] = dict()
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with the name `{name}` doesn't exist.\n"
                            f"View your closet entries with this command: "
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

            elif name not in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{name}` doesn't exist.\n"
                                f"See your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

            elif rename in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{rename}` already exists.\n"
                                f"See your closet entries with this command: "
                                f"`var:see_closet`.",
                    color=0xff0000))

            else:
                orig_url = self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].pop(name)
                self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].update({rename: orig_url})

        except KeyError:
            self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"] = dict()
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
    async def see_closet(self, ctx: Context):
        
        check = await self.bot.get_user_vote(ctx.author.id)
            
        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "[Top.gg](https://top.gg/bot/687427956364279873/vote) and "
                            "click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments."))

        if not self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"]:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You have nothing in your closet.",
                color=0xff0000))
        
        message_part = []
        
        for i, url in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].items():
            message_part.append(
                f"▄ Name: {i}\n"
                f"▀ URL: ({url})\n"
                f"\n")
        
        return await ctx.send(embed=Embed(
            title="Your Closet",
            description=f"Here is your closet. You can use these anywhere. Used "
                        f"[{len(self.bot.user_data['UserData'][str(ctx.author.id)]['Closet'].keys())}/10] slots.\n"
                        f"```{newline.join(message_part)}```"
        ))

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

        if str(ctx.author.id) not in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys():
            self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"] = dict()

        try:
            if name in self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"].keys():
                dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
                await dummy.send(embed=Embed(
                    title="Preview",
                    description=f"{self.bot.user.name}: Preview message.\n",
                    color=0xff87a3
                ).set_image(url=self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"][name]),
                    avatar_url=self.bot.user_data["UserData"][str(ctx.author.id)]["Closet"][name])
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
                description="A closet entry with that name doesn't exist. "
                            "See your closet entries with this command: "
                            "`var:see_closet`.",
                color=0xff0000))
    
    # MODERATION
    @command(aliases=["s_bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    @has_permissions(manage_channels=True)
    async def server_blacklist(self, ctx: Context, mode: str, item: str = None):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider using "
                            "it in a private channel in one of your servers.",
                color=0xff0000))

        channeladd = ["channel-add", "ch-a"]
        channelremove = ["channel-remove", "ch-r"]
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if not item and (mode in channeladd or mode in channelremove):
            item = str(ctx.channel.id)
        
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
                channel = await self.bot.fetch_channel(item)

                if channel is None:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description=f"No channel with that ID exists. Try to #mention the channel instead.",
                        color=0xff0000))

                else:
                    if channel not in ctx.guild.channels:
                        return await ctx.send(embed=Embed(
                            title="Access Denied",
                            description="The channel has to be in this server. I wouldn't "
                                        "just let you cheese your friends like that in "
                                        "another server.",
                            color=0xff0000))
                    
                    if item not in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                        self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].append(item)
                        print(
                            f"+ Channel #{ctx.channel.name} ({ctx.channel.name}) was server-blacklisted by {ctx.author} ({ctx.author.id}).")

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

            if item in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].remove(item)
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

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Your prefix can only be up to 5 characters long.",
                    color=0xff0000))
        
            if item not in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].append(item)
                print(
                    f"+ Added \"{item}\" to blacklisted prefixes for {ctx.author} ({ctx.author.id})."
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
            if item in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].remove(item)
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
            if self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"] == (list(), list()):
                message_part.append(
                    "You haven't blacklisted anything for this server yet.")
                
                return True

            message_part.append(
                "Here are this server's blacklisted items:")
            if len(self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]) != 0:
                message_part.append("**Channels:**")
                for c_id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                    channel = guild.get_channel(c_id)
                    if channel:
                        message_part.append(
                            f"-- Name: {channel.mention}; ID: {channel.id}")
                    else:
                        self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].remove(i)
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

        if len(self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]) != 0:
            message_part.append("**Prefixes:**")
            for i in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
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
        message = []
        if guild.id in self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(guild.id)] and \
            self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(guild.id)]:
            message.append(
                "Here are users using vanities in this server; "
                "The list may contain members who have left:\n```")

            show_list = False
            for u_id in self.bot.user_data["UserData"]:
                if str(ctx.guild.id) in u_id["VanityAvatars"] and u_id["VanityAvatars"][0]:
                    user = self.bot.get_user(u_id)
                    if user:
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
    @has_permissions(manage_messages=True)
    @command(aliases=["manage", "user"])
    async def manage_user(self, ctx: Context, mode: str, user: Member):
        author_role = ctx.author.top_role
        
        if str(user.id) not in self.bot.user_data["UserData"] or \
            str(ctx.guild.id) not in self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"]:
            return await ctx.send(embed=Embed(
                title="Error",
                description="That user has no information linked with this server.",
                color=0xff0000))

        if user == ctx.author and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You cannot use this command on yourself.",
                color=0xff0000))

        if ctx.author.id != ctx.guild.owner_id and \
            ctx.guild.id in self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)] and \
            ctx.author.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"]:
            return await ctx.send(embed=Embed(
                title="Permission Error",
                description="You cannot use this command because you were blocked "
                            "from using vanity avatars by another user.",
                color=0xff0000))

        if not user:
            return await ctx.send(embed=Embed(
                title="Error",
                description="That user is not a part of this server or does not exist.",
                color=0xff0000))

        if ctx.author.id != ctx.guild.owner_id and author_role <= user.top_role:
            return await ctx.send(embed=Embed(
                title="Permission Error",
                description="You cannot manage this user because they have an "
                            "equal or higher role than you.",
                color=0xff0000))

        if mode == "block":
            if user.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That user is already blocked.",
                    color=0xff0000))

            else:
                self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][1] = \
                    self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][0]
                self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][0] = None
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"].append(user.id)
                return await ctx.send(embed=Embed(
                    title="Success",
                    description="User vanity avatar removed and blocked for this server."))

        elif mode == "unblock":
            if not user.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That user is already unblocked.",
                    color=0xff0000))

            else:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"].remove(user.id)
                return await ctx.send(embed=Embed(
                    title="Success",
                    description="User unblocked for this server."))

        elif mode == "get_info":
            return await ctx.send(embed=Embed(
                title="Info",
                description=f'__**Vanity status for user {str(user)}:**__\n'
                            f'Vanity url: {self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][0]}\n'
                            f'Previous url: {self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][1]}\n'
                            f'Is blocked:  {user.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"]}'))

    @see_blacklists.before_invoke
    @see_closet.before_invoke
    @see_server_blacklists.before_invoke
    async def placeholder_remove(self, ctx):
        if ctx.command.name == "see_blacklists":
            if 0 in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][0]:
                self.bot.user_data['UserData'][str(ctx.author.id)]['Blacklists'][0].remove(0)
            if "placeholder" in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][1]:
                self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][1].remove("placeholder")
        
        if ctx.command.name == "see_closet":
            if "placeholder" in self.bot.user_data['UserData'][str(ctx.author.id)]["Closet"].keys():
                self.bot.user_data['UserData'][str(ctx.author.id)]["Closet"].pop("placeholder")
        
        if ctx.guild and ctx.command.name == "see_server_blacklists":
            if 0 in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].remove(0)
            if "placeholder" in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].remove("placeholder")
    
    @see_blacklists.after_invoke
    @see_closet.after_invoke
    @see_server_blacklists.after_invoke
    async def placeholder_add(self, ctx):
        if ctx.command.name == "see_blacklists":
            if 0 not in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][0]:
                self.bot.user_data['UserData'][str(ctx.author.id)]['Blacklists'][0].append(0)
            if "placeholder" not in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][1]:
                self.bot.user_data['UserData'][str(ctx.author.id)]['Blacklists'][1].append("placeholder")
        
        if ctx.command.name == "see_closet":
            if "placeholder" not in self.bot.user_data['UserData'][str(ctx.author.id)]["Closet"].keys():
                self.bot.user_data['UserData'][str(ctx.author.id)]["Closet"]["placeholder"] = "placeholder"
        
        if ctx.guild and ctx.command.name == "see_server_blacklists":
            if 0 not in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].append(0)
            if "placeholder" not in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].append("placeholder")

def setup(bot):
    bot.add_cog(Commands(bot))
