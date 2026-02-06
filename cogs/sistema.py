import discord
from discord.ext import commands
from discord import ui
import aiosqlite

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

async def setup(bot):
    await bot.add_cog(SystemCog(bot))