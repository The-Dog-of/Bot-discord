import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_bal(self, user_id, amount):
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR IGNORE INTO economy (user_id, wallet, bank) VALUES (?, 0, 0)', (str(user_id),))
            await db.execute('UPDATE economy SET wallet = wallet + ? WHERE user_id = ?', (amount, str(user_id)))
            await db.commit()

    @commands.hybrid_command(name="balance", description="Check your wallet")
    async def balance(self, ctx, member: discord.Member = None):
        user = member or ctx.author
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT wallet, bank FROM economy WHERE user_id = ?', (str(user.id),))
            res = await cursor.fetchone()
            wallet, bank = res if res else (0, 0)
        
        embed = discord.Embed(title=f"💸 Balance: {user.name}", color=discord.Color.gold())
        embed.add_field(name="Wallet", value=f"${wallet}", inline=True)
        embed.add_field(name="Bank", value=f"${bank}", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="daily", description="Get daily money")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        amount = random.randint(100, 1000)
        await self.update_bal(ctx.author.id, amount)
        await ctx.send(f"💰 You claimed **${amount}**!")

    @commands.hybrid_command(name="work", description="Work for money")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        amount = random.randint(50, 300)
        await self.update_bal(ctx.author.id, amount)
        await ctx.send(f"🔨 You worked and earned **${amount}**!")

    @daily.error
    @work.error
    async def on_cd(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Wait {int(error.retry_after)}s", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economy(bot))