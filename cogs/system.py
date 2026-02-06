import discord
from discord.ext import commands
from discord import ui
import time

# Dicionário de Traduções
LANG = {
    'pt': {
        'title': "Central de Ajuda",
        'desc': "Selecione um módulo abaixo para ver os comandos.",
        'ph': "Selecione uma categoria...",
        'mod': "Moderação",
        'mod_desc': "Banir, Expulsar, Mutar, Trancar",
        'tick': "Tickets",
        'tick_desc': "Sistema de atendimento",
        'info': "Informações",
        'info_desc': "Ver perfil e servidor",
        'ai': "Inteligência Artificial",
        'ai_desc': "Pergunte ao Gemini AI",
        'footer': "Sistema V2 • Português"
    },
    'en': {
        'title': "Help Center",
        'desc': "Select a module below to view commands.",
        'ph': "Select a category...",
        'mod': "Moderation",
        'mod_desc': "Ban, Kick, Timeout, Lock",
        'tick': "Tickets",
        'tick_desc': "Support system",
        'info': "Information",
        'info_desc': "User & Server info",
        'ai': "Artificial Intelligence",
        'ai_desc': "Ask Gemini AI",
        'footer': "System V2 • English"
    }
}

class HelpSelect(ui.Select):
    def __init__(self, bot, lang='en'):
        self.bot = bot
        self.lang = lang
        txt = LANG[lang]
        
        options = [
            discord.SelectOption(label=txt['mod'], description=txt['mod_desc'], emoji="🛡️", value="mod"),
            discord.SelectOption(label=txt['tick'], description=txt['tick_desc'], emoji="📩", value="tick"),
            discord.SelectOption(label=txt['info'], description=txt['info_desc'], emoji="🔎", value="info"),
            discord.SelectOption(label=txt['ai'], description=txt['ai_desc'], emoji="🧠", value="ai"),
        ]
        super().__init__(placeholder=txt['ph'], min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        prefix = self.bot.prefix_cache.get(interaction.guild.id, '!')
        
        embed = discord.Embed(color=0x2b2d31)
        embed.set_footer(text=LANG[self.lang]['footer'], icon_url=self.bot.user.display_avatar.url)

        # Conteúdo dos comandos (Sempre mostra o comando em Inglês, mas descrição traduzida)
        if val == "mod":
            embed.title = f"🛡️ {LANG[self.lang]['mod']}"
            embed.description = (
                f"`{prefix}ban @user [reason]`\n"
                f"`{prefix}kick @user [reason]`\n"
                f"`{prefix}mute @user [time]` (ex: 10m, 1h)\n"
                f"`{prefix}lock` / `{prefix}unlock`\n"
                f"`{prefix}purge [amount]`"
            )
        elif val == "tick":
            embed.title = f"📩 {LANG[self.lang]['tick']}"
            embed.description = f"`{prefix}setup_ticket` - Setup the panel / Cria o painel."
        elif val == "info":
            embed.title = f"🔎 {LANG[self.lang]['info']}"
            embed.description = f"`{prefix}userinfo [@user]`\n`{prefix}serverinfo`\n`{prefix}ping`"
        elif val == "ai":
            embed.title = f"🧠 {LANG[self.lang]['ai']}"
            embed.description = f"`{prefix}ask [text]` - Gemini AI."

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
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, prefix) VALUES (?, ?)', 
                             (str(ctx.guild.id), new_prefix))
            await db.commit()
        self.bot.prefix_cache[ctx.guild.id] = new_prefix
        await ctx.send(f"✅ Prefix updated to `{new_prefix}`")

async def setup(bot):
    await bot.add_cog(SystemCog(bot))