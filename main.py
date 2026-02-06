import discord
from discord.ext import commands, tasks
import aiosqlite
import os
import asyncio
from dotenv import load_dotenv
from itertools import cycle

load_dotenv()

# Configuração de Intents
intents = discord.Intents.all()

# Função para pegar prefixo do banco de dados
async def get_prefix(bot, message):
    if not message.guild: return '!'
    if message.guild.id in bot.prefix_cache:
        return bot.prefix_cache[message.guild.id]
    
    async with aiosqlite.connect(bot.db_name) as db:
        cursor = await db.execute('SELECT prefix FROM settings WHERE guild_id = ?', (str(message.guild.id),))
        result = await cursor.fetchone()
        
    prefix = result[0] if result else '!'
    bot.prefix_cache[message.guild.id] = prefix
    return prefix

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None)
        self.db_name = 'ultimate_bot.db'
        self.prefix_cache = {} 
        self.status = cycle(['!help for commands', 'Protecting the server', 'Beta Version 2.0', 'Developed with Python'])

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
        await self.change_presence(activity=discord.Game(next(self.status)))

    async def on_ready(self):
        print(f"🚀 Signed in as: {self.user}")
        print(f"🆔 ID: {self.user.id}")

    import discord
from discord.ext import commands, tasks
import aiosqlite
import os
import asyncio
from dotenv import load_dotenv
from itertools import cycle

load_dotenv()

intents = discord.Intents.all()

async def get_prefix(bot, message):
    if not message.guild: return '!'
    if message.guild.id in bot.prefix_cache:
        return bot.prefix_cache[message.guild.id]
    
    async with aiosqlite.connect(bot.db_name) as db:
        cursor = await db.execute('SELECT prefix FROM settings WHERE guild_id = ?', (str(message.guild.id),))
        result = await cursor.fetchone()
        
    prefix = result[0] if result else '!'
    bot.prefix_cache[message.guild.id] = prefix
    return prefix

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None)
        self.db_name = 'ultimate_bot.db'
        self.prefix_cache = {} 
        self.status = cycle(['/help', 'Moderating', 'Economy V2', 'Python Power'])

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
        await self.change_presence(activity=discord.Game(next(self.status)))

    async def on_ready(self):
        print(f"🚀 Signed in as: {self.user}")
        print(f"🆔 ID: {self.user.id}")

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS settings (guild_id TEXT PRIMARY KEY, log_channel_id TEXT, prefix TEXT DEFAULT "!")')
            await db.execute('CREATE TABLE IF NOT EXISTS tickets (channel_id TEXT PRIMARY KEY, author_id TEXT)')
            await db.execute('CREATE TABLE IF NOT EXISTS economy (user_id TEXT PRIMARY KEY, wallet INTEGER DEFAULT 0, bank INTEGER DEFAULT 0)')
            await db.commit()

bot = UltimateBot()

# --- COMANDO MÁGICO PARA O MENU APARECER ---
@bot.command()
@commands.is_owner() # Só você pode usar (configure seu ID no .env ou garanta que é o dono da aplicação)
async def sync(ctx):
    fmt = await ctx.bot.tree.sync()
    await ctx.send(f"✅ Synced {len(fmt)} commands globally. The menu should appear soon!")

bot.run(os.getenv('DISCORD_TOKEN'))

bot = UltimateBot()
bot.run(os.getenv('DISCORD_TOKEN'))