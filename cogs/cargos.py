import discord
from discord.ext import commands
from discord import ui
import aiosqlite

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_cargos(self, ctx):
        """Cria botões com os 3 últimos cargos criados no servidor"""
        roles = ctx.guild.roles[-4:-1] 
        if not roles: return await ctx.send("Sem cargos suficientes.")

        view = ui.View(timeout=None)
        for role in roles:
            button = ui.Button(label=role.name, style=discord.ButtonStyle.primary, custom_id=f"role_{role.id}")
            
            async def cb(interaction, r=role):
                if r in interaction.user.roles:
                    await interaction.user.remove_roles(r)
                    await interaction.response.send_message(f"❌ Removido: {r.name}", ephemeral=True)
                else:
                    await interaction.user.add_roles(r)
                    await interaction.response.send_message(f"✅ Adicionado: {r.name}", ephemeral=True)
            
            button.callback = cb
            view.add_item(button)
        await ctx.send("🎭 **Escolha seus Cargos:**", view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setautorole(self, ctx, role: discord.Role):
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, autorole_id) VALUES (?, ?)', 
                             (str(ctx.guild.id), str(role.id)))
            await db.commit()
        await ctx.send(f"🆕 AutoRole definido: {role.name}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.author.top_role <= role:
            return await ctx.send("❌ Você não pode dar um cargo maior que o seu.")
        await member.add_roles(role)
        await ctx.send(f"✅ Cargo {role.name} dado a {member.name}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT autorole_id FROM settings WHERE guild_id = ?', (str(member.guild.id),))
            res = await cursor.fetchone()
        if res and res[0]:
            role = member.guild.get_role(int(res[0]))
            if role: await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(RoleManager(bot))