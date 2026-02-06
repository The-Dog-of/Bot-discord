import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Get details about a user")
    async def userinfo(self, ctx, member: discord.Member = None):
        user = member or ctx.author
        embed = discord.Embed(color=user.color)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Joined", value=user.joined_at.strftime("%Y-%m-%d"))
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Get server statistics")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=guild.name, color=0x2b2d31)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Owner", value=guild.owner.mention)
        await ctx.send(embed=embed)

async def setup(bot): await bot.add_cog(Info(bot))