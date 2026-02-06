import discord
from discord.ext import commands
import aiosqlite
import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT log_channel_id FROM settings WHERE guild_id = ?', (str(guild.id),))
            res = await cursor.fetchone()
        if res and res[0]:
            return guild.get_channel(int(res[0]))
        return None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        
        channel = await self.get_log_channel(message.guild)
        if channel:
            embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
            embed.add_field(name="Channel", value=message.channel.mention)
            embed.add_field(name="Content", value=message.content if message.content else "*Image/Embed*", inline=False)
            embed.set_footer(text=f"ID: {message.author.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        
        channel = await self.get_log_channel(before.guild)
        if channel:
            embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.orange(), timestamp=datetime.datetime.now())
            embed.set_author(name=before.author.name, icon_url=before.author.display_avatar.url)
            embed.add_field(name="Channel", value=before.channel.mention)
            embed.add_field(name="Before", value=before.content[:1000], inline=False)
            embed.add_field(name="After", value=after.content[:1000], inline=False)
            embed.add_field(name="Link", value=f"[Jump to message]({after.jump_url})")
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))