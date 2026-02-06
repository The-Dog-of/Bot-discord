import discord
from discord.ext import commands
from discord import ui
import asyncio

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

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))