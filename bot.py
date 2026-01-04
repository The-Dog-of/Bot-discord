import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime, timedelta
import asyncio

class TaskBot(commands.Bot):
    def __init__(self):
        # Intents necessários para gerenciar membros e mensagens
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        
        # Inicializa Banco de Dados
        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                channel_id TEXT,
                task_desc TEXT,
                remind_at TEXT,
                notified INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    async def setup_hook(self):
        self.check_reminders.start()
        print(f"Bot logado como {self.user}")

    # --- LÓGICA DE LEMBRETES (BACKGROUND TASK) ---
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute('SELECT id, user_id, channel_id, task_desc FROM tasks WHERE remind_at <= ? AND notified = 0', (now,))
        pending_tasks = self.cursor.fetchall()

        for task_id, user_id, channel_id, desc in pending_tasks:
            channel = self.get_channel(int(channel_id))
            if channel:
                embed = discord.Embed(title="⏰ Lembrete de Tarefa!", description=desc, color=discord.Color.purple())
                await channel.send(content=f"<@{user_id}>", embed=embed)
            
            # Marca como notificado para não repetir
            self.cursor.execute('UPDATE tasks SET notified = 1 WHERE id = ?', (task_id,))
        self.conn.commit()

# --- INSTÂNCIA DO BOT ---
bot = TaskBot()

# --- COMANDOS DE MODERAÇÃO AVANÇADA ---

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Não especificado"):
    """Bane um usuário do servidor"""
    await member.ban(reason=motivo)
    await ctx.send(f"🚫 {member.name} foi banido. Motivo: {motivo}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def castigo(ctx, member: discord.Member, minutos: int, *, motivo="Não especificado"):
    """Dá um 'Timeout' (castigo) no usuário"""
    duration = timedelta(minutes=minutos)
    await member.timeout(duration, reason=motivo)
    await ctx.send(f"🔇 {member.name} foi colocado em castigo por {minutos} minutos.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def fechar(ctx):
    """Bloqueia o canal atual (ninguém envia mensagem)"""
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Este canal foi bloqueado para membros.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, segundos: int):
    """Adiciona modo lento ao canal"""
    await ctx.channel.edit(slowmode_delay=segundos)
    await ctx.send(f"⏳ Modo lento definido para {segundos} segundos.")

# --- COMANDO DE TAREFA (SQL INTEGRADO) ---

@bot.command()
async def tarefa(ctx, data_hora, *, descricao):
    """Uso: !tarefa YYYY-MM-DD HH:MM Descrição da tarefa"""
    user_id = str(ctx.author.id)
    channel_id = str(ctx.channel.id)
    
    bot.cursor.execute('INSERT INTO tasks (user_id, channel_id, task_desc, remind_at) VALUES (?, ?, ?, ?)', 
                      (user_id, channel_id, descricao, data_hora))
    bot.conn.commit()
    await ctx.send(f"✅ Ok {ctx.author.mention}, vou te lembrar disso em {data_hora}!")

    # ... (mantenha o início do código anterior com o TaskBot e a tabela de tarefas)

    def create_table(self):
        # Tabela de tarefas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT, channel_id TEXT, task_desc TEXT, remind_at TEXT, notified INTEGER DEFAULT 0
            )
        ''')
        # Nova tabela para avisos (Warns)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT, guild_id TEXT, reason TEXT, admin_id TEXT, date TEXT
            )
        ''')
        self.conn.commit()

# --- NOVOS COMANDOS DE MODERAÇÃO ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, quantidade: int):
    """Apaga um número específico de mensagens no canal"""
    await ctx.channel.purge(limit=quantidade + 1)
    await ctx.send(f"🧹 {quantidade} mensagens foram removidas.", delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo="Não especificado"):
    """Expulsa um membro do servidor"""
    await member.kick(reason=motivo)
    await ctx.send(f"👢 {member.name} foi expulso. Motivo: {motivo}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user_id: int):
    """Desbane um usuário pelo ID"""
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"🔓 O usuário {user.name} foi desbanido.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, motivo):
    """Avisa um usuário e registra no banco de dados"""
    admin_id = str(ctx.author.id)
    user_id = str(member.id)
    guild_id = str(ctx.guild.id)
    date = datetime.now().strftime("%d/%m/%Y %H:%M")

    bot.cursor.execute('INSERT INTO warns (user_id, guild_id, reason, admin_id, date) VALUES (?, ?, ?, ?, ?)',
                      (user_id, guild_id, motivo, admin_id, date))
    bot.conn.commit()
    
    await ctx.send(f"⚠️ {member.mention} foi avisado! Motivo: {motivo}")

@bot.command()
async def warns(ctx, member: discord.Member):
    """Lista todos os avisos de um usuário"""
    user_id = str(member.id)
    bot.cursor.execute('SELECT reason, date FROM warns WHERE user_id = ?', (user_id,))
    user_warns = bot.cursor.fetchall()

    if not user_warns:
        return await ctx.send(f"✅ {member.name} não possui avisos.")

    embed = discord.Embed(title=f"Avisos de {member.name}", color=discord.Color.orange())
    for reason, date in user_warns:
        embed.add_field(name=f"Data: {date}", value=f"Motivo: {reason}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ajuda(ctx):
    """Exibe a lista de comandos e manual de uso do bot"""
    embed = discord.Embed(
        title="📖 Central de Ajuda - The Dog Bot",
        description="Olá! Sou o seu assistente de produtividade e moderação. Aqui estão os comandos disponíveis:",
        color=0x9b59b6 # Roxo Meliodas / Celestiais Booster
    )

    # Seção de Produtividade
    embed.add_field(
        name="📅 Produtividade",
        value="`!tarefa AAAA-MM-DD HH:MM [desc]` - Agenda um lembrete.\n"
              "`!warns @user` - Consulta histórico de avisos.",
        inline=False
    )

    # Seção de Moderação (Chat)
    embed.add_field(
        name="💬 Moderação de Chat",
        value="`!limpar [qtd]` - Remove mensagens.\n"
              "`!fechar` - Bloqueia o canal.\n"
              "`!slowmode [seg]` - Define tempo de espera.",
        inline=False
    )

    # Seção de Gestão de Membros
    embed.add_field(
        name="🛡️ Gestão de Membros",
        value="`!warn @user [motivo]` - Dá um aviso oficial.\n"
              "`!castigo @user [min]` - Silencia o membro.\n"
              "`!kick @user [motivo]` - Expulsa do servidor.\n"
              "`!ban @user [motivo]` - Bane do servidor.\n"
              "`!unban [ID]` - Remove o banimento.",
        inline=False
    )

    embed.set_footer(text="The power of mentality and money. | Desenvolvido por RichardSouzaLlg")
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)

import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
client.run(token)