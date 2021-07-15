from discord import Member, TextChannel, CategoryChannel, VoiceChannel
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import has_permissions, bot_has_permissions, command
from discord.user import User

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
                f'+ SET/CHANGED vanity avatar for '
                f'{ctx.author} ({ctx.author.id}) in server {ctx.guild.name} ({ctx.guild.id}).')

    @command(aliases=["remove"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def remove_vanity(self, ctx: Context):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))
        
        if str(ctx.guild.id) in self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"]:
            self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)] = [
                None, self.bot.user_data["UserData"][str(ctx.author.id)]["VanityAvatars"][str(ctx.guild.id)][0]]

            await ctx.send(embed=Embed(
                title="Success",
                description="Removed vanity."))
            
            print(
                f'- REMOVED vanity avatar for '
                f'{ctx.author} ({ctx.author.id}) in server {ctx.guild.name} ({ctx.guild.id}).')

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You don't have a vanity avatar on right now.",
                color=0xff0000))

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def current(self, ctx: Context, user: User = None, standard: str = None):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

        if standard not in ["standard", "standard_url"]:
            standard = None

        if not user:
            user = ctx.author

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

                    await ctx.channel.send(embed=Embed(
                        title=f"Vanity Avatar: {user}",
                        description="Their current vanity avatar is located here:\n",
                    ).set_image(url=self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][0]))

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
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

        if not url:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                await ctx.send(embed=Embed(
                    title="Input Error",
                    description=":x: You need to provide an image URL or attach a file.",
                color=0xff0000))
                return

        try:
            dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
            await dummy.send(embed=Embed(
                title="Preview",
                description=f"{self.bot.user.name}: Preview message.\n"
                            f"If the image does not load, there is an issue with your URL. It must lead directly to an image.",
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

        await ctx.send(embed=Embed(
            title="Quick delete",
            description=f"{'✅' if symbol else '❎'} Quick delete toggled!\n"))

    # BLACKLISTING
    @command(aliases=["bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def blacklist(self, ctx, mode = None, item = None):
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

        if not mode:
            if self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)] == [[], []]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You haven't blacklisted anything for this server yet.",
                    color=0xff0000))
            
            remove_queue = []
            emb = Embed(title="Blacklist")

            if self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                channels_list = []
                for n in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                    channel = self.bot.get_channel(n)
                    if not channel:
                        remove_queue.append(n)
                        continue

                    else:
                        if isinstance(channel, TextChannel):
                            channels_list.append(f"-- {channel.mention} `({channel.id})`")
                            
                        elif isinstance(channel, CategoryChannel):
                            channels_list.append(f"-- `{channel.name} ({channel.id})`")
                            
                for n in remove_queue:
                    self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0].remove(n)

                if self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                    emb.add_field(
                        name="**Channels:**",
                        inline=False, 
                        value="\n".join(channels_list)
                    )

            if self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1]:
                prefixes_list = []

                for i in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1]:
                    prefixes_list.append(f'-- `{i}`')

                emb.add_field(
                    name="**Prefixes:**",
                    inline=False, 
                    value="\n".join(prefixes_list)
                )

            await ctx.send(embed=emb)
            print(f'[] Sent blacklisted items for {ctx.author} ({ctx.author.id}).')

        elif mode in channeladd:
            if not item:
                channel == ctx.channel
                here = True
            else:
                if item.startswith("<#") and item.endswith(">"):
                    item = item.replace("<#", "")
                    item = item.replace(">", "")

                try:
                    item = int(item)
                except ValueError:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="`item` needs to be a number and proper channel ID.\n"
                                    "Try to #mention the channel instead if it is a text channel.",
                        color=0xff0000))
                
                    return

                channel = self.bot.get_channel(item)

                if not channel or isinstance(channel, VoiceChannel) or channel not in ctx.guild.channels:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="No text channel or category with that ID exists.\n"
                                    "Try to #mention the channel instead. Note that voice channels are not allowed.\n"
                                    "If you are trying to add a category, you have to have its ID.",
                        color=0xff0000))

                    return

                if channel.id == ctx.channel.id:
                    here = True
                else:
                    here = False

            if channel.id in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"{'This' if here else 'That'} channel is already blacklisted for you.",
                    color=0xff0000))

                return

            elif channel.category and \
                channel.category.id in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"{'This' if here else 'That'} channel is already blacklisted for you.\n"
                                f"{self.bot.get_emoji(818664266390700074)} Automatically blacklisted by an added category:\n"
                                f"`{channel.category.name} ({channel.category.id})`.",
                    color=0xff0000))
                
                return

            else:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0].append(channel.id)
                        
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f"{channel.mention} {'(here) ' if here else ''}was blacklisted for you.\n"
                                f"You can still use bot commands here."))

                print(f"+ Channel '{channel.name}' ({channel.id}) was blacklisted for {ctx.author} ({ctx.author.id}).")

                return
                

        elif mode in channelremove:
            if not item:
                channel == ctx.channel
                here = True
            else:
                if item.startswith("<#") and item.endswith(">"):
                    item = item.replace("<#", "")
                    item = item.replace(">", "")

                try:
                    item = int(item)
                except ValueError:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="`item` needs to be a number and proper channel ID.\n"
                                    "Try to #mention the channel instead if it is a text channel.",
                        color=0xff0000))
                
                    return

                channel = self.bot.get_channel(item)

                if not channel or isinstance(channel, VoiceChannel) or channel not in ctx.guild.channels:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="No text channel or category with that ID exists.\n"
                                    "Try to #mention the channel instead. Note that voice channels are not allowed.\n"
                                    "If you are trying to add a category, you have to have its ID.",
                        color=0xff0000))

                    return

                if channel.id == ctx.channel.id:
                    here = True
                else:
                    here = False

            if channel.id in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0].remove(channel.id)
                    
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f"{channel.mention} {'(here) ' if here else ''}was unblacklisted for you."))

                print(f"- Channel '{channel.name}' ({channel.id}) was unblacklisted for {ctx.author} ({ctx.author.id}).")
                
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"{'This' if here else 'That'} channel isn't in your blacklist.\n"
                                f"Type `var:blacklist` with no arguments to see your "
                                f"blacklisted channels and prefixes.",
                    color=0xff0000))
                    
                return

        elif mode in prefixadd:
            if len(item) > 10:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="Your prefix can only be up to 10 characters long.",
                    color=0xff0000))

                return

            if item not in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1]:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1].append(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Added "{item}" to blacklisted prefixes for you.'))

                print(f'+ Added "{item}" to blacklisted prefixes for {ctx.author} ({ctx.author.id}).')

                return
            
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for you.",
                    color=0xff0000))

                return

        elif mode in prefixremove:
            if item in self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1]:
                self.bot.user_data["UserData"][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1].remove(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Removed "{item}" from blacklisted prefixes for you.'))

                print(f'- Removed "{item}" from blacklisted prefixes for {ctx.author} ({ctx.author.id}).')

                return
            
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`{item}` isn't in your blacklist.\n"
                                f"Type `var:see_blacklists` to see your blacklisted channels and prefixes.",
                    color=0xff0000))
                
                return

        else:
            await ctx.send(embed=Embed(
                title="Argument Error",
                description=f'Invalid mode passed: `{mode}`. See [blacklisting](https://github.com/SUPERMECHM500/Ram-Rebase-#blacklist-aliases-bl).',
                color=0xff0000))

            return

    # CLOSETS
    @command(aliases=["cl_add"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def add_to_closet(self, ctx: Context, *, name: str):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

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
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

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
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel.\n"
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000))

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
    async def server_blacklist(self, ctx, mode = None, item = None):
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

        if not mode:
            if self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"] == [[], []]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You haven't blacklisted anything for this server yet.",
                    color=0xff0000))
            
            remove_queue = []
            emb = Embed(title="Blacklist")

            if self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                channels_list = []
                for n in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                    channel = self.bot.get_channel(n)
                    if not channel:
                        remove_queue.append(n)
                        continue

                    else:
                        if isinstance(channel, TextChannel):
                            channels_list.append(f"-- {channel.mention} `({channel.id})`")
                            
                        elif isinstance(channel, CategoryChannel):
                            channels_list.append(f"-- `{channel.name} ({channel.id})`")
                            
                for n in remove_queue:
                    self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].remove(n)

                if self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                    emb.add_field(
                        name="**Channels:**",
                        inline=False, 
                        value="\n".join(channels_list)
                    )

            if self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                prefixes_list = []

                for i in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                    prefixes_list.append(f'-- `{i}`')

                emb.add_field(
                    name="**Prefixes:**",
                    inline=False, 
                    value="\n".join(prefixes_list)
                )

            await ctx.send(embed=emb)
            print(f'[] Sent blacklisted items for {ctx.guild} ({ctx.guild.id}).')

        elif mode in channeladd:
            if not item:
                channel == ctx.channel
                here = True
            else:
                if item.startswith("<#") and item.endswith(">"):
                    item = item.replace("<#", "")
                    item = item.replace(">", "")

                try:
                    item = int(item)
                except ValueError:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="`item` needs to be a number and proper channel ID.\n"
                                    "Try to #mention the channel instead if it is a text channel.",
                        color=0xff0000))
                
                    return

                channel = self.bot.get_channel(item)

                if not channel or isinstance(channel, VoiceChannel) or channel not in ctx.guild.channels:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="No text channel or category with that ID exists.\n"
                                    "Try to #mention the channel instead. Note that voice channels are not allowed.\n"
                                    "If you are trying to add a category, you have to have its ID.",
                        color=0xff0000))

                    return

                if channel.id == ctx.channel.id:
                    here = True
                else:
                    here = False

            if channel.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"{'This' if here else 'That'} channel is already blacklisted for this server.",
                    color=0xff0000))

                return

            elif channel.category and \
                channel.category.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"{'This' if here else 'That'} channel is already blacklisted for this server.\n"
                                f"{self.bot.get_emoji(818664266390700074)} Automatically blacklisted by an added category:\n"
                                f"`{channel.category.name} ({channel.category.id})`.",
                    color=0xff0000))
                
                return

            else:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].append(channel.id)
                        
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f"{channel.mention} {'(here) ' if here else ''}was blacklisted for this server.\n"
                                f"You can still use bot commands here."))

                print(f"+ Channel '{channel.name}' ({channel.id}) was blacklisted for {ctx.guild} ({ctx.guild.id}).")

                return
                

        elif mode in channelremove:
            if not item:
                channel == ctx.channel
                here = True
            else:
                if item.startswith("<#") and item.endswith(">"):
                    item = item.replace("<#", "")
                    item = item.replace(">", "")

                try:
                    item = int(item)
                except ValueError:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="`item` needs to be a number and proper channel ID.\n"
                                    "Try to #mention the channel instead if it is a text channel.",
                        color=0xff0000))
                
                    return

                channel = self.bot.get_channel(item)

                if not channel or isinstance(channel, VoiceChannel) or channel not in ctx.guild.channels:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="No text channel or category with that ID exists.\n"
                                    "Try to #mention the channel instead. Note that voice channels are not allowed.\n"
                                    "If you are trying to add a category, you have to have its ID.",
                        color=0xff0000))

                    return

                if channel.id == ctx.channel.id:
                    here = True
                else:
                    here = False

            if channel.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].remove(channel.id)
                    
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f"{channel.mention} {'(here) ' if here else ''}was unblacklisted for this server."))

                print(f"- Channel '{channel.name}' ({channel.id}) was unblacklisted for {ctx.guild} ({ctx.guild.id}).")
                
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"{'This' if here else 'That'} channel isn't in this server's blacklist.\n"
                                f"Type `var:blacklist` with no arguments to see this server's blacklisted channels and prefixes.",
                    color=0xff0000))
                    
                return

        elif mode in prefixadd:
            if len(item) > 10:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="Your prefix can only be up to 10 characters long.",
                    color=0xff0000))

                return

            if item not in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].append(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Added "{item}" to blacklisted prefixes for this server.'))

                print(f'+ Added "{item}" to blacklisted prefixes for {ctx.guild} ({ctx.guild.id}).')

                return
            
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for this server.",
                    color=0xff0000))

                return

        elif mode in prefixremove:
            if item in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].remove(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Removed "{item}" from blacklisted prefixes for this server.'))

                print(f'- Removed "{item}" from blacklisted prefixes for {ctx.guild} ({ctx.guild.id}).')

                return
            
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`{item}` isn't in this server's blacklist.\n"
                                f"Type `var:see_blacklists` to see this server's blacklisted channels and prefixes.",
                    color=0xff0000))
                
                return

        else:
            await ctx.send(embed=Embed(
                title="Argument Error",
                description=f'Invalid mode passed: `{mode}`. See [server_blacklisting](https://github.com/SUPERMECHM500/Ram-Rebase-#server_blacklist-aliases-s_bl).',
                color=0xff0000))

            return

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def list(self, ctx):
 
        message_part = []
        remove_queue = []

        for uid in self.bot.user_data["UserData"]:
            if str(ctx.guild.id) in self.bot.user_data["UserData"][uid]["VanityAvatars"] and \
                self.bot.user_data["UserData"][uid]["VanityAvatars"][str(ctx.guild.id)][0]:
                    
                member = ctx.guild.get_member(int(uid))
                if not member:
                    try: member = await ctx.guild.fetch_member(int(uid))
                    except NotFound: member = None

                if member:
                    url = self.bot.user_data["UserData"][uid]['VanityAvatars'][str(ctx.guild.id)][0]
                    filename = url.split("/")[-1]

                    message_part.append(
                        f"▌{member.mention} - URL: \n"
                        f"▌[{filename}]({url})\n"
                        f"")
                else:
                    remove_queue.append(uid)
            
        for uid in remove_queue:
            self.bot.user_data["UserData"][uid]["VanityAvatars"].pop(str(ctx.guild.id))

        if not message_part:
            return await ctx.send(embed=Embed(
                title="No Result",
                description="This server has no users with equipped vanities."
            ))

            return

        await ctx.send(embed=Embed(
            title="Server Equipped Vanities",
            description="Here are users using vanities in this server\n"
                        f"{newline.join(message_part)}"))

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
                description=f'__**Vanity status for {str(user)}:**__\n'
                            f'Vanity url: {self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][0]}\n'
                            f'Previous url: {self.bot.user_data["UserData"][str(user.id)]["VanityAvatars"][str(ctx.guild.id)][1]}\n'
                            f'Is blocked:  {user.id in self.bot.user_data["GuildData"][str(ctx.guild.id)]["BlockedUsers"]}'))

    @blacklist.before_invoke
    @see_closet.before_invoke
    @server_blacklist.before_invoke
    async def placeholder_remove(self, ctx):
        if ctx.command.name == "blacklist":
            if str(ctx.guild.id) not in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"]:
                return
                
            if 0 in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                self.bot.user_data['UserData'][str(ctx.author.id)]['Blacklists'][str(ctx.guild.id)][0].remove(0)
            if "placeholder" in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1]:
                self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1].remove("placeholder")
        
        if ctx.command.name == "see_closet":
            if "placeholder" in self.bot.user_data['UserData'][str(ctx.author.id)]["Closet"].keys():
                self.bot.user_data['UserData'][str(ctx.author.id)]["Closet"].pop("placeholder")
        
        if ctx.guild and ctx.command.name == "server_blacklist":
            if 0 in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][0].remove(0)
            if "placeholder" in self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1]:
                self.bot.user_data["GuildData"][str(ctx.guild.id)]["ServerBlacklists"][1].remove("placeholder")
    
    @blacklist.after_invoke
    @see_closet.after_invoke
    @server_blacklist.after_invoke
    async def placeholder_add(self, ctx):
        if ctx.command.name == "blacklist":
            if 0 not in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][0]:
                self.bot.user_data['UserData'][str(ctx.author.id)]['Blacklists'][str(ctx.guild.id)][0].append(0)
            if "placeholder" not in self.bot.user_data['UserData'][str(ctx.author.id)]["Blacklists"][str(ctx.guild.id)][1]:
                self.bot.user_data['UserData'][str(ctx.author.id)]['Blacklists'][str(ctx.guild.id)][1].append("placeholder")
        
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
