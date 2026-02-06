import discord
from discord.ext import commands
import aiosqlite
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_balance(self, user_id):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT wallet, bank FROM economy WHERE user_id = ?', (str(user_id),))
            res = await cursor.fetchone()
            if not res:
                await db.execute('INSERT INTO economy (user_id, wallet, bank) VALUES (?, 0, 0)', (str(user_id),))
                await db.commit()
                return 0, 0
            return res[0], res[1]

    async def update_balance(self, user_id, amount, mode="wallet"):
        async with aiosqlite.connect(self.bot.db_name) as db:
            # Garante que usuário existe
            await self.get_balance(user_id) 
            query = f'UPDATE economy SET {mode} = {mode} + ? WHERE user_id = ?'
            await db.execute(query, (amount, str(user_id)))
            await db.commit()

    @commands.command(aliases=['bal', 'atm'])
    async def balance(self, ctx, member: discord.Member = None):
        """Check your wallet and bank balance"""
        if not member: member = ctx.author
        wallet, bank = await self.get_balance(member.id)

        embed = discord.Embed(title=f"💳 Bank of {ctx.guild.name}", color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="💵 Wallet", value=f"${wallet:,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${bank:,}", inline=True)
        embed.add_field(name="💰 Net Worth", value=f"${wallet + bank:,}", inline=False)
        embed.set_footer(text="Economy System V1")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user) # 24 horas de cooldown
    async def daily(self, ctx):
        """Claim your daily reward"""
        amount = random.randint(500, 2000)
        await self.update_balance(ctx.author.id, amount, "wallet")
        
        embed = discord.Embed(description=f"✅ You claimed your daily reward of **${amount}**!", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user) # 1 hora cooldown
    async def work(self, ctx):
        """Work to earn money"""
        jobs = ["Developer", "Driver", "Cook", "Streamer", "Doctor"]
        earnings = random.randint(100, 500)
        job = random.choice(jobs)
        
        await self.update_balance(ctx.author.id, earnings, "wallet")
        await ctx.send(f"🔨 You worked as a **{job}** and earned **${earnings}**.")

    @commands.command(aliases=['top', 'rich'])
    async def leaderboard(self, ctx):
        """See the richest users"""
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT user_id, wallet + bank as total FROM economy ORDER BY total DESC LIMIT 10')
            rows = await cursor.fetchall()

        embed = discord.Embed(title="🏆 Richest Leaders", color=discord.Color.gold())
        text = ""
        for i, row in enumerate(rows, 1):
            user = ctx.guild.get_member(int(row[0]))
            name = user.name if user else "Unknown User"
            text += f"**#{i}** {name} • ${row[1]:,}\n"
        
        embed.description = text if text else "No data yet."
        await ctx.send(embed=embed)

    @daily.error
    @work.error
    async def cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            # Formata o tempo restante de forma bonita
            hours = int(error.retry_after // 3600)
            minutes = int((error.retry_after % 3600) // 60)
            await ctx.send(f"⏳ Please wait **{hours}h {minutes}m** before using this command again.")

async def setup(bot):
    await bot.add_cog(Economy(bot))