from sys import exc_info
from copy import deepcopy

from discord.embeds import Embed
from discord.ext.commands import command
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import group, is_owner
from discord.ext.commands.errors import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError
)


class Admin(Cog):
    """Administrative Commands"""

    def __init__(self, bot):
        self.bot = bot

    @is_owner()
    @group(name="module", aliases=["cog", "mod"], invoke_without_command=True)
    async def module(self, ctx: Context):
        """Base command for managing bot modules

        Use without subcommand to list currently loaded modules"""

        modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
        space = len(max(modules.keys(), key=len))

        fmt = "\n".join([f"{module}{' ' * (space - len(module))} : {cog}" for module, cog in modules.items()])

        em = Embed(
            title="Administration: Currently Loaded Modules",
            description=f"```py\n{fmt}\n```",
            color=0x00ff00
        )
        await ctx.send(embed=em)

    @is_owner()
    @module.command(name="load", usage="(module name)")
    async def load(self, ctx: Context, module: str):
        """load a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"

        try:
            self.bot.load_extension(module)

        except ExtensionNotFound:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xff0000
            )

        except ExtensionAlreadyLoaded:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionAlreadyLoaded__**\n"
                            f"Module `{module}` is already loaded",
                color=0xff0000
            )

        except NoEntryPointError:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xff0000
            )

        except ExtensionFailed as error:
            if isinstance(error.original, TypeError):
                em = Embed(
                    title="Administration: Load Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"The cog loaded by `{module}` must be a subclass of discord.ext.commands.Cog",
                    color=0xff0000
                )
            else:
                em = Embed(
                    title="Administration: Load Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"An execution error occurred during module `{module}`'s setup function",
                    color=0xff0000
                )

                try:
                    try:
                        raise error.original
                    except AttributeError:
                        raise error
                except Exception:
                    error = exc_info()
                
                await self.bot.errorlog.send(error, ctx=ctx, event="Load Module")

        except Exception as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xff0000
            )
            
            error = exc_info()
            await self.bot.errorlog.send(error, ctx=ctx, event="Load Module")

        else:
            em = Embed(
                title="Administration: Load Module",
                description=f"Module `{module}` loaded successfully",
                color=0x00ff00
            )
            print(f"[] Loaded module \"{module}\".")

        await ctx.send(embed=em)

    @is_owner()
    @module.command(name="unload", usage="(module name)")
    async def unload(self, ctx: Context, module: str):
        """Unload a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"

        try:
            self.bot.unload_extension(module)

        except ExtensionNotLoaded:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__ExtensionNotLoaded__**\n"
                            f"Module `{module}` is not loaded",
                color=0xff0000
            )

        except Exception as error:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xff0000
            )

            try:
                try:
                    raise error.original
                except AttributeError:
                    raise error
            except Exception:
                error = exc_info()
            
            await self.bot.errorlog.send(error, ctx=ctx, event="Unload Module")

        else:
            em = Embed(
                title="Administration: Unload Module",
                description=f"Module `{module}` unloaded successfully",
                color=0x00ff00
            )
            print(f"[] Unloaded module \"{module}\".")
        
        await ctx.send(embed=em)

    @is_owner()
    @module.command(name="reload", usage="(module name)")
    async def reload(self, ctx: Context, module: str):
        """Reload a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"

        try:
            self.bot.reload_extension(module)

        except ExtensionNotLoaded:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotLoaded__**\n"
                            f"Module `{module}` is not loaded",
                color=0xff0000
            )

        except ExtensionNotFound:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xff0000
            )

        except NoEntryPointError:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xff0000
            )

        except ExtensionFailed as error:
            if isinstance(error.original, TypeError):
                em = Embed(
                    title="Administration: Reload Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"The cog loaded by `{module}` must be a subclass of discord.ext.commands.Cog",
                    color=0xff0000
                )
            else:
                em = Embed(
                    title="Administration: Reload Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"An execution error occurred during module `{module}`'s setup function",
                    color=0xff0000
                )

            try:
                try:
                    raise error.original
                except AttributeError:
                    raise error
            except Exception:
                error = exc_info()
            
            await self.bot.errorlog.send(error, ctx=ctx, event="Reload Module")

        except Exception as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xff0000
            )

            error = exc_info()
            await self.bot.errorlog.send(error, ctx=ctx, event="Reload Module")

        else:
            em = Embed(
                title="Administration: Reload Module",
                description=f"Module `{module}` reloaded successfully",
                color=0x00ff00
            )
            print(f"[] Reloaded module \"{module}\".")
    
        await ctx.send(embed=em)

    @is_owner()
    @command()
    async def config(self, ctx: Context, mode="view", setting=None, new_value=None):
        """View and change bot settings"""
        if mode == "view":
            message_lines = list()

            for setting, value in self.bot.config.items():
                message_lines.append(f"{setting}:\n{type(value).__name__}({value})")
            
            message_lines.insert(0, "```")
            message_lines.append("```")
            
            newline = "\n"
            em = Embed(
                title="Administration: Config",
                description=f"The options and values are listed below:\n"
                            f"{str(newline+newline).join(message_lines)}",
                color=0x0000ff)
            
            return await ctx.send(embed=em)
        
        elif mode == "change":
            if not setting or not new_value:
                return await ctx.send("Specify the setting and value to change.")
            
            if setting not in self.bot.config:
                return await ctx.send("That setting option doesn't exist.")

            if type(self.bot.config[setting]).__name__ == "int":
                try: self.bot.config[setting] = int(new_value)
                except ValueError: 
                    return await ctx.send("Invalid value type. Setting value should be of type `int`.")
            
            elif type(self.bot.config[setting]).__name__ == "float":
                try: self.bot.config[setting] = float(new_value)
                except ValueError: 
                    return await ctx.send("Invalid value type. Setting value should be of type `float`.")
            
            elif type(self.bot.config[setting]).__name__ == "bool":
                if new_value == "True":
                    self.bot.config[setting] = True
                elif new_value == "False":
                    self.bot.config[setting] = False
                else: 
                    return await ctx.send("Invalid value type. Setting value should be of type `bool`.")
            
            else:
                return await ctx.send(f"Unknown config value type ({type(self.bot.config[setting]).__name__}).")
            
            await ctx.send(f"Changed `{setting}` to `{new_value}`")

def setup(bot):
    bot.add_cog(Admin(bot))
