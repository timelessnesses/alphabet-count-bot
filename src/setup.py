import typing

import discord
from discord.ext import commands

from .utils import stuffs

if typing.TYPE_CHECKING:
    from ..bot import IHatePylanceComplainsPleaseShutUp


class setup_(commands.Cog, name="Setup"):
    """
    Alphabet's config command group
    """

    def __init__(self, bot: "IHatePylanceComplainsPleaseShutUp") -> None:
        self.bot = bot

    @property
    def display_emoji(self):
        return "🔨"

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context) -> None:
        """
        Setup the alphabet counter
        """
        if not ctx.guild:
            return
        is_setupped = await self.bot.db.fetch(
            "SELECT * FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not is_setupped:
            pass
        elif is_setupped[0]["already_setupped"]:
            view = stuffs.Confirm()
            await ctx.send(
                embed=discord.Embed(
                    title="Already set",
                    description="You have already set up Letter Counting this server. This command will override your previous settings. Do you want to do that?",
                ),
                view=view,
            )
            await view.wait()
            if view.value:
                await self.bot.db.execute(
                    "DELETE FROM config WHERE guild_id = $1", ctx.guild.id
                )
                await self.bot.db.execute(
                    "DELETE FROM counting WHERE guild_id = $1", ctx.guild.id
                )
                await ctx.send(
                    embed=discord.Embed(
                        title="Resetted",
                        colour=discord.Colour.green(),
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title="Cancelled",
                        colour=discord.Colour.red(),
                    )
                )
        await ctx.send(
            embed=discord.Embed(
                title="Letter Counting Setup",
                description="""
                This command will ask you
                1. Mention a channel
                2. Can person counting without checking if it is a same person (Unranked if enabled) (true/false)
                3. Save the count (Unranked if enabled) (true/false)
                """,
                colour=discord.Colour.green(),
            ),
        )
        ask = [
            "channel",
            "same_person",
            "save_count",
        ]
        answers = {}
        a = None
        j = None
        for i in ask:
            a = await ctx.send(
                embed=discord.Embed(
                    title="Please answer {}".format(i), colour=discord.Colour.green()
                )
            )
            answer = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author
            )

            if i == "channel":
                answers[i] = int(answer.content.strip("<#>"))
                j = answer
            else:
                answers[i] = True if answer.content.lower() == "true" else False
            await a.delete()
        if j is not None:
            channel = j
        else:
            return
        await self.bot.db.execute(
            """
            INSERT INTO config (guild_id, is_same_person, already_setupped, channel_id, save_count)
            VALUES ($1, $2, $3, $4, $5)
            """,
            ctx.guild.id,
            answers["same_person"],
            True,
            answers["channel"],
            answers["save_count"],
        )
        await ctx.send(
            embed=discord.Embed(
                title="Setupped",
                description=f"""
                You have setupped this server.
                Now {channel.content} will be enforced to count alphabet.
                """,
                colour=discord.Colour.green(),
            )
        )
        channel = await ctx.guild.fetch_channel(int(channel.content.strip("<#>")))
        message = await channel.send(
            embed=discord.Embed(
                title="Alphabet Count Rules",
                description=f"""
                This channel has been claimed for alphabet count
                Here's some rules
                1. {"You can't chain alphabet count else this server will lose streak." if not answers["same_person"] else "You can chain alphabet count."}
                2. You can't broke counting chain by typing anything other than alphabet else you will lose streak.
                3. You can't make conversation in this channel else this server will lose streak.
                """,
                colour=discord.Colour.green(),
            )
        )
        message2 = await channel.send(
            embed=discord.Embed(
                title="Alphabet Count Howto",
                description="""
                Pattern:
                ```
                A
                B
                ...
                Z
                ```
                But if you reached the end of alphabet, the next format should be something like this
                ```
                AA
                AB
                ...
                AZ
                ```
                or
                ```
                BA
                BB
                ...
                BZ
                ```
                If any of you broke the pattern, the server streak will be ended and ended streak will be logged.
                """,
                colour=discord.Colour.green(),
            )
        )
        await message.pin()
        await message2.pin()
        await self.bot.db.execute(
            "INSERT INTO counting (guild_id, count_number, count_channel_id, previous_person) VALUES ($1, $2, $3, $4)",
            ctx.guild.id,
            0,
            channel.id,
            None,
        )


async def setup(bot: "IHatePylanceComplainsPleaseShutUp"):
    await bot.add_cog(setup_(bot))
