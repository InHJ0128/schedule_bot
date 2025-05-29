import discord
from discord.ext import commands

from dotenv import load_dotenv
import os

import base64
import hashlib
import hmac
import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import datetime

import requests



def save_to_db(timetable, user_id, user_name, semester, url):
    payload = {
    "user_id": user_id,
    "user_name": user_name,
    "semester": semester,
    "secret": "iwantsave",
    "type": "bot",
    "timetable": timetable
    }
    try:
        res = requests.post("http://inhuckjin85.dothome.co.kr/python/save_schedule.php", json=payload, verify=False)
        print(f"응답 코드: {res.status_code}")
        print(f"응답 본문:\n{res.text}")
        data = res.json()
        if data.get("success"):
            payload2 = {
            "user_id": user_id,
            "user_name": user_name,
            "secret": "userlist",
            "url": url
            }
            res2 = requests.post("http://inhuckjin85.dothome.co.kr/python/save_user.php", json=payload2, verify=False)
            print(f"응답 코드2: {res2.status_code}")
            print(f"응답 본문2:\n{res2.text}")
            return data
        else:
            print("서버 응답 실패:", data.get("message"))
            return data
    except Exception as e:
        print("요청 오류:", e)
        return {
            "success": False,
            "message": f"요청 오류: {e}"
        }

def delete_to_db(user_id, semester):
    payload = {
    "user_id": user_id,
    "semester": semester,
    "secret": "iwantdelete",
    }
    try:
        res = requests.post("http://inhuckjin85.dothome.co.kr/python/delete_schedule.php", json=payload, verify=False)
        data = res.json()
        if data.get("success"):
            return True
        else:
            print("서버 응답 실패:", data.get("message"))
            return False
    except Exception as e:
        print("요청 오류:", e)
        return False

def load_from_db(user_id=None, user_name=None, semester=None):
    payload = {
        "secret": "iwantload",
        "semester": semester,
    }
    if user_id:
        payload["user_id"] = user_id
    elif user_name:
        payload["user_name"] = user_name

    try:
        res = requests.post("http://inhuckjin85.dothome.co.kr/python/load_schedule.php", json=payload)
        data = res.json()
        if data.get("success"):
            return data["timetable"]
        else:
            print("서버 응답 실패:", data.get("message"))
            return []
    except Exception as e:
        print("요청 오류:", e)
        return []
def trim_time(time_str):
    return time_str[:5] if time_str and len(time_str) >= 5 else time_str
    
def get_current_semester():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    if month <= 7:
        return f"{year}년1학기"
    else:
        return f"{year}년2학기"

def fetch_timetable_html(url):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # 봇 감지 우회
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135 Safari/537.36")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)  # chromedriver.exe는 같은 폴더에 있어야 함

    try:
        driver.get(url)
        html = driver.page_source
        return html
    finally:
        driver.quit()



def px_to_time(px):
    base_top = 450  # 오전 9시
    px_per_hour = 50
    total_minutes = (int(px) - base_top)
    hours = total_minutes // px_per_hour + 9
    minutes = (total_minutes % px_per_hour) * 60 // px_per_hour
    minutes = minutes / 10
    minutes = int(minutes)*10
    return f"{hours:02}:{minutes:02}"

def parse_timetable(html):
    soup = BeautifulSoup(html, 'html.parser')

    active_li = soup.select_one('div.menu ol li.active a')
    if active_li:
        semester = active_li.text.strip().replace(" ", "") 
    else:
        semester = "알수없음"
    days = ['월', '화', '수', '목', '금']
    columns = soup.select('table.tablebody td')  # 요일별 열
    

    for day_index, td in enumerate(columns[:5]):
        subjects = td.select('div.cols > div.subject')
        for sub in subjects:
            style = sub.get('style', '')
            top = next((s for s in style.split(';') if 'top' in s), None)
            height = next((s for s in style.split(';') if 'height' in s), None)
            if top and height:
                top_px = int(top.split(':')[1].replace('px', '').strip())
                height_px = int(height.split(':')[1].replace('px', '').strip())
    
    timetable = []
    for day_index, td in enumerate(columns[:5]):  # 월~금
        subjects = td.select('div.cols > div.subject')
        for sub in subjects:
            name = sub.find('h3').text.strip()
            prof = sub.find('em').text.strip()
            room = sub.find('span').text.strip()

            style = sub.get('style', '')
            top = next((s for s in style.split(';') if 'top' in s), None)
            height = next((s for s in style.split(';') if 'height' in s), None)
            if top and height:
                top_px = int(top.split(':')[1].replace('px', '').strip())
                height_px = int(height.split(':')[1].replace('px', '').strip())
                start_time = px_to_time(top_px)
                end_time = px_to_time(top_px + height_px)
            else:
                start_time = end_time = "Unknown"
            
            timetable.append({
                'semester': semester,
                'day': days[day_index],
                'name': name,
                'professor': prof,
                'room': room,
                'start': start_time,
                'end': end_time
            })

    return timetable

intents = discord.Intents.default()
intents.message_content = True  # 메시지 읽기 권한 설정

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'봇 로그인 성공: {bot.user}')


@bot.command()
#@commands.has_permissions(manage_channels=True)
async def 시간표(ctx, cm2=None, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        await ctx.send("❌ 메시지를 삭제할 권한이 없습니다.")
    if cm2 == None:
        guild = ctx.guild
        category_name = "시간표 개인방"
        
        # 1. 카테고리 찾기 (없으면 None)
        category = discord.utils.get(guild.categories, name=category_name)
        
        # 2. 없으면 새로 생성
        if category is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                ctx.author: discord.PermissionOverwrite(view_channel=True),
                bot.user: discord.PermissionOverwrite(view_channel=True)
            }

            category = await guild.create_category(name="시간표 개인방", overwrites=overwrites)
        # 권한 설정: 유저 + 봇만 보기 가능
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            bot.user: discord.PermissionOverwrite(read_messages=True)
        }

        # 채널 이름은 고유하게: 닉네임 또는 ID
        channel_name = f"🔒-비밀방-{ctx.author.display_name}".replace(" ", "-")
        # 동일 이름 채널이 이미 존재하는지 확인
        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            await ctx.send(f"{ctx.author.mention}, 이미 개인 채널이 존재합니다: {existing.mention}")
            try:
                await ctx.author.send(f"🔒 이미 존재하는 개인 채널입니다: {existing.mention}")
            except discord.Forbidden:
                await ctx.send("📭 DM을 보낼 수 없습니다. 유저의 DM 설정을 확인해주세요.")
            return

        # 채널 생성
        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)

        await channel.send(f"""```
        {ctx.author.display_name}님, 여기는 당신만 접근할 수 있는 채널입니다.
        간단히 봇 사용법을 설명드리겠습니다.

    * 시간표 추가
        - 에브리타임 시간표 우측상단 톱니바퀴를 누르시면 URL공유가 있습니다.
        - '!시간표 추가 (URL)' 을 입력하시면 시간표가 데이터베이스에 저장됩니다.
        - 시간표 수정은 에브리타임 앱에서 수정한후 추가하면 수정됩니다.

    *시간표 조회
        - '!시간표 확인 (년도학기)' 
        - '!시간표 조회 (이름) (년도학기)'
            ㄴ(년도학기)를 생략하시면 현재 학기를 보여줍니다.

    *시간표 삭제
        - '!시간표 삭제 (년도학기)'
            ㄴ(년도학기)를 생략하시면 현재 학기를 삭제합니다.

    *현재 채팅방 나가기
        - '!시간표 채팅방나가기'

    - 더 편한 시간표 수정 및 조회는 웹페이지를 통해서 가능합니다.
        '!시간표 사이트접속'
```""")


    if cm2 == "추가" and args[0]:
        msg = await ctx.send("⌛ 시간표를 불러오는 중입니다...")
        html = fetch_timetable_html(args[0])
        timetable = parse_timetable(html)

        if not timetable:
            await ctx.send("❌ 시간표 항목을 찾지 못했습니다. 공개된 에브리타임 링크인지 확인해주세요.")
            return

        # 요일 순서를 사전으로 지정
        day_order = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4}

        # 정렬 기준을 요일 순서 + 시작 시간으로 설정
        timetable.sort(key=lambda x: (day_order.get(x['day'], 99), x['start']))

        # 메시지 구성 (2000자 제한 대비 분할)
        max_len = 1900  # 여유를 두고 1900자 제한
        output = "```\n📚 시간표\n\n"
        check = True
        messages = []

        for t in timetable:
            if check:
                semester = t.get('semester', '알 수 없음')
                output += f"📆 학기: {semester}\n\n"
                check = False

            line = f"[{t['day']}] {t['name']} ({t['professor']}) - {t['room']} / {t['start']}~{t['end']}\n"

            if len(output) + len(line) >= max_len:
                output += "```"
                messages.append(output)
                output = "```\n" + line
            else:
                output += line

        output += "```"
        messages.append(output)
        data = save_to_db(timetable, ctx.author.id, ctx.author.display_name, semester, args[0])
        # 메시지 출력
        if data.get("success") :
            await msg.edit(content=messages[0])
            for part in messages[1:]:
                await ctx.send(part)
        else:
            await msg.edit(content="❌ 시간표 저장에 실패하였습니다.")
        
        

    if cm2 == "확인":
        msg = await ctx.send("⏳ 시간표를 불러오는 중입니다...")
        semester = args[0] if args else get_current_semester()
        user_id = ctx.author.id
        user_name = ctx.author.display_name
        timetable = load_from_db(user_id=user_id, user_name=user_name, semester=semester)
        if not timetable:
            await msg.edit(content="❌ 해당 시간표를 찾을 수 없습니다.")
            return
        day_order = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4}

        # 정렬 기준을 요일 순서 + 시작 시간으로 설정
        timetable.sort(
            key=lambda x: (
                day_order.get(x.get('day'), 99),
                trim_time(x.get('start_time', '00:00'))
            )
        )

        
        # 4️⃣ 메시지 구성 (2000자 제한 대비 분할)
        max_len = 1900  # 여유를 두고 1900자 제한
        output = "```\n📚 시간표\n\n"
        check = True
        messages = []

        for t in timetable:
            if check:
                semester = t.get('semester', '알 수 없음')
                output += f"📆 학기: {semester}\n\n"
                check = False

            line = f"[{t['day']}] {t['name']} ({t['professor']}) - {t['room']} / {trim_time(t['start_time'])}~{trim_time(t['end_time'])}\n"

            if len(output) + len(line) >= max_len:
                output += "```"
                messages.append(output)
                output = "```\n" + line
            else:
                output += line

        output += "```"
        messages.append(output)
        # 5️⃣ 메시지 출력
        await msg.edit(content=messages[0])
        for part in messages[1:]:
            await ctx.send(part)
    if cm2 == "조회":
        if not args:
            await ctx.send("```\n이름을 입력해주세요. 예: !시간표 조회 홍길동 2025년1학기\n```")
            return
        msg = await ctx.send("⏳ 시간표를 불러오는 중입니다...")
        user_name = args[0]
        semester = args[1] if len(args) > 1 else get_current_semester()
        user_id = None
        timetable = load_from_db(user_id=user_id, user_name=user_name, semester=semester)
        if not timetable:
            await msg.edit("❌ 해당 시간표를 찾을 수 없습니다.")
            return
        day_order = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4}
        
        # 정렬 기준을 요일 순서 + 시작 시간으로 설정
        timetable.sort(
            key=lambda x: (
                day_order.get(x.get('day'), 99),
                trim_time(x.get('start_time', '00:00'))
            )
        )

        # 4️⃣ 메시지 구성 (2000자 제한 대비 분할)
        max_len = 1900  # 여유를 두고 1900자 제한
        output = f"```\n📚 {args[0]}님의 시간표\n\n"
        check = True
        messages = []

        for t in timetable:
            if check:
                semester = t.get('semester', '알 수 없음')
                output += f"📆 학기: {semester}\n\n"
                check = False

            line = f"[{t['day']}] {t['name']} ({t['professor']}) - {t['room']} / {trim_time(t['start_time'])}~{trim_time(t['end_time'])}\n"

            if len(output) + len(line) >= max_len:
                output += "```"
                messages.append(output)
                output = "```\n" + line
            else:
                output += line

        output += "```"
        messages.append(output)
        # 5️⃣ 메시지 출력
        await msg.edit(content=messages[0])
        for part in messages[1:]:
            await ctx.send(part)
    if cm2 == "삭제":
        semester = args[0] if args else get_current_semester()
        user_id = ctx.author.id
        success = delete_to_db(ctx.author.id, semester)
        if success :
            await ctx.send("시간표를 삭제하였습니다.")
        else :
            await ctx.send("❌ 삭제에 실패하였습니다.")
    if cm2 == "채팅방나가기":
        guild = ctx.guild
        channel_name = f"🔒-비밀방-{ctx.author.display_name}".replace(" ", "-").lower()

        # 현재 채널이 그 채널인지 또는 채널 목록에서 찾기
        target = discord.utils.get(guild.text_channels, name=channel_name)

        if target:
            await target.delete()
        else:
            await ctx.send("❌ 삭제할 비밀 채널이 존재하지 않아요.")
    if cm2 == "사이트접속":
        SECRET_KEY = "createSite"
        user_id = ctx.author.id
        user_name = ctx.author.display_name
        timestamp = int(time.time())
        payload = f"{user_id}:{timestamp}"
        sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

        bundle = f"{user_id}:{timestamp}:{sig}:{user_name}"

        token = base64.urlsafe_b64encode(bundle.encode()).decode()

        login_url = f"http://inhuckjin85.dothome.co.kr/schedule/web_login.php?token={token}"
        #login_url = f"http://schedule.o-r.kr?token={token}"
        await ctx.send(f"🔐 로그인 링크입니다:\n{login_url}")

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot.run(TOKEN) 