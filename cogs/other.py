from discord.ext import commands
from db import DB
from views.poll import Poll
from views.help import HelpView
import constants, tools.other, os, ai, logger, checks, discord


class Other(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = DB()

    @commands.command()
    async def help(self, ctx: commands.Context, page: str | None) -> None:
        if page and page in constants.HELP_PAGES:
            embed = tools.other.create_embed(constants.HELP_PAGES[page])
        else:
            embed = tools.other.create_embed(constants.HELP_PAGES["main"])

        await ctx.reply(embed=embed, view=HelpView(sender=ctx.author.id))

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.reply(f":ping_pong: `{tools.other.ping()}`")

    @commands.command()
    @checks.ownerOrPerms(
        manage_channels=True,
        manage_messages=True,
        send_messages=True,
    )
    async def poll(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel | None,
        poll: str | None,
        options: str | None,
    ) -> None:
        help_page = tools.other.create_embed(constants.POLL_HELP_PAGE)

        if not channel or not poll or not options:
            await ctx.reply(embed=help_page)
            return

        try:
            options_int = int(options)
        except:
            await ctx.reply(embed=help_page)
            return

        if options_int > 10 or options_int < 1:
            await ctx.reply(embed=help_page)
            return

        embed = discord.Embed(
            title=f"Poll by {ctx.message.author.display_name}",
            description=poll,
            color=discord.Color.random(),
        )

        await channel.send(
            embed=embed,
            view=Poll(options=list(range(1, options_int + 1)), msg=poll),
        )

    @commands.command("ai-reset")
    async def aireset(self, ctx: commands.Context):
        self.db.clear_msg_history(ctx.channel.id)
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def contributors(self, ctx: commands.Context):
        await ctx.reply(embed=tools.other.create_embed(constants.CONTRIBUTORS))

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if not self.bot.user:
            return

        if msg.author.id == self.bot.user.id:
            return

        if self.bot.user in msg.mentions:
            async with msg.channel.typing():
                res = await ai.send(
                    msg,
                    self.bot.user,
                )

            await msg.reply(res)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Other(bot))
