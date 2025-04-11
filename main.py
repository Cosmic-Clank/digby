import discord
import datetime
from discord.ext import commands

# Your Discord user ID (right-click on yourself > Copy ID with Developer Mode enabled)
YOUR_USER_ID = 428149883564720129  # <-- replace with your ID

# Setup intents
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True  # Needed to fetch member display names

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        user = await bot.fetch_user(YOUR_USER_ID)

        # Someone joined a VC
        if before.channel is None and after.channel is not None:
            await user.send(
                f"👀 **{member.display_name}** just joined **{after.channel.name}** in *{after.channel.guild.name}* at *{datetime.datetime.now().strftime('%c')}*."
            )

        # Someone left a VC
        elif before.channel is not None and after.channel is None:
            await user.send(
                f"🚪 {member.display_name} just left **{before.channel.name}** in *{before.channel.guild.name}* at *{datetime.datetime.now().strftime('%c')}*."
            )


        # Optional: You could also track switches (moving from one VC to another)
        elif before.channel != after.channel:
            await user.send(
                f"🔀 **{member.display_name}** switched from **{before.channel.name}** to **{after.channel.name}** in *{after.channel.guild.name}* at *{datetime.datetime.now().strftime('%c')}*."
            )

    except Exception as e:
        print(f"Failed to send DM: {e}")

# Run the bot
bot.run("MTM2MDI4MTM0NzA2Mjc1OTU0NQ.Gs8cJk.4M9DFr7JfB4MfqEP7bUYRvuqUrielekcktGrdY")
