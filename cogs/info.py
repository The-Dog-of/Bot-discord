import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['user', 'av'])
    async def userinfo(self, ctx, member: discord.Member = None):
        if not member: member = ctx.author
        
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        
        embed = discord.Embed(color=member.color)
        embed.set_author(name=f"{member.name}'s Profile", icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="📅 Registered", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="📥 Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=", ".join(roles[:5]) if roles else "None", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['server', 'si'])
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"🏰 {guild.name}", color=0x2b2d31)
        
        if guild.icon: embed.set_thumbnail(url=guild.icon.url)
        if guild.banner: embed.set_image(url=guild.banner.url)

        embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))