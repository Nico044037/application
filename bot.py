import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(ApplicationView())
    bot.add_view(StaffView())


# =========================
# SETUP COMMAND
# =========================
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild

    category = discord.utils.get(guild.categories, name="Applications")
    if not category:
        category = await guild.create_category("Applications")

    start_channel = discord.utils.get(guild.text_channels, name="application-start")
    if not start_channel:
        start_channel = await guild.create_text_channel(
            "application-start",
            category=category
        )

    embed = discord.Embed(
        title="📋 Start Your Application",
        description="Click the button below to start your application.",
        color=discord.Color.blue()
    )

    await start_channel.send(embed=embed, view=ApplicationView())
    await ctx.send("✅ Application system setup complete!")


# =========================
# USER START APPLICATION
# =========================
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Application", style=discord.ButtonStyle.green, custom_id="start_application")
    async def start_application(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Applications")

        existing = discord.utils.get(
            guild.text_channels,
            name=f"application-{interaction.user.id}"
        )
        if existing:
            await interaction.response.send_message(
                "❌ You already have an open application!",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            f"application-{interaction.user.id}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="📝 Application Opened",
            description=f"{interaction.user.mention} started an application.\n\nStaff can review below.",
            color=discord.Color.orange()
        )

        embed.set_footer(text=f"Applicant ID: {interaction.user.id}")

        await channel.send(embed=embed, view=StaffView())
        await interaction.response.send_message(
            f"✅ Your application channel: {channel.mention}",
            ephemeral=True
        )


# =========================
# STAFF BUTTONS
# =========================
class StaffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_roles:
            return True
        await interaction.response.send_message("❌ Staff only!", ephemeral=True)
        return False

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green, custom_id="accept_app")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        applicant_id = int(interaction.message.embeds[0].footer.text.split(": ")[1])
        member = interaction.guild.get_member(applicant_id)
        role = interaction.guild.get_role(1471207852508188768)

        if member and role:
            await member.add_roles(role)

        embed = discord.Embed(
            title="✅ Application Accepted",
            description=f"{member.mention} has been accepted!",
            color=discord.Color.green()
        )

        await interaction.channel.send(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.red, custom_id="decline_app")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):

        applicant_id = int(interaction.message.embeds[0].footer.text.split(": ")[1])
        member = interaction.guild.get_member(applicant_id)

        embed = discord.Embed(
            title="❌ Application Declined",
            description=f"{member.mention} has been declined.",
            color=discord.Color.red()
        )

        await interaction.channel.send(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.gray, custom_id="close_app")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 Closing application...", ephemeral=True)
        await interaction.channel.delete()


# =========================
# SUDO GROUP
# =========================
@bot.group()
@commands.has_permissions(administrator=True)
async def sudo(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("⚠️ Available subcommands: consoleadd, removeconsole")


# =========================
# ADD CONSOLE ROLE
# =========================
@sudo.command()
async def consoleadd(ctx, member: discord.Member):
    guild = ctx.guild

    role = discord.utils.get(guild.roles, name="Console")

    if not role:
        role = await guild.create_role(
            name="Console",
            colour=discord.Color.dark_green(),
            reason="Console role auto-created"
        )

    if role in member.roles:
        await ctx.send("❌ That user already has Console role.")
        return

    await member.add_roles(role)

    embed = discord.Embed(
        title="🖥️ Console Role Added",
        description=f"{member.mention} has been given the **Console** role.",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# =========================
# REMOVE CONSOLE ROLE
# =========================
@sudo.command()
async def removeconsole(ctx, member: discord.Member):
    guild = ctx.guild

    role = discord.utils.get(guild.roles, name="Console")

    if not role:
        await ctx.send("❌ Console role does not exist.")
        return

    if role not in member.roles:
        await ctx.send("❌ That user does not have Console role.")
        return

    await member.remove_roles(role)

    embed = discord.Embed(
        title="🗑️ Console Role Removed",
        description=f"{member.mention} has been removed from **Console** role.",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
