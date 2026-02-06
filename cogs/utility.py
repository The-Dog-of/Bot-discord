import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

class Utility(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="giveaway", description="Start a giveaway")
    @app_commands.describe(time="Duration (ex: 10s, 1m)", prize="Prize to win")
    async def giveaway(self, ctx, time: str, *, prize: str):
        unit = time[-1]
        try: val = int(time[:-1])
        except: return await ctx.send("❌ Use: 10s, 1m", ephemeral=True)
        
        seconds = val * (60 if unit == 'm' else 3600 if unit == 'h' else 1)
        
        embed = discord.Embed(title="🎉 GIVEAWAY", description=f"**Prize:** {prize}\n**Ends in:** {time}", color=discord.Color.purple())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        
        await asyncio.sleep(seconds)
        
        # Pega a mensagem atualizada para conferir reações
        try:
            msg = await ctx.channel.fetch_message(msg.id)
        except:
            return # Mensagem foi deletada

        users = [u async for u in msg.reactions[0].users() if not u.bot]
        
        if users:
            winner = random.choice(users)
            await ctx.send(f"🎊 Winner: {winner.mention} won **{prize}**!")
        else:
            await ctx.send(f"😢 Giveaway for **{prize}** ended. No participants.")

    @commands.hybrid_command(name="poll", description="Create a poll")
    async def poll(self, ctx, *, question: str):
        embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

async def setup(bot):
    await bot.add_cog(Utility(bot))