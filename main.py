import discord
import datetime
import os
from discord.ext import commands

# Get your user ID and token securely from environment variables
YOUR_USER_ID = int(os.getenv("OWNER_ID"))

# Setup Discord Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        # if member.id == YOUR_USER_ID:
        #     return  # Don't notify for yourself

        user = await bot.fetch_user(YOUR_USER_ID)

        # Joined a VC
        if before.channel is None and after.channel is not None:
            await user.send(
                f"👀 **{member.display_name}** just joined **{after.channel.name}** in *{after.channel.guild.name}* at *{datetime.datetime.now().strftime('%c')}*."
            )

        # Left a VC
        elif before.channel is not None and after.channel is None:
            await user.send(
                f"🚪 **{member.display_name}** just left **{before.channel.name}** in *{before.channel.guild.name}* at *{datetime.datetime.now().strftime('%c')}*."
            )

        # Switched VC
        elif before.channel != after.channel:
            await user.send(
                f"🔀 **{member.display_name}** switched from **{before.channel.name}** to **{after.channel.name}** in *{after.channel.guild.name}* at *{datetime.datetime.now().strftime('%c')}*."
            )

    except Exception as e:
        print(f"❌ Failed to send DM: {e}")


# Run the bot using secret token
bot.run(os.getenv("BOT_TOKEN"))
