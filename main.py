import discord
from discord.ext import commands
import aiosqlite
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

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
        intents = discord.Intents.all()
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None)
        self.db_name = 'ultimate_bot.db'
        self.prefix_cache = {} 

    async def setup_hook(self):
        await self.init_db()
        print("--- Carregando Módulos (Cogs) ---")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ {filename} carregado.')
                except Exception as e:
                    print(f'❌ Falha em {filename}: {e}')
        print("---------------------------------")

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            # Tabela de Configurações
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    guild_id TEXT PRIMARY KEY, log_channel_id TEXT, autorole_id TEXT, prefix TEXT DEFAULT '!'
                )
            ''')
            # Tabela de Warns (para uso futuro)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warns (
                    id INTEGER PRIMARY KEY, user_id TEXT, guild_id TEXT, reason TEXT, admin_id TEXT
                )
            ''')
            await db.commit()

    async def on_ready(self):
        print(f"🚀 Bot online como: {self.user}")
        print(f"🆔 ID: {self.user.id}")

bot = UltimateBot()
bot.run(os.getenv('DISCORD_TOKEN'))