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


@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild

    # Create Applications Category
    category = discord.utils.get(guild.categories, name="Applications")
    if not category:
        category = await guild.create_category("Applications")

    # Create application start channel
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

    view = ApplicationView()

    await start_channel.send(embed=embed, view=view)
    await ctx.send("✅ Application system setup complete!")


class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Application", style=discord.ButtonStyle.green)
    async def start_application(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Applications")

        # Prevent duplicate applications
        existing = discord.utils.get(
            guild.text_channels,
            name=f"application-{interaction.user.name}"
        )
        if existing:
            await interaction.response.send_message(
                "❌ You already have an open application!",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        ticket_channel = await guild.create_text_channel(
            f"application-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="📝 Application Started",
            description=f"{interaction.user.mention}, please answer the questions here.\n\nGood luck!",
            color=discord.Color.green()
        )

        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Your application channel: {ticket_channel.mention}",
            ephemeral=True
        )


# Get token from Railway environment variable
TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
