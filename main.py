import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 봇 실행됨: {bot.user}")
    for guild in bot.guilds:
        print(f'서버 이름: {guild.name} (ID: {guild.id})')
    total_members = sum(guild.member_count for guild in bot.guilds)
    activity = discord.Game(f"{total_members}명의 유저와 함께함")
    await bot.change_presence(activity=activity)

async def get_or_create_log_channel(guild: discord.Guild):
    # 1. 주제가 "hyerin-log"인 기존 채널 찾기
    for channel in guild.text_channels:
        if channel.topic and "hyerin-log" in channel.topic.lower():
            return channel

    # 2. 없다면 새로 생성
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False)
    }
    for role in guild.roles:
        if role.permissions.administrator:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True)
    try:
        log_channel = await guild.create_text_channel(
            "hyerin-log",
            overwrites=overwrites,
            topic="hyerin-log"
        )
        return log_channel
    except discord.Forbidden:
        return None

async def check_role_hierarchy(ctx, member):
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("🚫 당신보다 높은 역할을 가진 사용자에게 이 명령어를 사용할 수 없습니다.")
        return False
    return True

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "사유 없음"):
    if not await check_role_hierarchy(ctx, member): return
    try:
        await member.ban(reason=reason)
        try:
            await member.send(f"당신은 {ctx.guild.name} 서버에서 밴당했습니다. 사유: {reason}")
        except:
            await ctx.send(f"{member}님에게 DM을 보낼 수 없습니다.")
        await ctx.send(f"{member}님을 밴했습니다. 사유: {reason}")
        log_channel = await get_or_create_log_channel(ctx.guild)
        if log_channel:
            embed = discord.Embed(title="🔨 사용자 밴", color=discord.Color.red(), timestamp=ctx.message.created_at)
            embed.add_field(name="밴 대상", value=member.mention)
            embed.add_field(name="사유", value=reason)
            embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await log_channel.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ 밴 처리 중 오류가 발생했습니다: {e}")

@bot.command(name="개발자")
async def developer(ctx):
    await ctx.send("혜린 ㅣ discord.gg/ilbe")

@bot.command()
async def 도움말(ctx):
    commands_list = [command.name for command in bot.commands]
    await ctx.send("사용 가능한 명령어:\n" + ", ".join(commands_list))

@bot.command()
@commands.has_permissions(manage_messages=True)
async def 청소(ctx, amount: int = 5):
    if amount < 1:
        await ctx.send("1개 이상의 메시지를 삭제해야 합니다.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {len(deleted)-1}개의 메시지를 삭제했습니다!", delete_after=2)
    log_channel = await get_or_create_log_channel(ctx.guild)
    if log_channel:
        embed = discord.Embed(title="🧹 메시지 삭제", color=discord.Color.orange(), timestamp=ctx.message.created_at)
        embed.add_field(name="삭제 수", value=str(len(deleted)-1))
        embed.add_field(name="채널", value=ctx.channel.mention)
        embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await log_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def role(ctx, member: discord.Member, *, role_input: str):
    if not await check_role_hierarchy(ctx, member): return
    role = None
    if role_input.isdigit():
        role = discord.utils.get(ctx.guild.roles, id=int(role_input))
    if not role:
        role = discord.utils.get(ctx.guild.roles, name=role_input)
    if not role:
        await ctx.send(f"❌ 역할을 찾을 수 없습니다: `{role_input}`")
        return
    try:
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention}님에게 `{role.name}` 역할을 부여했습니다.")
        log_channel = await get_or_create_log_channel(ctx.guild)
        if log_channel:
            embed = discord.Embed(title="🎭 역할 부여", color=discord.Color.green(), timestamp=ctx.message.created_at)
            embed.add_field(name="대상 사용자", value=member.mention)
            embed.add_field(name="부여된 역할", value=role.name)
            embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await log_channel.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("🚫 봇에게 역할을 부여할 권한이 없습니다.")
    except Exception as e:
        await ctx.send(f"⚠️ 오류 발생: {e}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, time: int, *, reason="사유 없음"):
    if not await check_role_hierarchy(ctx, member): return
    try:
        duration = discord.utils.utcnow() + discord.timedelta(seconds=time)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"🔇 {member.mention}님을 {time}초 동안 타임아웃 시켰습니다. 사유: {reason}")
        log_channel = await get_or_create_log_channel(ctx.guild)
        if log_channel:
            embed = discord.Embed(title="🔇 사용자 타임아웃", color=discord.Color.greyple(), timestamp=ctx.message.created_at)
            embed.add_field(name="대상", value=member.mention)
            embed.add_field(name="시간", value=f"{time}초")
            embed.add_field(name="사유", value=reason)
            embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await log_channel.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ 오류 발생: {e}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def 해제(ctx, member: discord.Member):
    if not await check_role_hierarchy(ctx, member): return
    try:
        await member.remove_timeout()
        await ctx.send(f"🔈 {member.mention}님의 타임아웃을 해제했습니다.")
        log_channel = await get_or_create_log_channel(ctx.guild)
        if log_channel:
            embed = discord.Embed(title="🔈 타임아웃 해제", color=discord.Color.green(), timestamp=ctx.message.created_at)
            embed.add_field(name="대상", value=member.mention)
            embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await log_channel.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ 오류 발생: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="사유 없음"):
    if not await check_role_hierarchy(ctx, member): return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention}님을 킥했습니다. 사유: {reason}")
        log_channel = await get_or_create_log_channel(ctx.guild)
        if log_channel:
            embed = discord.Embed(title="👢 사용자 킥", color=discord.Color.dark_orange(), timestamp=ctx.message.created_at)
            embed.add_field(name="대상", value=member.mention)
            embed.add_field(name="사유", value=reason)
            embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await log_channel.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ 오류 발생: {e}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def 경고(ctx, member: discord.Member, *, reason="사유 없음"):
    if not await check_role_hierarchy(ctx, member): return
    await ctx.send(f"⚠️ {member.mention}님에게 경고를 부여했습니다. 사유: {reason}")
    log_channel = await get_or_create_log_channel(ctx.guild)
    if log_channel:
        embed = discord.Embed(title="⚠️ 사용자 경고", color=discord.Color.yellow(), timestamp=ctx.message.created_at)
        embed.add_field(name="대상", value=member.mention)
        embed.add_field(name="사유", value=reason)
        embed.set_footer(text=f"처리자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await log_channel.send(embed=embed)

@bot.command(name="명령어")
async def 명령어(ctx, *, command_name: str = None):
    if not command_name:
        embed = discord.Embed(
            title="📘 사용 가능한 명령어 목록",
            description="명령어에 대한 자세한 정보를 보려면 `>명령어 [명령어이름]` 을 입력하세요.",
            color=discord.Color.green()
        )
        for name, desc in command_descriptions.items():
            embed.add_field(name=f"> {name}", value=desc.split("\n")[0], inline=False)
        embed.set_footer(text=f"요청자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=embed)
    else:
        command_name = command_name.lower()
        description = command_descriptions.get(command_name)
        if description:
            embed = discord.Embed(
                title=f"📘 명령어 정보: `{command_name}`",
                description=description,
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"요청자: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ `{command_name}` 명령어를 찾을 수 없습니다.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        return

command_descriptions = {
    "ban": "🚫 사용자를 서버에서 밴합니다.\n사용법: `>ban @유저 [사유]`",
    "kick": "👢 사용자를 서버에서 추방합니다.\n사용법: `>kick @유저 [사유]`",
    "mute": "🔇 사용자를 일정 시간 동안 타임아웃합니다.\n사용법: `>mute @유저 시간(초) [사유]`",
    "해제": "🔈 타임아웃된 사용자를 복구합니다.\n사용법: `>해제 @유저`",
    "청소": "🧹 채널의 메시지를 삭제합니다.\n사용법: `>청소 [개수]`",
    "role": "🎭 특정 역할을 유저에게 부여합니다.\n사용법: `>role @유저 역할이름 또는 역할ID`",
    "도움말": "❓ 사용 가능한 명령어 목록을 보여줍니다.\n사용법: `>도움말`",
    "개발자": "👨‍💻 봇 개발자 정보를 표시합니다.\n사용법: `>개발자`",
    "명령어": "ℹ️ 특정 명령어에 대한 설명을 표시합니다.\n사용법: `>명령어 [명령어이름]`",
}

bot.run(os.getenv("BOT_TOKEN"))

