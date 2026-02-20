import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Application", style=discord.ButtonStyle.green, custom_id="create_application")
    async def create_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Find or create "apply" category
        category = discord.utils.get(guild.categories, name="apply")
        if category is None:
            category = await guild.create_category("apply")

        # Channel name
        channel_name = f"application-{user.name}".lower()

        # Check if user already has a channel
        existing = discord.utils.get(category.text_channels, name=channel_name)
        if existing:
            await interaction.response.send_message(
                f"You already have an application channel: {existing.mention}",
                ephemeral=True
            )
            return

        # Permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        # Create channel
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(
            f"Your application channel has been created: {channel.mention}",
            ephemeral=True
        )

        embed = discord.Embed(
            title="Application Channel",
            description=f"Hello {user.mention}, please fill out your application here.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)


@bot.event
async def on_ready():
    bot.add_view(ApplicationView())  # Persistent buttons
    print(f"Logged in as {bot.user}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):
    embed = discord.Embed(
        title="Application Panel",
        description="Click the button below to create your application channel.",
        color=discord.Color.green()
    )

    view = ApplicationView()
    await channel.send(embed=embed, view=view)
    await ctx.send(f"Application panel sent in {channel.mention}")


bot.run(TOKEN)