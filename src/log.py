import typing

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from ..bot import IHatePylanceComplainsPleaseShutUp


class Log(commands.Cog, name="Logs"):
    """
    Get ruined logs here!
    """

    def __init__(self, bot: "IHatePylanceComplainsPleaseShutUp") -> None:
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return "📝"

    @commands.hybrid_command()
    async def get_log(self, ctx: commands.Context, log_id: int) -> None:
        """
        Get the log of a specific log id
        """
        if not ctx.guild:
            return
        log = await self.bot.db.fetch(
            "SELECT * FROM logger WHERE guild_id = $1 AND id = $2",
            ctx.guild.id,
            log_id,
        )
        if not log:
            await ctx.send(
                embed=discord.Embed(
                    title="Log not found",
                    description="Log not found",
                    colour=discord.Colour.red(),
                )
            )
            return
        selected = log[0]
        embed = discord.Embed(
            title="Log info of {}".format(selected["id"]),
        )
        channel = (await ctx.guild.fetch_channel(selected["channel_id"])).mention
        embed.add_field(name="Channel", value=channel)
        ruined_author = (await self.bot.fetch_user(selected["ruiner_id"])).mention
        embed.add_field(name="Ruined by", value=ruined_author)
        embed.add_field(
            name="Ruined at",
            value=selected["when_ruined"].strftime("%Y/%m/%d %H:%M:%S"),
        )
        embed.add_field(name="Reason", value=selected["reason"])
        embed.add_field(
            name="Jump to ruined message", value=selected["ruined_jump_url"]
        )
        embed.set_footer(text=">:(")
        await ctx.send(embed=embed)


async def setup(bot: "IHatePylanceComplainsPleaseShutUp"):
    await bot.add_cog(Log(bot))
