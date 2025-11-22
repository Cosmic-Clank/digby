import random
import discord
import datetime
import os
from discord.ext import commands
from discord.ext import voice_recv
from dotenv import load_dotenv
import json
from pathlib import Path
import sys

import syncedlyrics
load_dotenv()

# Get your user ID and token securely from environment variables
YOUR_USER_ID = int(os.getenv("OWNER_ID"))  # type: ignore

# Setup Discord Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True  # Added for command processing

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store debt amounts (member_id: amount_owed)
debt_tracker = {}


def project_root() -> Path:
    # If frozen by PyInstaller etc.
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # When running from source
    return Path(__file__).resolve().parent


ROOT = project_root()


@bot.event
async def on_ready():
    # pyright: ignore[reportOptionalMemberAccess]
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")  # type: ignore


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        # if member.id == YOUR_USER_ID:
        #     return  # Don't notify for yourself

        user = await bot.fetch_user(YOUR_USER_ID)

        # Joined a VC
        if before.channel is None and after.channel is not None:
            await user.send(
                f"👀 **{member.display_name}** enter **{after.channel.name}** at *{datetime.datetime.now().strftime('%c')}*."
            )

        # Left a VC
        elif before.channel is not None and after.channel is None:
            await user.send(
                f"🚪 **{member.display_name}** just left **{before.channel.name}** at *{datetime.datetime.now().strftime('%c')}*."
            )

        # Switched VC
        elif before.channel != after.channel:
            await user.send(
                f"🔀 **{member.display_name}** switched from **{before.channel.name}** to **{after.channel.name}** at *{datetime.datetime.now().strftime('%c')}*."
            )

    except Exception as e:
        print(f"❌ Failed to send DM: {e}")


DEBT_FILE = ROOT / "debt_tracker.json"


def load_debt():
    if os.path.exists(DEBT_FILE):
        with open(DEBT_FILE, "r", encoding="utf-8") as f:
            try:
                return {int(k): v for k, v in json.load(f).items()}
            except Exception:
                return {}
    return {}


def save_debt():
    with open(DEBT_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in debt_tracker.items()}, f)


# Load debts at startup
debt_tracker = load_debt()


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
            debt_list.sort(key=lambda x: int(x.split(": ")[1].split(" ")[0]))
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
            save_debt()
            await ctx.send(
                f"💸 Added 10 DHS to {member.display_name}'s debt. Total owed: {debt_tracker[member.id]} DHS"
            )

    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        print(f"❌ Error in dwai command: {e}")

cuss_list = [
    "Shut your putrid, shit-crusted mouth, {name}, you fucking worthless maggot",
    "What the fuck, {name}, did you just vomit that brain-dead bullshit from your diseased lips?",
    "Sit your pathetic, cum-stained ass down, {name}, you’re a goddamn walking abortion",
    "Calm the fuck down, {name}, you sniveling pile of festering dogshit, you’re a disgrace",
    "Imagine being {name}, a fucking rancid loser who’s a stain on humanity’s asshole",
    "Bro, {name}, you’re so fucked, you’re a rotting turd sizzling in your own piss",
    "Shut the fuck up, {name}, before I kick your dumbass into a fucking sewer",
    "Nice try, you miserable cockroach, {name}, but you’re a complete shit-filled failure",
    "Jesus fucking Christ, {name}, you’re such a goddamn embarrassment, crawl into a ditch",
    "Certified fuckwit moment, brought to you by {name}’s pathetic, shit-smeared existence",
    "Get a fucking grip, {name}, you’re a revolting, puss-dripping mess nobody can stomach",
    "Holy shit, {name}, your stupidity is a fucking crime against all human intelligence",
    "Take a fucking hike, {name}, you’re a putrid skidmark on the universe’s crusty underwear",
    "Damn, {name}, you’re so fucking useless, even a cesspool would spit you out",
    "Keep your rancid trap shut, {name}, you’re a whining, shit-for-brains waste of oxygen",
    "Go fuck yourself raw, {name}, you’re a pitiful, syphilitic excuse for a person",
    "Christ, {name}, your face is a fucking insult to every poor bastard who sees it",
    "Shut your diseased hole, {name}, you’re a vile, shit-slurping piece of garbage",
    "Wow, {name}, you’re such a fucking brain-dead moron, it’s almost sad how pathetic you are",
    "Get lost, {name}, you’re a goddamn walking miscarriage of any shred of decency",
    "Choke on your own bullshit, {name}, you’re a festering pile of human waste",
    "Fuck off, {name}, you’re a slimy, ass-licking failure who reeks of desperation",
    "You’re a fucking disgrace, {name}, a moldy, cum-soaked rag not even rats would touch",
    "Eat shit and die, {name}, you’re a putrid, cock-sucking leech on society’s balls",
    "Go crawl back to your shithole, {name}, you’re a fucking insult to every living thing",
]


@bot.command()
# pyright: ignore[reportArgumentType]
async def cuss(ctx, *, person_name: str = None):  # type: ignore
    if not person_name:
        await ctx.send("❌ Please provide a name after !cuss")
        return

    if not cuss_list:
        await ctx.send("⚠️ No cusses defined yet! Fill in the cuss_list in the code.")
        return

    chosen_cuss = random.choice(cuss_list)
    response = chosen_cuss.format(name=person_name)
    await ctx.send(response)


@bot.event
async def on_message(message):
    # Prevent the bot from replying to itself
    if message.author == bot.user:
        return

    # Example: if someone says "sybau"
    sent_message = message.content.lower()
    if "sybau" in sent_message:
        await message.channel.send(f"BRO {message.author.display_name.upper()} YOU SHUT YOUR BITCHASS UP MF YOU SOUND GAY AS FUCK!")

    # Example: if someone says "goodnight"
    if "goodnight" in sent_message or "good night" in sent_message or "gnite" in sent_message:
        await message.channel.send("🌙 Sweet dreams!")

    if "goodmorning" in sent_message or "good morning" in sent_message:
        await message.channel.send("🎂 Good morning muffins!")

    if "wrap" in sent_message:
        await message.add_reaction("🌯")

    if "sugarbun" in sent_message or " sb" in sent_message or "sb " in sent_message:
        await message.add_reaction("🫓")

    if "type shi" in sent_message or "type shit" in sent_message or "typeshi" in sent_message or "typeshit" in sent_message or "type type" in sent_message:
        await message.add_reaction("🖕")

    if "nigga" in sent_message or "niggi" in sent_message or "niggesh" in sent_message or "negro" in sent_message or "negroni" in sent_message:
        await message.add_reaction("👨🏿")

    if "actually" in sent_message:
        await message.add_reaction("☝️")
        await message.add_reaction("🤓")
    # Make sure normal commands still work
    await bot.process_commands(message)


# Run the bot using secret token


@bot.command()
# pyright: ignore[reportArgumentType]
async def lyrics(ctx, *, song_name: str = None):  # type: ignore
    if not song_name:
        await ctx.send("🎵 Please provide a song name. Example: `!lyrics Bohemian Rhapsody`")
        return

    try:
        # Fetch synced lyrics (timestamps + text)
        lyrics = syncedlyrics.search(song_name)

        if not lyrics:
            await ctx.send(f"❌ Couldn't find synced lyrics for **{song_name}**.")
            return

        # SyncedLyrics returns a raw LRC-style string (with timestamps)
        # If you want just the text, you can strip timestamps
        lines = []
        for line in lyrics.splitlines():
            if "]" in line:  # format is [mm:ss.xx] lyric
                parts = line.split("]")
                if len(parts) > 1 and parts[1].strip():
                    lines.append(parts[1].strip())

        clean_lyrics = "\n".join(lines) if lines else lyrics

        # Discord messages have a 2000 char limit
        if len(clean_lyrics) > 2000:
            # Send in chunks if lyrics are too long
            for i in range(0, len(clean_lyrics), 2000):
                await ctx.send(clean_lyrics[i:i+2000])
        else:
            await ctx.send(f"🎤 Singing **{song_name}**:\n\n{clean_lyrics}")

    except Exception as e:
        await ctx.send(f"⚠️ Error while fetching lyrics: {e}")


@bot.command()
# pyright: ignore[reportArgumentType]
async def play(ctx, *, file_path: str = None):  # type: ignore
    """Play an audio file from your system (must be accessible to the bot)."""
    if not file_path:
        await ctx.send("⚠️ Please provide a file path. Example: `!play song.mp3`")
        return

    voice_client = ctx.voice_client
    if not voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send("❌ You must be in a voice channel!")
            return

    # Ensure FFmpeg is installed and available in PATH
    audio_source = discord.FFmpegPCMAudio(file_path)

    if not voice_client.is_playing():
        voice_client.play(audio_source, after=lambda e: print(
            f"Finished playing: {e}"))
        await ctx.send(f"🎶 Now playing: `{file_path}`")
    else:
        await ctx.send("⚠️ Already playing something!")


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc: voice_recv.VoiceRecvClient = await channel.connect(cls=voice_recv.VoiceRecvClient)
        await ctx.send(f"✅ Joined {channel} and ready to listen.")
    else:
        await ctx.send("❌ You must be in a voice channel first!")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the channel")
    else:
        await ctx.send("❌ I'm not in a voice channel!")


@bot.command()
async def mazak(ctx):
    """Send the mazak image to the chat."""
    image_path = ROOT / "assets/images" / \
        random.choice(["mazak1.png", "mazak2.png", "mazak3.png", "mazak4.png"])
    if os.path.exists(image_path):
        await ctx.send("👐 MAZAK THA 👐")
        await ctx.send(file=discord.File(image_path))
    else:
        await ctx.send("❌ Could not find mazak.png!")

        # Harry Potter House Scoring System

houses = {
    "gryffindor": 0,
    "hufflepuff": 0,
    "ravenclaw": 0,
    "slytherin": 0
}

HOUSE_FILE = ROOT / "house_points.json"


def load_house_points():
    if os.path.exists(HOUSE_FILE):
        with open(HOUSE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return {k: int(v) for k, v in data.items()}
            except Exception:
                return houses.copy()
    return houses.copy()


def save_house_points():
    with open(HOUSE_FILE, "w", encoding="utf-8") as f:
        json.dump(houses, f)


# Load house points at startup
houses.update(load_house_points())


@bot.command()
async def award(ctx, house: str = None, points: int = None):  # type: ignore
    """Add points to a house or show current house scores."""
    if house is None:
        # Show current scores
        msg = "**🏆 House Points 🏆**\n"
        for h, pts in houses.items():
            msg += f"**{h.title()}**: {pts} points\n"
        await ctx.send(msg)
        return

    house = house.lower()
    if house not in houses:
        await ctx.send("❌ Invalid house! Choose from Gryffindor, Hufflepuff, Ravenclaw, Slytherin.")
        return

    if points is None:
        await ctx.send("❌ Please specify the number of points to add or subtract.")
        return

    houses[house] += points
    save_house_points()
    await ctx.send(f"✅ Updated {house.title()}! New total: {houses[house]} points.")


@bot.command()
async def housetally(ctx):
    """Show the current house points tally."""
    sorted_houses = sorted(houses.items(), key=lambda x: x[1], reverse=True)
    msg = "**🏅 House Points Tally 🏅**\n"
    for h, pts in sorted_houses:
        msg += f"**{h.title()}**: {pts} points\n"
    await ctx.send(msg)


@bot.command()
async def bye(ctx):
    gif_path = ROOT / "assets/videos/bye.gif"
    if os.path.exists(gif_path):
        await ctx.send(file=discord.File(gif_path))
    else:
        await ctx.send("❌ Could not find bye.gif!")


bot.run(os.getenv("BOT_TOKEN"))  # pyright: ignore[reportArgumentType]
