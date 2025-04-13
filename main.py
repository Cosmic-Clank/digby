import discord
import datetime
import os
from discord.ext import commands
from zoneinfo import ZoneInfo

# Get your user ID and token securely from environment variables
YOUR_USER_ID = int(os.getenv("OWNER_ID"))

# Setup Discord Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True  # Added for command processing

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store debt amounts (member_id: amount_owed)
debt_tracker = {}


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
                f"👀 **{member.display_name}** just joined **{after.channel.name}** in *{after.channel.guild.name}* at *{datetime.datetime.now(ZoneInfo('Asia/Dubai')).strftime('%c')}*."
            )

        # Left a VC
        elif before.channel is not None and after.channel is None:
            await user.send(
                f"🚪 **{member.display_name}** just left **{before.channel.name}** in *{before.channel.guild.name}* at *{datetime.datetime.now(ZoneInfo('Asia/Dubai')).strftime('%c')}*."
            )

        # Switched VC
        elif before.channel != after.channel:
            await user.send(
                f"🔀 **{member.display_name}** switched from **{before.channel.name}** to **{after.channel.name}** in *{after.channel.guild.name}* at *{datetime.datetime.now(ZoneInfo('Asia/Dubai')).strftime('%c')}*."
            )

    except Exception as e:
        print(f"❌ Failed to send DM: {e}")


@bot.command()
async def dwai(ctx, *, member_name=None):
    # Only allow the bot owner to use this command
    if ctx.author.id != YOUR_USER_ID:
        await ctx.send("❌ You don't have permission to use this command!")
        return

    if member_name is None:
        await ctx.send("❌ Please provide a member name or 'all'!")
        return

    try:
        if member_name.lower() == "all":
            if not debt_tracker:
                await ctx.send("✅ No debts recorded yet!")
                return

            debt_list = []
            for member_id, amount in debt_tracker.items():
                try:
                    member = await bot.fetch_user(member_id)
                    debt_list.append(f"{member.display_name}: {amount} DHS")
                except discord.NotFound:
                    debt_list.append(
                        f"Unknown User (ID: {member_id}): {amount} DHS")
            debt_message = "\n".join(
                debt_list) if debt_list else "✅ No debts recorded yet!"
            await ctx.send(f"📊 Current debts:\n{debt_message}")
        else:
            # Find member by name (case-insensitive)
            member = discord.utils.find(
                lambda m: m.display_name.lower() == member_name.lower(
                ) or m.name.lower() == member_name.lower(),
                ctx.guild.members
            )

            if not member:
                await ctx.send(f"❌ Couldn't find member '{member_name}'!")
                return

            # Add 10 DHS to member's debt
            debt_tracker[member.id] = debt_tracker.get(member.id, 0) + 10
            await ctx.send(
                f"💸 Added 10 DHS to {member.display_name}'s debt. Total owed: {debt_tracker[member.id]} DHS"
            )

    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        print(f"❌ Error in dwai command: {e}")

# Run the bot using secret token
bot.run(os.getenv("BOT_TOKEN"))
