import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # O decorator muda para app_commands
    @app_commands.command(name="giveaway", description="Start a giveaway (Sorteio)")
    @app_commands.describe(time="Duration (ex: 10s, 1m)", prize="What is the prize?")
    async def giveaway(self, interaction: discord.Interaction, time: str, prize: str):
        # Slash commands precisam responder rápido, então usamos defer() se for demorar, 
        # mas aqui vamos responder direto.
        
        # Conversão de tempo
        unit = time[-1]
        try:
            val = int(time[:-1])
        except ValueError:
            return await interaction.response.send_message("❌ Invalid format. Use: 10s, 5m, 1h", ephemeral=True)

        seconds = 0
        if unit == 's': seconds = val
        elif unit == 'm': seconds = val * 60
        elif unit == 'h': seconds = val * 3600
        else: return await interaction.response.send_message("❌ Use: s, m, h", ephemeral=True)

        embed = discord.Embed(title="🎉 GIVEAWAY / SORTEIO 🎉", color=discord.Color.purple())
        embed.add_field(name="Prize", value=prize)
        embed.add_field(name="Hosted by", value=interaction.user.mention)
        embed.add_field(name="Time", value=f"Ends in {time}")
        embed.set_footer(text="React with 🎉 to join!")
        
        # Resposta inicial do Slash Command
        await interaction.response.send_message(embed=embed)
        
        # Precisamos pegar a mensagem que o bot acabou de enviar para reagir nela
        msg = await interaction.original_response()
        await msg.add_reaction("🎉")

        await asyncio.sleep(seconds)

        msg = await interaction.channel.fetch_message(msg.id)
        users = [user async for user in msg.reactions[0].users() if not user.bot]

        if len(users) == 0:
            await interaction.followup.send(f"😢 No winner for **{prize}** (No participants).")
        else:
            winner = random.choice(users)
            await interaction.followup.send(f"🎊 Congratulations {winner.mention}! You won **{prize}**!")

    @app_commands.command(name="poll", description="Create a Yes/No poll")
    async def poll(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 Poll / Votação", description=question, color=discord.Color.blue())
        embed.set_footer(text=f"Asked by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @app_commands.command(name="suggest", description="Send a suggestion")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        embed = discord.Embed(title="💡 New Suggestion", description=suggestion, color=discord.Color.yellow())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

async def setup(bot):
    await bot.add_cog(Utility(bot))