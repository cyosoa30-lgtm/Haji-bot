import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── TRACKERS ───
join_tracker = defaultdict(list)
channel_tracker = defaultdict(list)
role_tracker = defaultdict(list)
ban_tracker = defaultdict(list)

RAID_THRESHOLD = 5      # joins in 10 seconds
ACTION_THRESHOLD = 3    # actions in 10 seconds

# ─── ON READY ───
@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🛡️ Protecting Server"
        )
    )
    print(f"✅ Online! Logged in as {bot.user}")

# ══════════════════════════════════════
#           ANTI RAID
# ══════════════════════════════════════

@bot.event
async def on_member_join(member: discord.Member):
    now = datetime.datetime.now().timestamp()
    guild_id = member.guild.id

    join_tracker[guild_id] = [t for t in join_tracker[guild_id] if now - t < 10]
    join_tracker[guild_id].append(now)

    # Kung 5+ joins in 10 seconds = RAID
    if len(join_tracker[guild_id]) >= RAID_THRESHOLD:
        try:
            await member.kick(reason="⚠️ Anti-Raid Protection")
        except:
            pass

        log_channel = discord.utils.get(member.guild.text_channels, name="mod-logs")
        if log_channel:
            embed = discord.Embed(
                title="🚨 RAID DETECTED!",
                description=f"Maraming users ang nag-join nang mabilis!\n{member.mention} ay na-kick!",
                color=discord.Color.red()
            )
            embed.add_field(name="Joins", value=f"{len(join_tracker[guild_id])} in 10 seconds")
            await log_channel.send(embed=embed)

# ══════════════════════════════════════
#           ANTI NUKE
# ══════════════════════════════════════

# ─── Channel Delete Protection ───
@bot.event
async def on_guild_channel_delete(channel):
    now = datetime.datetime.now().timestamp()
    guild = channel.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        user = entry.user
        if user.bot:
            return

        channel_tracker[user.id] = [t for t in channel_tracker[user.id] if now - t < 10]
        channel_tracker[user.id].append(now)

        if len(channel_tracker[user.id]) >= ACTION_THRESHOLD:
            try:
                await user.timeout(datetime.timedelta(hours=24), reason="Anti-Nuke: Mass Channel Delete")
            except:
                pass

            log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
            if log_channel:
                embed = discord.Embed(
                    title="🚨 NUKE DETECTED!",
                    description=f"{user.mention} ay nag-delete ng maraming channels!",
                    color=discord.Color.red()
                )
                await log_channel.send(embed=embed)

# ─── Role Delete Protection ───
@bot.event
async def on_guild_role_delete(role):
    now = datetime.datetime.now().timestamp()
    guild = role.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
        user = entry.user
        if user.bot:
            return

        role_tracker[user.id] = [t for t in role_tracker[user.id] if now - t < 10]
        role_tracker[user.id].append(now)

        if len(role_tracker[user.id]) >= ACTION_THRESHOLD:
            try:
                await user.timeout(datetime.timedelta(hours=24), reason="Anti-Nuke: Mass Role Delete")
            except:
                pass

            log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
            if log_channel:
                embed = discord.Embed(
                    title="🚨 NUKE DETECTED!",
                    description=f"{user.mention} ay nag-delete ng maraming roles!",
                    color=discord.Color.red()
                )
                await log_channel.send(embed=embed)

# ─── Mass Ban Protection ───
@bot.event
async def on_member_ban(guild, user):
    now = datetime.datetime.now().timestamp()

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        banner = entry.user
        if banner.bot:
            return

        ban_tracker[banner.id] = [t for t in ban_tracker[banner.id] if now - t < 10]
        ban_tracker[banner.id].append(now)

        if len(ban_tracker[banner.id]) >= ACTION_THRESHOLD:
            try:
                await banner.timeout(datetime.timedelta(hours=24), reason="Anti-Nuke: Mass Ban")
            except:
                pass

            log_channel = discord.utils.get(guild.text_channels, name="mod-logs")
            if log_channel:
                embed = discord.Embed(
                    title="🚨 MASS BAN DETECTED!",
                    description=f"{banner.mention} ay nag-ban ng maraming members!",
                    color=discord.Color.red()
                )
                await log_channel.send(embed=embed)

# ══════════════════════════════════════
#           SLASH COMMANDS
# ══════════════════════════════════════

@bot.tree.command(name="antinuke", description="Anti-Nuke status")
@app_commands.checks.has_permissions(administrator=True)
async def antinuke(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ Anti-Nuke Status",
        color=discord.Color.green()
    )
    embed.add_field(name="Mass Channel Delete", value="✅ Active", inline=False)
    embed.add_field(name="Mass Role Delete", value="✅ Active", inline=False)
    embed.add_field(name="Mass Ban", value="✅ Active", inline=False)
    embed.add_field(name="Anti Raid", value="✅ Active", inline=False)
    embed.set_footer(text="🛡️ Server is Protected!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="antiraid", description="Anti-Raid status")
@app_commands.checks.has_permissions(administrator=True)
async def antiraid(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚨 Anti-Raid Status",
        description=f"Kick ang users kung **{RAID_THRESHOLD}+ joins** sa loob ng **10 seconds**",
        color=discord.Color.green()
    )
    embed.add_field(name="Status", value="✅ Active")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Lahat ng commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ Anti-Nuke & Anti-Raid Bot", color=discord.Color.purple())
    embed.add_field(name="🛡️ Protection", value="`/antinuke` `/antiraid`", inline=False)
    embed.add_field(name="📋 Logs", value="Pumunta sa **#mod-logs** channel", inline=False)
    embed.set_footer(text="Bot is always watching 👀")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("MTQ3MTY4MzM2OTMwMDM5NDA5NA.GvORDY.kKgdMaZXH1OwMURglimg8b_T-7W5C7Y3xNHFDg"))
```

---

**requirements.txt:**
```
discord.py
python-dotenv
```

**Procfile:**
```
worker: python bot.py
