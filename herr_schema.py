import os
import discord
import requests
from icalendar import Calendar
from datetime import datetime, timedelta
from discord.ext import commands, tasks
import pytz

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents,case_insensitive=True)

def get_schedule(url, date):
    ics = requests.get(url).text
    cal = Calendar.from_ical(ics)
    local_timezone = pytz.timezone("Europe/Stockholm")
    
    events = []
    for event in cal.walk("vevent"):
        start = event.get("dtstart").dt.astimezone(local_timezone)
        end = event.get("dtend").dt.astimezone(local_timezone)
        if start.date() == date:
            summary = event.get("summary")
            time_range = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
            events.append((time_range, summary))
    
    return events

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    daily_schedule.start()

@tasks.loop(hours=24)
async def daily_schedule():
    channel_id = 123  # Replace with your channel ID
    channel = bot.get_channel(channel_id)
    
    local_timezone = pytz.timezone("Europe/Stockholm")
    today = datetime.now(local_timezone).date()
    
    events = get_schedule("https://cloud.timeedit.net/nackademin/web/1/ri65E5ZQ1Q48eCQZ05Q7dtDQZ58ZZ5D9BuAYZ6Qy875tAnFb0FCQ74DF35585AD8B23AA2D4.ics", today)
    
    if events:
        message = f"Dagens schema ({today.strftime('%Y-%m-%d')} - {today.strftime('%A')}):\n"
        for time_range, summary in events:
            message += f"{time_range}: {summary}\n"
    else:
        message = f"Inga händelser idag ({today.strftime('%Y-%m-%d')} - {today.strftime('%A')})."
    
    await channel.send(message)

@bot.command()
async def schema(ctx, date_str=None):
    if date_str is None:
        local_timezone = pytz.timezone("Europe/Stockholm")
        date = datetime.now(local_timezone).date()
    else:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            await ctx.send("Ange datum i formatet YYYY-MM-DD.")
            return

    events = get_schedule("https://cloud.timeedit.net/nackademin/web/1/ri65E5ZQ1Q48eCQZ05Q7dtDQZ58ZZ5D9BuAYZ6Qy875tAnFb0FCQ74DF35585AD8B23AA2D4.ics", date)

    if events:
        message = f"Schema för {date.strftime('%Y-%m-%d')} - {date.strftime('%A')}:\n"
        for time_range, summary in events:
            message += f"{time_range}: {summary}\n"
    else:
        message = f"Inga händelser för {date.strftime('%Y-%m-%d')} - {date.strftime('%A')}."
    await ctx.send(message)

# Replace "YOUR_DISCORD_BOT_TOKEN" with your actual bot token
bot.run("token")
