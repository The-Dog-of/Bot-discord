import discord
from discord.ext import commands
from discord import ui
import time

# Dicionário de Traduções e Comandos
LANG = {
    'pt': {
        'desc': "Selecione um módulo abaixo para ver os comandos.",
        'ph': "Selecione uma categoria...",
        'footer': "Sistema Híbrido (Prefix & Slash) • Português",
        'cats': {
            'mod': "Moderação",
            'eco': "Economia",
            'util': "Utilidades",
            'tick': "Tickets",
            'ai': "Inteligência Artificial",
            'info': "Informações"
        }
    },
    'en': {
        'desc': "Select a module below to view commands.",
        'ph': "Select a category...",
        'footer': "Hybrid System (Prefix & Slash) • English",
        'cats': {
            'mod': "Moderation",
            'eco': "Economy",
            'util': "Utility",
            'tick': "Tickets",
            'ai': "Artificial Intelligence",
            'info': "Information"
        }
    }
}

class HelpSelect(ui.Select):
    def __init__(self, bot, lang='en'):
        self.bot = bot
        self.lang = lang
        txt = LANG[lang]
        cats = txt['cats']
        
        options = [
            discord.SelectOption(label=cats['mod'], description="Ban, Kick, Mute, Lock", emoji="🛡️", value="mod"),
            discord.SelectOption(label=cats['eco'], description="Work, Daily, Balance", emoji="💰", value="eco"),
            discord.SelectOption(label=cats['util'], description="Giveaway, Poll, Suggest", emoji="🎉", value="util"),
            discord.SelectOption(label=cats['tick'], description="Support System", emoji="📩", value="tick"),
            discord.SelectOption(label=cats['ai'], description="Gemini AI", emoji="🧠", value="ai"),
            discord.SelectOption(label=cats['info'], description="User & Server Info", emoji="🔎", value="info"),
        ]
        super().__init__(placeholder=txt['ph'], min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        prefix = self.bot.prefix_cache.get(interaction.guild.id, '!')
        
        embed = discord.Embed(color=0x2b2d31)
        embed.set_footer(text=LANG[self.lang]['footer'], icon_url=self.bot.user.display_avatar.url)
        
        # Título da Categoria
        embed.title = f"{LANG[self.lang]['cats'][val]}"

        # --- LISTA DE COMANDOS ---
        if val == "mod":
            embed.description = (
                f"`{prefix}ban @user [reason]`\n"
                f"`{prefix}kick @user [reason]`\n"
                f"`{prefix}mute @user [time]` (ex: 10m)\n"
                f"`{prefix}lock` / `{prefix}unlock`\n"
                f"`{prefix}purge [amount]`\n"
                f"`{prefix}setlogs #channel`"
            )
        elif val == "eco":
            embed.description = (
                f"`{prefix}work` - Work to earn money\n"
                f"`{prefix}daily` - Daily reward\n"
                f"`{prefix}bal` - Check wallet/bank\n"
                f"`{prefix}top` - Rich leaderboard"
            )
        elif val == "util":
            embed.description = (
                "**Slash Commands (Use /):**\n"
                f"`/giveaway [time] [prize]` - Start a giveaway\n"
                f"`/poll [question]` - Create a poll\n"
                f"`/suggest [text]` - Send suggestion"
            )
        elif val == "tick":
            embed.description = f"`{prefix}setup_ticket` - Setup support panel."
        elif val == "ai":
            embed.description = f"`{prefix}ask [text]` - Chat with AI."
        elif val == "info":
            embed.description = f"`{prefix}userinfo [@user]`\n`{prefix}serverinfo`\n`{prefix}ping`"

        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @ui.button(emoji="🇺🇸", style=discord.ButtonStyle.grey)
    async def en_btn(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(title="Help Center", description=LANG['en']['desc'], color=0x5865F2)
        view = ui.View()
        view.add_item(HelpSelect(self.bot, 'en'))
        await interaction.response.edit_message(embed=embed, view=view)

    @ui.button(emoji="🇧🇷", style=discord.ButtonStyle.grey)
    async def pt_btn(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(title="Central de Ajuda", description=LANG['pt']['desc'], color=0x009739)
        view = ui.View()
        view.add_item(HelpSelect(self.bot, 'pt'))
        await interaction.response.edit_message(embed=embed, view=view)

class SystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="🌎 Select Language / Selecione o Idioma", color=0x2b2d31)
        await ctx.send(embed=embed, view=HelpView(self.bot))

    @commands.command()
    async def ping(self, ctx):
        start = time.perf_counter()
        msg = await ctx.send("Analysing...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await msg.edit(content=f"🏓 **Pong!** API: `{round(self.bot.latency * 1000)}ms` | Bot: `{round(duration)}ms`")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix: str):
        # Atualização do prefixo no banco (simplificado para o exemplo)
        self.bot.prefix_cache[ctx.guild.id] = new_prefix
        await ctx.send(f"✅ Prefix updated to `{new_prefix}`")

async def setup(bot):
    await bot.add_cog(SystemCog(bot))