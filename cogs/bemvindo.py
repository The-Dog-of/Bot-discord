import discord
from discord.ext import commands
import aiosqlite

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # 1. Busca canal de boas vindas (vamos usar o log_channel_id por enquanto ou criar um novo campo)
        # Para simplificar, vou usar o canal System Channel do servidor (o padrão do Discord)
        channel = member.guild.system_channel
        
        if channel:
            embed = discord.Embed(
                title=f"👋 Bem-vindo(a), {member.name}!", 
                description=f"Você é o membro número **{member.guild.member_count}**!",
                color=discord.Color.teal()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")
            embed.set_image(url="https://i.imgur.com/G5ChpY4.png") # Banner genérico bonito
            
            await channel.send(f"Olá {member.mention}!", embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))