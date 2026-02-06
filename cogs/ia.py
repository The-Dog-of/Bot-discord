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

    @commands.command()
    async def ask(self, ctx, *, question):
        """Ask Gemini AI something"""
        if not self.model: 
            return await ctx.send("❌ AI not configured.")
        
        async with ctx.typing():
            try:
                res = await asyncio.to_thread(self.model.generate_content, question)
                text = res.text
                if len(text) > 4000:
                    text = text[:4000] + "..."
                
                embed = discord.Embed(description=text, color=discord.Color.teal())
                embed.set_footer(text="Powered by Google Gemini")
                await ctx.send(embed=embed)
            except Exception as e: 
                await ctx.send(f"⚠️ AI Error: {e}")

async def setup(bot):
    await bot.add_cog(AIFeatures(bot))