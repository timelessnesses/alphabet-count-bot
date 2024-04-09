import string
import typing

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from ..bot import IHatePylanceComplainsPleaseShutUp


class Leaderboard(commands.Cog):
    """
    Get a ranking of the top 10 users/servers!
    """

    def __init__(self, bot: "IHatePylanceComplainsPleaseShutUp") -> None:
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return "📊"

    def column(self, num: int, res="") -> str:
        return (
            self.column(
                (num - 1) // 26,
                string.ascii_lowercase[(num - 1) % 26] + res,
            )
            if num > 0
            else res
        )

    def prefix(self, n: int):
        return str(n) + (
            "th"
            if 4 <= n % 100 <= 20
            else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        )

    @commands.hybrid_group()
    async def leaderboard(self, _: commands.Context) -> None:
        """
        Leaderboard command group
        """

    @leaderboard.command()
    async def by_alphabet_counts(self, ctx: commands.Context):
        """
        Get every server's alphabet chain count that wasn't ruined ranked by most to the least in top 10!
        """
        if not ctx.guild:
            return
        await ctx.defer()
        servers = sorted(
            await self.bot.db.fetch("SELECT * FROM counting"),
            key=lambda x: x["count_number"],
            reverse=True,
        )[:10]
        all_guilds = sorted(
            await self.bot.db.fetch("SELECT * FROM counting"),
            key=lambda x: x["count_number"],
            reverse=True,
        )
        embed = discord.Embed(title="Top 10 Servers by Chain Count", color=0x00FF00)
        configs = await self.bot.db.fetch("SELECT * FROM config")
        for i, server in enumerate(servers):
            if server["count_number"] == 0:
                continue
            if server["guild_id"] in [x["guild_id"] for x in configs]:
                config = [x for x in configs if x["guild_id"] == server["guild_id"]][0]
                if config["is_same_person"] or config["save_count"]:  # unranked
                    continue
            embed.add_field(
                name=f"{self.prefix(i + 1)}. {await self.bot.fetch_guild(server['guild_id'])}",
                value=f"{server['count_number']} chains. (Currently at character {self.column(server['count_number'])})",
                inline=False,
            )
        i_ = -1
        server_ = {}
        for i, server in enumerate(all_guilds):
            if server["guild_id"] == ctx.guild.id:
                i_ = i
                server_ = server
                break
        try:
            embed.set_footer(
                text=f"{ctx.guild} is at currently at {self.prefix(i_ + 1)} and currently at character {self.column(server_['count_number'])}. {'But your server is unranked due to you enable save count or is same person.' if server_['guild_id'] in [x['guild_id'] for x in configs] and [x for x in configs if x['guild_id'] == server_['guild_id']][0]['is_same_person'] or server_['guild_id'] in [x['guild_id'] for x in configs] and [x for x in configs if x['guild_id'] == server_['guild_id']][0]['save_count'] else ''}"
            )
        except UnboundLocalError:
            pass
        await ctx.send(embed=embed)

    @leaderboard.command()
    async def by_contribution_alphabets(self, ctx: commands.Context):
        """
        Get letters count by alphabet ranked by most to the least in top 10!
        """
        await ctx.defer()
        users = sorted(
            await self.bot.db.fetch("SELECT * FROM user_stats"),
            key=lambda x: x["alphabet_counts"],
            reverse=True,
        )[:10]
        all_users = sorted(
            await self.bot.db.fetch("SELECT * FROM user_stats"),
            key=lambda x: x["alphabet_counts"],
            reverse=True,
        )
        embed = discord.Embed(title="Top 10 Users by Alphabet Count", color=0x00FF00)
        for i, user in enumerate(users):
            embed.add_field(
                name=f"{self.prefix(i + 1)}. {await self.bot.fetch_user(user['user_id'])}",
                value=f"{user['alphabet_counts']} letters.",
                inline=False,
            )
        i_ = -1
        user_ = {}
        for i, user in enumerate(all_users):
            if user["user_id"] == ctx.author.id:
                i_ = i
                user_ = user
                break
        try:
            embed.set_footer(
                text=f"{ctx.author} is at currently at {self.prefix(i_ + 1)} and currently have alphabet count at {user_['alphabet_counts']}."
            )
        except UnboundLocalError:
            pass
        await ctx.send(embed=embed)

    @leaderboard.command()
    async def by_longest_chain(self, ctx: commands.Context):
        """
        Get every server's alphabet chain count that's ruined ranked by most to the least in top 10!
        """
        if not ctx.guild:
            return
        await ctx.defer()
        servers = sorted(
            await self.bot.db.fetch("SELECT * FROM counting"),
            key=lambda x: x["longest_chain"],
            reverse=True,
        )[:10]
        all_guilds = sorted(
            await self.bot.db.fetch("SELECT * FROM counting"),
            key=lambda x: x["longest_chain"],
            reverse=True,
        )
        embed = discord.Embed(title="Top 10 Servers by Longest Chain", color=0x00FF00)
        configs = await self.bot.db.fetch("SELECT * FROM config")
        for i, server in enumerate(servers):
            if server["longest_chain"] == 0:
                continue
            if server["guild_id"] in [x["guild_id"] for x in configs]:
                config = [x for x in configs if x["guild_id"] == server["guild_id"]][0]
                if config["is_same_person"] or config["save_count"]:
                    continue
            embed.add_field(
                name=f"{self.prefix(i + 1)}. {await self.bot.fetch_guild(server['guild_id'])}",
                value=f"{server['longest_chain']} characters. (Currently at character {self.column(server['longest_chain'])})",
                inline=False,
            )
        i_ = -1
        server_ = {}
        for i, server in enumerate(all_guilds):
            if int(server["guild_id"]) == ctx.guild.id:
                i_ = i
                server_ = server
                break
        try:
            embed.set_footer(
                text=f"{ctx.guild} is at currently at {self.prefix(i_ + 1)} and currently at character {self.column(server_['longest_chain'])}. {'But your server is unranked due to you enable save count or is same person.' if server_['guild_id'] in [x['guild_id'] for x in configs] and [x for x in configs if x['guild_id'] == server_['guild_id']][0]['is_same_person'] or server_['guild_id'] in [x['guild_id'] for x in configs] and [x for x in configs if x['guild_id'] == server_['guild_id']][0]['save_count'] else ''}."
            )
        except UnboundLocalError:
            pass
        await ctx.send(embed=embed)


async def setup(bot: "IHatePylanceComplainsPleaseShutUp") -> None:
    await bot.add_cog(Leaderboard(bot))
