import datetime

import discord
from discord.ext import commands

from .utils import stuffs


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def column(self, num, res=""):
        return (
            self.column(
                (num - 1) // 26,
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()[(num - 1) % 26] + res,
            )
            if num > 0
            else res
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        m = await self.bot.db.fetch(
            "SELECT channel_id FROM config WHERE guild_id = $1", message.guild.id
        )
        try:
            if not message.channel.id == int(m[0]["channel_id"]):
                return
        except IndexError:
            return
        # -------------------------------------------------------
        # Check if it is a same person
        previous_person = await self.bot.db.fetch(
            "SELECT previous_person FROM counting WHERE guild_id = $1",
            message.guild.id,
        )
        if not previous_person:
            return
        if previous_person[0]["previous_person"] is None:
            await self.bot.db.execute(
                "UPDATE counting SET previous_person = $1 WHERE guild_id = $2",
                message.author.id,
                message.guild.id,
            )
            previous_person = await self.bot.db.fetch(
                "SELECT previous_person FROM counting WHERE guild_id = $1",
                message.guild.id,
            )
        elif int(previous_person[0]["previous_person"]) == message.author.id:
            is_same_person = await self.bot.db.fetch(
                "SELECT is_same_person FROM config WHERE guild_id = $1",
                message.guild.id,
            )
            if is_same_person[0]["is_same_person"]:
                return
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
            await self.bot.db.execute(
                "INSERT INTO logger (id, guild_id, channel_id, ruined_chain_id, ruiner_id, ruined_jump_url, ruined_content, when_ruined, reason, previous_chain_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                id,
                message.guild.id,
                message.channel.id,
                message.id,
                message.author.id,
                message.jump_url,
                message.content,
                now,
                "You can't chain alphabet count else this server will lose streak.",
                [a async for a in history][0].id,
            )
            await self.bot.db.execute(
                "UPDATE counting SET previous_person = $1, count_number =  $2 WHERE guild_id = $3",
                None,
                0,
                message.guild.id,
            )
            return
        # -------------------------------------------------------
        # Check if it is a chained message
        previous_count = await self.bot.db.fetch(
            "SELECT count_number FROM counting WHERE guild_id = $1", message.guild.id
        )
        expect = self.column(int(previous_count[0]["count_number"]) + 1)
        if message.content != expect:
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
            await self.bot.db.execute(
                "INSERT INTO logger (id, guild_id, channel_id, ruined_chain_id, ruiner_id, ruined_jump_url, ruined_content, when_ruined, reason, previous_chain_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                id,
                message.guild.id,
                message.channel.id,
                message.id,
                message.author.id,
                message.jump_url,
                message.content,
                now,
                "You broke the pattern.",
                [a async for a in message.channel.history(limit=1)][0].id,
            )
            return
        # -------------------------------------------------------
        # all condition were met so we can count
        previous_number = await self.bot.db.fetch(
            "SELECT count_number FROM counting WHERE guild_id = $1", message.guild.id
        )

        await self.bot.db.execute(
            "UPDATE counting SET previous_person = $1, count_number = $2 WHERE guild_id = $3",
            message.author.id,
            previous_number[0]["count_number"] + 1,
            message.guild.id,
        )
        await message.add_reaction("✅")


async def setup(bot: commands.Bot):
    await bot.add_cog(events(bot))