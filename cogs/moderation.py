import discord
from discord.ext import commands
from discord import app_commands # Necessário para descrições dos parâmetros
import aiosqlite
from datetime import timedelta

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

    @commands.hybrid_command(name="setlogs", description="Define the channel for logs")
    @app_commands.describe(channel="Channel to send logs to")
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel):
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, log_channel_id) VALUES (?, ?)', 
                             (str(ctx.guild.id), str(channel.id)))
            await db.commit()
        await ctx.send(f"📝 Logs channel set to {channel.mention}")

    @commands.hybrid_command(name="ban", description="Ban a user")
    @app_commands.describe(member="User to ban", reason="Reason for ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 Banned", description=f"**User:** {member}\n**Reason:** {reason}", color=discord.Color.red())
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, embed)

    @commands.hybrid_command(name="kick", description="Kick a user")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.kick(reason=reason)
        embed = discord.Embed(title="👢 Kicked", description=f"**User:** {member}\n**Reason:** {reason}", color=discord.Color.orange())
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, embed)

    @commands.hybrid_command(name="mute", description="Timeout/Mute a user (ex: 10m, 1h)")
    @app_commands.describe(time="Duration (e.g., 10m, 1h)", reason="Reason")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, time: str, *, reason: str = "No reason"):
        unit = time[-1]
        try: val = int(time[:-1])
        except: return await ctx.send("❌ Use format: 10m, 1h", ephemeral=True)
        
        delta = None
        if unit == 'm': delta = timedelta(minutes=val)
        elif unit == 'h': delta = timedelta(hours=val)
        elif unit == 'd': delta = timedelta(days=val)
        else: return await ctx.send("❌ Units: m, h, d", ephemeral=True)

        await member.timeout(delta, reason=reason)
        embed = discord.Embed(title="🤐 Muted", description=f"**User:** {member}\n**Time:** {time}", color=discord.Color.dark_grey())
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, embed)

    @commands.hybrid_command(name="purge", description="Delete messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount > 100: amount = 100
        # Defer serve para avisar que vai demorar (Slash) ou mostrar digitando (Texto)
        await ctx.defer(ephemeral=True) 
        deleted = await ctx.channel.purge(limit=amount)
        # No Slash isso responde só pra você, no texto manda no chat normal
        await ctx.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True, delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))