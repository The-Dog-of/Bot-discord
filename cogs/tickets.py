import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import asyncio

class TicketModal(ui.Modal, title="Support Ticket"):
    subject = ui.TextInput(label="Subject", placeholder="Help me with...", style=discord.TextStyle.short)
    description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        # Lógica de criação do ticket (Interação pura)
        cat = discord.utils.get(interaction.guild.categories, name="Tickets")
        if not cat: cat = await interaction.guild.create_category("Tickets")
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
        
        embed = discord.Embed(title=f"Ticket: {self.subject.value}", description=self.description.value, color=discord.Color.green())
        
        view = ui.View()
        btn = ui.Button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
        async def close_cb(inter):
            await inter.response.send_message("Closing...", ephemeral=True)
            await asyncio.sleep(5)
            await channel.delete()
        btn.callback = close_cb
        view.add_item(btn)

        await channel.send(f"{interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Created: {channel.mention}", ephemeral=True)

class TicketView(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="Open Ticket", style=discord.ButtonStyle.blurple, emoji="📩")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketModal())

class Tickets(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="setup_tickets", description="Create ticket panel")
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        embed = discord.Embed(title="📞 Support Center", description="Click below to open a ticket.", color=0x2b2d31)
        # ctx.send funciona tanto pra !setup_tickets quanto pra /setup_tickets
        await ctx.send(embed=embed, view=TicketView())
        
        # Confirmação efêmera só funciona no slash
        if ctx.interaction:
            await ctx.interaction.response.send_message("Panel created!", ephemeral=True)

async def setup(bot): await bot.add_cog(Tickets(bot))