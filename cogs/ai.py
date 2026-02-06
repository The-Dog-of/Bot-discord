import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        key = os.getenv('GEMINI_API_KEY')
        if key:
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel('gemini-pro')
        else: self.model = None

    @commands.hybrid_command(name="ask", description="Ask AI something")
    @app_commands.describe(question="What do you want to know?")
    async def ask(self, ctx, *, question: str):
        if not self.model: return await ctx.send("❌ AI not configured.", ephemeral=True)
        
        await ctx.defer() # Importante para não dar timeout
        async with ctx.typing():
            try:
                res = await asyncio.to_thread(self.model.generate_content, question)
                text = res.text[:4000]
                embed = discord.Embed(description=text, color=discord.Color.teal())
                embed.set_footer(text=f"Q: {question}")
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"⚠️ Error: {e}")

async def setup(bot):
    await bot.add_cog(AI(bot))