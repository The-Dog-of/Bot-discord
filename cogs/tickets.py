import discord
from discord.ext import commands
from discord import ui
import asyncio

class TicketModal(ui.Modal, title="Support Request"):
    subject = ui.TextInput(label="Subject / Assunto", placeholder="Ex: Report, Help, Purchase...", style=discord.TextStyle.short)
    description = ui.TextInput(label="Description / Descrição", style=discord.TextStyle.paragraph, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        cat = discord.utils.get(guild.categories, name="Tickets")
        if not cat: cat = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
        
        embed = discord.Embed(title=f"Ticket: {self.subject.value}", color=discord.Color.from_rgb(43, 45, 49))
        embed.description = f"Welcome {interaction.user.mention}. Staff will be with you shortly.\n\n**Issue:**\n{self.description.value}"
        
        view = ui.View(timeout=None)
        btn_close = ui.Button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
        
        async def close_callback(inter):
            await inter.response.send_message("Deleting ticket in 5s...")
            await asyncio.sleep(5)
            await channel.delete()
            
        btn_close.callback = close_callback
        view.add_item(btn_close)

        await channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket opened: {channel.mention}", ephemeral=True)

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Open Ticket", style=discord.ButtonStyle.blurple, emoji="📩", custom_id="open_ticket_main")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketModal())

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        embed = discord.Embed(
            title="📞 Support Center", 
            description="Need help? Click the button below to contact staff.\nPrecisa de ajuda? Clique abaixo.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))