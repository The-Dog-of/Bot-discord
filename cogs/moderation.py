import discord
from discord.ext import commands
import aiosqlite
from datetime import timedelta, datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, guild, embed):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT log_channel_id FROM settings WHERE guild_id = ?', (str(guild.id),))
            res = await cursor.fetchone()
        if res and res[0]:
            ch = guild.get_channel(int(res[0]))
            if ch: await ch.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel):
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, log_channel_id) VALUES (?, ?)', 
                             (str(ctx.guild.id), str(channel.id)))
            await db.commit()
        await ctx.send(f"📝 Logs channel set to {channel.mention}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, time_str: str, *, reason="No reason provided"):
        """Timeout a user (e.g. !mute @user 10m)"""
        unit = time_str[-1]
        val = int(time_str[:-1])
        delta = None
        
        if unit == 'm': delta = timedelta(minutes=val)
        elif unit == 'h': delta = timedelta(hours=val)
        elif unit == 'd': delta = timedelta(days=val)
        else: return await ctx.send("❌ Use format: `10m`, `2h`, `1d`.")

        await member.timeout(delta, reason=reason)
        await ctx.send(f"🤐 **{member}** muted for `{time_str}`.")
        
        embed = discord.Embed(title="🤐 User Muted", color=discord.Color.light_grey())
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Time", value=time_str)
        embed.add_field(name="Reason", value=reason)
        await self.log_action(ctx.guild, embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 **Channel Locked.**")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 **Channel Unlocked.**")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="N/A"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 **{member}** has been banned.")
        
        embed = discord.Embed(title="🔨 User Banned", color=discord.Color.red())
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Moderator", value=ctx.author.mention)
        embed.add_field(name="Reason", value=reason)
        await self.log_action(ctx.guild, embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount > 100: amount = 100
        await ctx.channel.purge(limit=amount+1)
        msg = await ctx.send(f"🧹 Cleared **{amount}** messages.", delete_after=3)

async def setup(bot):
    await bot.add_cog(Moderation(bot))