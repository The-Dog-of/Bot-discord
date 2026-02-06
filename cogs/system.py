import discord
from discord.ext import commands
from discord import app_commands
from discord import ui

class HelpSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", emoji="🛡️", value="mod"),
            discord.SelectOption(label="Economy", emoji="💰", value="eco"),
            discord.SelectOption(label="Utility", emoji="🎉", value="util"),
            discord.SelectOption(label="AI", emoji="🧠", value="ai")
        ]
        super().__init__(placeholder="Select category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        embed = discord.Embed(color=0x2b2d31)
        if val == "mod":
            embed.title = "🛡️ Moderation"
            embed.description = "`/ban`, `/kick`, `/mute`, `/purge`, `/setlogs`"
        elif val == "eco":
            embed.title = "💰 Economy"
            embed.description = "`/work`, `/daily`, `/balance`"
        elif val == "util":
            embed.title = "🎉 Utility"
            embed.description = "`/giveaway`, `/poll`"
        elif val == "ai":
            embed.title = "🧠 AI"
            embed.description = "`/ask`"
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

class System(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="ping", description="Bot latency")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`")

    @commands.hybrid_command(name="help", description="Show commands")
    async def help(self, ctx):
        embed = discord.Embed(title="Help Center", description="Select a module below", color=0x2b2d31)
        await ctx.send(embed=embed, view=HelpView())

async def setup(bot): await bot.add_cog(System(bot))