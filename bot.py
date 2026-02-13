import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="MANDEM$ Server 👀"
        )
    )
    print(f"✅ Online! Logged in as {bot.user}")

# ─── WELCOME ───
@bot.event
async def on_member_join(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = discord.Embed(
            title=f"Welcome sa {member.guild.name}! 🎉",
            description=f"Kamusta {member.mention}!",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name="👥 Members", value=member.guild.member_count)
        await channel.send(embed=embed)

# ─── MODERATION ───
@bot.tree.command(name="kick", description="Kick ng member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ Na-kick si {member.mention} | {reason}")

@bot.tree.command(name="ban", description="Ban ng member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Na-ban si {member.mention} | {reason}")

@bot.tree.command(name="mute", description="Mute ng member")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 10):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 Na-mute si {member.mention} ng {minutes} mins!")

@bot.tree.command(name="clear", description="Mag-clear ng messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int = 5):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🗑️ Na-clear ang {amount} messages!", ephemeral=True)

# ─── FUN ───
@bot.tree.command(name="coinflip", description="Mag-flip ng coin")
async def coinflip(interaction: discord.Interaction):
    import random
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await interaction.response.send_message(f"**{result}**!")

# ─── HELP ───
@bot.tree.command(name="help", description="Lahat ng commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 MANDEM$ Commands", color=discord.Color.purple())
    embed.add_field(name="⚔️ Mod", value="`/kick` `/ban` `/mute` `/clear`", inline=False)
    embed.add_field(name="🎮 Fun", value="`/coinflip`", inline=False)
    embed.set_footer(text="MANDEM$ Bot ❤️")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("TOKEN"))
```

---

**Requirements.txt:**
```
discord.py
python-dotenv
```

**Procfile:**
```
worker: python bot.py
