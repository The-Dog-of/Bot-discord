import discord
from discord.ext import commands
import aiosqlite
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, guild, title, description, color):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT log_channel_id FROM settings WHERE guild_id = ?', (str(guild.id),))
            result = await cursor.fetchone()
        if result and result[0]:
            channel = guild.get_channel(int(result[0]))
            if channel:
                embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
                await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel):
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, log_channel_id) VALUES (?, ?)', 
                             (str(ctx.guild.id), str(channel.id)))
            await db.commit()
        await ctx.send(f"📝 Logs definidos em {channel.mention}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, motivo="N/A"):
        await member.ban(reason=motivo)
        await ctx.send(f"🚫 {member} banido.")
        await self.log_action(ctx.guild, "🔨 Banimento", f"Alvo: {member}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.red())

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def limpar(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"🧹 {len(deleted)-1} mensagens apagadas.", delete_after=5)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, motivo="N/A"):
        await member.kick(reason=motivo)
        await ctx.send(f"👢 {member} expulso.")
        await self.log_action(ctx.guild, "👢 Expulsão", f"Alvo: {member}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.orange())

async def setup(bot):
    await bot.add_cog(Moderation(bot))