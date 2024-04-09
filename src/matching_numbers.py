import datetime
import typing

import asyncpg
import discord
from discord.ext import commands

from .utils import stuffs

if typing.TYPE_CHECKING:
    from ..bot import IHatePylanceComplainsPleaseShutUp


class events(commands.Cog):
    def __init__(self, bot: "IHatePylanceComplainsPleaseShutUp") -> None:
        self.bot = bot
        self.db: asyncpg.Pool = bot.db

    def column(self, num, res="") -> str:
        return (
            self.column(
                (num - 1) // 26,
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()[(num - 1) % 26] + res,
            )
            if num > 0
            else res
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        ctx = await self.bot.get_context(message)
        if ctx.guild is None:
            return
        try:
            async with self.db.acquire() as db:
                if message.author.bot:
                    return
                if message.guild is None:
                    return
                m = await db.fetch(
                    "SELECT channel_id FROM config WHERE guild_id = $1",
                    message.guild.id,
                )
                try:
                    if not message.channel.id == int(m[0]["channel_id"]):
                        return
                except IndexError:
                    return
                # -------------------------------------------------------
                # Check if it is a same person
                previous_person = await db.fetch(
                    "SELECT previous_person FROM counting WHERE guild_id = $1",
                    message.guild.id,
                )
                previous_count = await db.fetch(
                    "SELECT count_number FROM counting WHERE guild_id = $1",
                    message.guild.id,
                )
                if not previous_person:
                    return
                is_same_person = await db.fetch(
                    "SELECT is_same_person FROM config WHERE guild_id = $1",
                    message.guild.id,
                )
                if previous_person[0]["previous_person"] is None:
                    await db.execute(
                        "UPDATE counting SET previous_person = $1 WHERE guild_id = $2",
                        message.author.id,
                        message.guild.id,
                    )
                    previous_person = await db.fetch(
                        "SELECT previous_person FROM counting WHERE guild_id = $1",
                        message.guild.id,
                    )
                elif (
                    int(previous_person[0]["previous_person"]) == message.author.id
                    and is_same_person[0]["is_same_person"] != True
                ):
                    await ctx.message.add_reaction("❌")
                    id = stuffs.random_id()
                    now = datetime.datetime.now()
                    await message.channel.send(
                        embed=discord.Embed(
                            title="You can't chain alphabet count",
                            colour=discord.Colour.red(),
                        )
                        .add_field(
                            name="Reason",
                            value="You can't chain alphabet count else this server will lose streak.",
                        )
                        .add_field(
                            name="Log ID",
                            value=id,
                        )
                        .add_field(
                            name="Ruined by",
                            value=message.author.mention,
                        )
                        .add_field(
                            name="Time",
                            value=now.strftime("%Y/%m/%d %H:%M:%S"),
                        )
                        .add_field(
                            name="How to fix",
                            value="You can't chain alphabet count else this server will lose streak.",
                        )
                    )
                    history = message.channel.history(limit=1)
                    await db.execute(
                        "INSERT INTO logger (id, guild_id, channel_id, ruiner_id, ruined_jump_url, when_ruined, reason) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                        id,
                        message.guild.id,
                        message.channel.id,
                        message.author.id,
                        message.jump_url,
                        now,
                        "You can't chain alphabet count else this server will lose streak.",
                    )
                    await db.execute(
                        "UPDATE counting SET previous_person = $1, count_number =  $2 WHERE guild_id = $3",
                        None,
                        0,
                        message.guild.id,
                    )
                    current_count = await db.fetch(
                        "SELECT * FROM counting WHERE guild_id = $1", ctx.guild.id
                    )
                    if not current_count:
                        return
                    if (
                        previous_count[0]["count_number"] + 1
                        > current_count[0]["longest_chain"]
                        and previous_count[0]["count_number"] != 0
                    ):
                        await ctx.send(
                            embed=discord.Embed(
                                title="This server has broke personal streak",
                                description=f"Your previous chain count is {current_count[0]['longest_chain']}. Now it is {current_count[0]['count_number']}. Congratulation! 🥳",
                                colour=discord.Colour.green(),
                            )
                        )
                        await db.execute(
                            "UPDATE counting SET longest_chain = $1 WHERE guild_id = $2",
                            current_count[0]["count_number"],
                            ctx.guild.id,
                        )
                    current_highest_chain = await db.fetch("SELECT * FROM counting")
                    first_rank = sorted(
                        current_highest_chain,
                        key=lambda x: x["longest_chain"],
                        reverse=True,
                    )[0]
                    if (
                        first_rank["longest_chain"]
                        < previous_count[0]["count_number"] + 1
                    ):
                        await ctx.send(
                            embed=discord.Embed(
                                title=f"This server has broke global streak that was made by {await self.bot.fetch_guild(first_rank['guild_id'])}",
                                description=f"Previous world record is {first_rank['longest_chain']} from {(await self.bot.fetch_guild(first_rank['guild_id']))}. Now it is {current_count[0]['longest_chain']}. Congratulation! 🥳",
                                colour=discord.Colour.green(),
                            )
                        )
                        await db.execute(
                            "UPDATE counting SET longest_chain = $1 WHERE guild_id = $2",
                            current_count[0]["longest_chain"],
                            ctx.guild.id,
                        )
                    save_count = await db.fetch(
                        "SELECT * FROM config WHERE guild_id = $1", ctx.guild.id
                    )
                    if save_count[0]["save_count"]:
                        await db.execute(
                            "UPDATE counting SET count_number = $1 WHERE guild_id = $2",
                            current_count[0]["count_number"],
                            ctx.guild.id,
                        )
                    else:
                        await db.execute(
                            "UPDATE counting SET count_number = $1 WHERE guild_id = $2",
                            0,
                            ctx.guild.id,
                        )
                    return
                # -------------------------------------------------------
                # Check if it is a chained message
                expect = self.column(int(previous_count[0]["count_number"]) + 1)
                if message.content.lower() != expect:
                    await ctx.message.add_reaction("❌")
                    id = stuffs.random_id()
                    now = datetime.datetime.now()
                    await message.channel.send(
                        embed=discord.Embed(
                            title="You broke the pattern",
                            colour=discord.Colour.red(),
                        )
                        .add_field(
                            name="Reason",
                            value="You broke the pattern.",
                        )
                        .add_field(
                            name="Log ID",
                            value=id,
                        )
                        .add_field(
                            name="Ruined by",
                            value=message.author.mention,
                        )
                        .add_field(
                            name="Time",
                            value=now.strftime("%Y/%m/%d %H:%M:%S"),
                        )
                        .add_field(
                            name="How to fix",
                            value="You supposed to type `{}`".format(expect),
                        )
                    )
                    await db.execute(
                        "INSERT INTO logger (id, guild_id, channel_id, ruiner_id, ruined_jump_url, when_ruined, reason) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                        id,
                        message.guild.id,
                        message.channel.id,
                        message.author.id,
                        message.jump_url,
                        now,
                        "You broke the pattern.",
                    )  # TODO: this errored out
                    await db.execute(
                        "UPDATE counting SET previous_person = $1, count_number =  $2 WHERE guild_id = $3",
                        None,
                        0,
                        message.guild.id,
                    )

                    current_count = await db.fetch(
                        "SELECT * FROM counting WHERE guild_id = $1", ctx.guild.id
                    )
                    if not current_count:
                        return
                    if (
                        previous_count[0]["count_number"] + 1
                        > current_count[0]["longest_chain"]
                        and previous_count[0]["count_number"] != 0
                    ):
                        await ctx.send(
                            embed=discord.Embed(
                                title="This server has broke personal streak",
                                description=f"Your previous chain count is {current_count[0]['longest_chain']}. Now it is {previous_count[0]['count_number']+1}. Congratulation! 🥳",
                                colour=discord.Colour.green(),
                            )
                        )
                        await db.execute(
                            "UPDATE counting SET longest_chain = $1 WHERE guild_id = $2",
                            previous_count[0]["count_number"] + 1,
                            ctx.guild.id,
                        )
                    current_highest_chain = await db.fetch("SELECT * FROM counting")
                    first_rank = sorted(
                        current_highest_chain,
                        key=lambda x: x["longest_chain"],
                        reverse=True,
                    )[0]
                    if (
                        first_rank["longest_chain"]
                        < previous_count[0]["count_number"] + 1
                    ):
                        await ctx.send(
                            embed=discord.Embed(
                                title=f"This server has broke global streak that was made by {await self.bot.fetch_guild(first_rank['guild_id'])}",
                                description=f"Previous world record is {first_rank['longest_chain']}. Now it is {current_count[0]['longest_chain']}. Congratulation! 🥳",
                                colour=discord.Colour.green(),
                            )
                        )
                        await db.execute(
                            "UPDATE counting SET longest_chain = $1 WHERE guild_id = $2",
                            previous_count[0]["count_number"] + 1,
                            ctx.guild.id,
                        )

                    save_count = await db.fetch(
                        "SELECT * FROM config WHERE guild_id = $1", ctx.guild.id
                    )
                    if save_count[0]["save_count"]:
                        await db.execute(
                            "UPDATE counting SET count_number = $1 WHERE guild_id = $2",
                            previous_count[0]["count_number"] + 1,
                            ctx.guild.id,
                        )
                    else:
                        await db.execute(
                            "UPDATE counting SET count_number = $1 WHERE guild_id = $2",
                            0,
                            ctx.guild.id,
                        )
                    return
                # -------------------------------------------------------
                # all condition were met so we can count
                previous_number = await db.fetch(
                    "SELECT count_number FROM counting WHERE guild_id = $1",
                    message.guild.id,
                )

                await db.execute(
                    "UPDATE counting SET previous_person = $1, count_number = $2 WHERE guild_id = $3",
                    message.author.id,
                    previous_number[0]["count_number"] + 1,
                    message.guild.id,
                )
                await message.add_reaction("✅")
                if not (
                    await db.fetch(
                        "SELECT * FROM user_stats WHERE user_id = $1", message.author.id
                    )
                ):
                    await db.execute(
                        "INSERT INTO user_stats (user_id, alphabet_counts, ruined_counts) VALUES ($1, $2, $3)",
                        message.author.id,
                        0,
                        0,
                    )
                count = (
                    await db.fetch(
                        "SELECT * FROM user_stats WHERE user_id = $1", message.author.id
                    )
                )[0]["alphabet_counts"] + 1
                await db.execute(
                    "UPDATE user_stats SET alphabet_counts = $1 WHERE user_id = $2",
                    count,
                    message.author.id,
                )
        except Exception as e:
            await ctx.send(
                "Something went wrong with checking process! Please consider looking at log file."
            )
            raise e


async def setup(bot: "IHatePylanceComplainsPleaseShutUp"):
    await bot.add_cog(events(bot))
