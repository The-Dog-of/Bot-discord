import discord
from discord.ext import commands, tasks
import aiosqlite
import os
import asyncio
from dotenv import load_dotenv
from itertools import cycle

load_dotenv()

intents = discord.Intents.all()

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.db_name = 'ultimate_bot.db'
        self.status_cycle = cycle(['/help', '!help', 'Moderating', 'Hybrid System'])

    async def setup_hook(self):
        await self.init_db()
        print("--- Loading Modules ---")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Loaded: {filename}')
                except Exception as e:
                    print(f'❌ Failed: {filename} -> {e}')
        print("-----------------------")
        self.change_status_loop.start()

    @tasks.loop(seconds=15)
    async def change_status_loop(self):
        await self.change_presence(activity=discord.Game(next(self.status_cycle)))

    @change_status_loop.before_loop
    async def before_status_loop(self):
        await self.wait_until_ready()

    async def on_ready(self):
        print(f"🚀 Signed in as: {self.user}")

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS settings (guild_id TEXT PRIMARY KEY, log_channel_id TEXT)')
            await db.execute('CREATE TABLE IF NOT EXISTS economy (user_id TEXT PRIMARY KEY, wallet INTEGER DEFAULT 0, bank INTEGER DEFAULT 0)')
            await db.commit()

bot = UltimateBot()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Sincroniza os comandos híbridos com o Discord"""
    msg = await ctx.send("🔄 Syncing global commands...")
    try:
        # Sincroniza tudo (Híbridos + Slash puros)
        synced = await ctx.bot.tree.sync()
        await msg.edit(content=f"✅ Success! Synced {len(synced)} commands globally. They should appear in both ! and / menus.")
    except Exception as e:
        await msg.edit(content=f"❌ Error: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))