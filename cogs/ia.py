import discord
from discord.ext import commands
import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class AIFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("⚠️ AVISO: GEMINI_API_KEY não encontrada no .env")

    @commands.command()
    async def pergunte(self, ctx, *, q):
        if not self.model: 
            return await ctx.send("❌ IA não configurada. Verifique o arquivo .env")
        
        async with ctx.typing():
            try:
                # Executa em thread separada para não travar o bot
                res = await asyncio.to_thread(self.model.generate_content, q)
                
                # Tratamento para respostas longas (limite do Discord é 4096 no embed)
                texto = res.text
                if len(texto) > 4000:
                    texto = texto[:4000] + "... (resposta cortada por limite)"
                    
                await ctx.send(embed=discord.Embed(description=texto, color=discord.Color.teal()))
            except Exception as e: 
                await ctx.send(f"Erro na IA: {e}")

async def setup(bot):
    await bot.add_cog(AIFeatures(bot))