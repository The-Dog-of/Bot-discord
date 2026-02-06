import discord
from discord.ext import commands
from discord import ui
import aiosqlite
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO INICIAL ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- 2. MENU DE SELEÇÃO DE AJUDA ---
class HelpSelect(ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label="👮 Moderação", description="Ban, Kick, Logs, Limpar", emoji="🛡️"),
            discord.SelectOption(label="🎭 Cargos", description="Painel, AutoRole, AddRole", emoji="🧢"),
            discord.SelectOption(label="🎫 Tickets", description="Sistema de atendimento", emoji="📩"),
            discord.SelectOption(label="🤖 Inteligência Artificial", description="Chat GPT/Gemini", emoji="🧠"),
            discord.SelectOption(label="⚙️ Configurações", description="Mudar prefixo, setup", emoji="🔧"),
        ]
        super().__init__(placeholder="Selecione uma categoria...", min_values=1, max_values=1, options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        embed = discord.Embed(title=f"Comandos de {categoria}", color=discord.Color.blue())
        
        # Pega o prefixo atual para mostrar no help
        prefix = self.bot.prefix_cache.get(interaction.guild.id, '!')

        if "Moderação" in categoria:
            embed.add_field(name=f"`{prefix}ban @user [motivo]`", value="Bane um usuário.", inline=False)
            embed.add_field(name=f"`{prefix}kick @user [motivo]`", value="Expulsa um usuário.", inline=False)
            embed.add_field(name=f"`{prefix}limpar [qtd]`", value="Limpa mensagens do chat.", inline=False)
            embed.add_field(name=f"`{prefix}setlogs #canal`", value="Define onde os logs aparecem.", inline=False)
        
        elif "Cargos" in categoria:
            embed.add_field(name=f"`{prefix}painel_cargos`", value="Cria botões para pegar cargos.", inline=False)
            embed.add_field(name=f"`{prefix}setautorole @cargo`", value="Define cargo automático ao entrar.", inline=False)
            embed.add_field(name=f"`{prefix}addrole`", value="Gerencia cargos manualmente.", inline=False)

        elif "Tickets" in categoria:
            embed.add_field(name=f"`{prefix}setup_ticket`", value="Cria o painel de atendimento.", inline=False)
            embed.add_field(name=f"`{prefix}fechar`", value="Fecha um ticket aberto.", inline=False)

        elif "Inteligência" in categoria:
            embed.add_field(name=f"`{prefix}pergunte [pergunta]`", value="Responde qualquer coisa usando IA.", inline=False)

        elif "Configurações" in categoria:
            embed.add_field(name=f"`{prefix}setprefix [novo]`", value="Muda o prefixo do bot.", inline=False)

        await interaction.response.edit_message(embed=embed)

# --- 3. DEFINIÇÃO DAS COGS (Funcionalidades) ---

class SystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ajuda(self, ctx):
        """Exibe o menu interativo de comandos"""
        view = ui.View()
        view.add_item(HelpSelect(self.bot))
        embed = discord.Embed(title="📚 Central de Ajuda", description="Selecione uma categoria abaixo:", color=discord.Color.gold())
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, novo_prefixo: str):
        """Muda o prefixo do bot"""
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, prefix) VALUES (?, ?)', 
                             (str(ctx.guild.id), novo_prefixo))
            await db.commit()
        self.bot.prefix_cache[ctx.guild.id] = novo_prefixo
        await ctx.send(f"✅ Prefixo alterado para `{novo_prefixo}`")

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

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_cargos(self, ctx):
        """Cria botões com os 3 últimos cargos criados no servidor"""
        roles = ctx.guild.roles[-4:-1] 
        if not roles: return await ctx.send("Sem cargos suficientes.")

        view = ui.View(timeout=None)
        for role in roles:
            button = ui.Button(label=role.name, style=discord.ButtonStyle.primary, custom_id=f"role_{role.id}")
            async def cb(interaction, r=role):
                if r in interaction.user.roles:
                    await interaction.user.remove_roles(r)
                    await interaction.response.send_message(f"❌ Removido: {r.name}", ephemeral=True)
                else:
                    await interaction.user.add_roles(r)
                    await interaction.response.send_message(f"✅ Adicionado: {r.name}", ephemeral=True)
            button.callback = cb
            view.add_item(button)
        await ctx.send("🎭 **Escolha seus Cargos:**", view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setautorole(self, ctx, role: discord.Role):
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, autorole_id) VALUES (?, ?)', 
                             (str(ctx.guild.id), str(role.id)))
            await db.commit()
        await ctx.send(f"🆕 AutoRole definido: {role.name}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.author.top_role <= role:
            return await ctx.send("❌ Você não pode dar um cargo maior que o seu.")
        await member.add_roles(role)
        await ctx.send(f"✅ Cargo {role.name} dado a {member.name}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT autorole_id FROM settings WHERE guild_id = ?', (str(member.guild.id),))
            res = await cursor.fetchone()
        if res and res[0]:
            role = member.guild.get_role(int(res[0]))
            if role: await member.add_roles(role)

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        view = ui.View(timeout=None)
        btn = ui.Button(label="Abrir Ticket", style=discord.ButtonStyle.success, emoji="📩")
        
        async def cb(interaction):
            cat = discord.utils.get(interaction.guild.categories, name="Tickets")
            if not cat: cat = await interaction.guild.create_category("Tickets")
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
            await interaction.response.send_message(f"✅ Ticket criado: {ch.mention}", ephemeral=True)
            await ch.send(f"{interaction.user.mention} Como podemos ajudar? Digite `!fechar` para encerrar.")
        
        btn.callback = cb
        view.add_item(btn)
        await ctx.send(embed=discord.Embed(title="Central de Suporte", description="Clique abaixo para falar com a staff.", color=discord.Color.green()), view=view)

    @commands.command(name="fechar")
    async def fechar_tkt(self, ctx):
        if "ticket-" in ctx.channel.name:
            await ctx.send("🔒 Fechando em 3 segundos...")
            await asyncio.sleep(3)
            await ctx.channel.delete()

class AIFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pergunte(self, ctx, *, q):
        if not model: return await ctx.send("❌ IA não configurada no .env")
        async with ctx.typing():
            try:
                res = await asyncio.to_thread(model.generate_content, q)
                await ctx.send(embed=discord.Embed(description=res.text[:4000], color=discord.Color.teal()))
            except Exception as e: 
                await ctx.send(f"Erro na IA: {e}")

# --- 4. CLASSE PRINCIPAL DO BOT (Agora fica no final) ---

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
        # Agora o bot consegue ver as classes porque elas foram criadas acima!
        await self.add_cog(SystemCog(self)) 
        await self.add_cog(Moderation(self))
        await self.add_cog(RoleManager(self))
        await self.add_cog(TicketSystem(self))
        if model: await self.add_cog(AIFeatures(self))
        print(f"✅ Bot logado como {self.user}")

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    guild_id TEXT PRIMARY KEY, log_channel_id TEXT, autorole_id TEXT, prefix TEXT DEFAULT '!'
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warns (
                    id INTEGER PRIMARY KEY, user_id TEXT, guild_id TEXT, reason TEXT, admin_id TEXT
                )
            ''')
            await db.commit()

# --- 5. EXECUÇÃO ---
bot = UltimateBot()
bot.run(TOKEN)