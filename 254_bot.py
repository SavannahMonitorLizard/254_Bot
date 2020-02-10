import os, discord, datetime, random, json, requests, time, threading, asyncio
from discord.ext import commands

with open("secrets.json") as json_file:
    secrets = json.load(json_file)
TOKEN = secrets["token"]
authKey = secrets["authKey"]

dominance = True
assert dominance

blessedTeams = ["254", "118", "1323"]
teams = ["33", "118", "148", "254", "330", "341", "930", "971", "973", "1114", "1155", "1323", "1678", "1986", "2056", "2767", "2910", "5160"]
teamsHelp = ", ".join(teams)
information = {"Version": "2.1.0", "Teams": teamsHelp}

bot = commands.Bot(command_prefix='!', description="Bot commands")
bot.remove_command('help')

@bot.command(name="countdown", description="A counter until major events!")
async def countdown(ctx, event):
    if event.lower() != 'events':
        days, hours, minutes, seconds, valid = getTimeUntilEvent(event)
        if valid:
            response = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds until {event}!"
            embed = discord.Embed(title=event.title(), description=response, color=0x00ff00)
        else:
            response = "Invalid event"
            embed = discord.Embed(title='Events', description="Wake\nECU\nPembroke\nAsheville\nGuilford", color=0x00ff00)
    else:
        embed = discord.Embed(title='Events', description="Wake\nECU\nPembroke\nAsheville\nGuilford", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name='help', description="Get info on commands")
async def help(ctx):
    embed = discord.Embed(title="Commands", description='Here are the robot bot commands', color=0x00ff00)
    embed.add_field(name='Countdown', value='!countdown <insert event>', inline=False)
    embed.add_field(name='Teaminfo', value='!teaminfo <insert team>', inline=False)
    embed.add_field(name='Team image', value='<team number>', inline=False)
    embed.add_field(name='Robotinfo', value='!robotinfo <team number> <year (optional)>', inline=False)
    await ctx.send(embed=embed)

@bot.command(name="note", description="A note taker, will put notification at the start of robotics on applicable days")
async def note(ctx, note: str):
    if ctx.guild.id == 359482017093779456 or ctx.guild.id == 523962430179770369:
        allNotes = {}
        userID = ctx.message.author.id
        userID = str(userID)
        with open('notes.txt') as json_file:
            allNotes = json.load(json_file)
        if userID not in allNotes.keys():
            allNotes[userID] = allNotes.get(userID, [])
        allNotes[userID].append(note)
        with open('notes.txt', 'w') as outfile:
            json.dump(allNotes, outfile)
        await ctx.send('Note noted')

@bot.command(name="getnotes", description="")
async def getnotes(ctx):
    if ctx.guild.id == 359482017093779456 or ctx.guild.id == 523962430179770369:   
        userID = ctx.message.author.id
        userID = str(userID)
        notes = {}
        with open('notes.txt') as json_file:
            notes = json.load(json_file)
            try:
                notes = "\n\t - ".join(notes[userID])
                response = f"<@{userID}>'s notes\n\t - {notes}"
                await ctx.send(response)
            except KeyError:
                await ctx.send("You have no notes")

@bot.command(name="remind", description="remind us of the notes")
async def remind(ctx):
    if ctx.guild.id == 359482017093779456 or ctx.guild.id == 523962430179770369:
        userID = ctx.message.author.id
        if userID == 336714995582894095:
            try:
                response = ''
                response = notifyTeam()
                channel = bot.get_channel(523967513172770848)
                await channel.send(response)
            except UnboundLocalError:
                await ctx.send("There are no current notes")

@bot.command(name="delnote", description="delete a note")
async def delnote(ctx, note: str):
    if ctx.guild.id == 359482017093779456 or ctx.guild.id == 523962430179770369:   
        userID = ctx.message.author.id
        userID = str(userID)
        notes = {}
        with open('notes.txt') as json_file:
            notes = json.load(json_file)
        if note in notes[userID]:
            notes[userID].remove(note)
            await ctx.send("Note removed")
            with open('notes.txt', 'w') as outfile:
                json.dump(notes, outfile)
        else:
            await ctx.send("No such note exists")

@bot.command(name="teaminfo", description="get info on a team")
async def teaminfo(ctx, team):
    teamsinfo = {}
    response = requests.get(f'https://www.thebluealliance.com/api/v3/team/frc{team}', headers={"X-TBA-Auth-Key": authKey}).json()
    teamsinfo = response
    embed = discord.Embed(title="Team", description=team, color=0x00ff00)
    embed.add_field(name="Name", value=f"{teamsinfo['nickname']}", inline=False)
    embed.add_field(name='Location', value="%s, %s, %s, %s%s%s%s"%(teamsinfo['city'], teamsinfo['state_prov'], teamsinfo['country'], (teamsinfo['postal_code'] if teamsinfo['postal_code'] != None else ""), ("\nAddress: " + teamsinfo['address'] if teamsinfo['address'] != None else ""), ("\nLatitude: " + teamsinfo['lat'] if teamsinfo['lat'] != None else ""), (", Longitude: " + teamsinfo['lng'] if teamsinfo['lng'] != None else "")), inline=False)
    embed.add_field(name='Website', value=f'{teamsinfo["website"]}')
    embed.add_field(name="Rookie Year", value=f"{teamsinfo['rookie_year']}", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command(name='robotinfo', description='get info on a robot')
async def robotinfo(ctx, team, year=None):
    response = requests.get(f'https://www.thebluealliance.com/api/v3/team/frc{team}/robots', headers={"X-TBA-Auth-Key": authKey}).json()
    rInfo = []
    
    if year == None:
        for robot in response:
            rInfo.append(robot['year'])

        year = random.choice(rInfo)
    else:
        pass

    for robot in response:
        if robot['year'] == year:
            robotName = robot['robot_name']
    try:
        robotName = robotName
    except UnboundLocalError:
        robotName = 'No robot for given year'

    embed = discord.Embed(title=team, description=f'Here is some info on {team}s {year} robot', color=0x00ff00)
    embed.add_field(name='Robot name', value=robotName, inline=False)
    await ctx.send(embed=embed)
            
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if message.content in blessedTeams:
        blessedTime = blessedTimes(message.content)
        if blessedTime:
            response = "It is a blessed time"
            await message.channel.send(response)
        else:
            possibleImages = getPossibleImages()
            embed = discord.Embed(title="It is not a blessed time...", description='try looking at this instead :)', color=0x00ff00)
            embed.set_image(url=random.choice(possibleImages[message.content]))
            await message.channel.send(embed=embed)
    elif message.content in teams:
        possibleImages = getPossibleImages()
        embed = discord.Embed(title=f"Here is an image of {message.content}s robot", description='', color=0x00ff00)
        embed.set_image(url=random.choice(possibleImages[message.content]))
        await message.channel.send(embed=embed)
    else:
        pass
        try:
            int(message.content)
        except ValueError:
            pass
        rInfo = []
        try:
            response = requests.get(f'https://www.thebluealliance.com/api/v3/team/frc{message.content}/robots', headers={"X-TBA-Auth-Key": authKey}).json()
        except IndexError:
            pass
        embed = discord.Embed(title=message.content, description=f'Here are some of {message.content}s robots')
        for robot in response:
            embed.add_field(name=f"{robot['year']}", value=robot['robot_name'])
        await message.channel.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='!help'))

def blessedTimes(team):
    now = datetime.datetime.now()
    allTimes = getTimes(team, now)
    if now >= allTimes[3][0] and now <= allTimes[3][1]:
        if team == "254":
            if now >= allTimes[0][0] and now <= allTimes[0][1]:
                return True
            else:
                return False
        elif team == "118":
            if now >= allTimes[1][0] and now <= allTimes[1][1]:
                return True
            else:
                return False
    else:
        if team == "254":
            if now >= allTimes[0][2] and now <= allTimes[0][3]:
                return True
            else:
                return False
        elif team == "118":
            if now >= allTimes[1][2] and now <= allTimes[1][3]:
                return True
            else:
                return False
        elif team == "1323":
            if now >= allTimes[2][0] and now <= allTimes[2][1]:
                return True
            else:
                return False

def getPossibleImages():
    possibleImage = {"33": [r"https://i.imgur.com/gJWn777.png",
                            r"https://i.imgur.com/EYMvdZw.jpg",
                            r"https://i.imgur.com/6AblHkw.jpg",
                            r"https://i.imgur.com/W4oiZlI.jpg"],
                     "118": [r"https://i.imgur.com/gqXk6rD.png",
                             r"https://bit.ly/37lOMNz",
                             r"https://i.imgur.com/AddLTKz.png",
                             r"https://i.imgur.com/YbhxiEP.jpg",
                             r"https://i.imgur.com/zHwoYva.jpg"],
                     "148": [r"https://i.imgur.com/1FqA6wa.jpg",
                             r"https://i.imgur.com/Qzz3Lwy.jpg",
                             r"https://i.imgur.com/L7QP37C.jpg",
                             r"https://i.imgur.com/sRvsRJI.png"], 
                     "254": [r"https://media.team254.com/2019/03/8de207a3-backlash.jpg", 
                             r"https://media.team254.com/2018/03/968207de-lockdown.jpg", 
                             r"https://media.team254.com/2017/03/902d07bd-misfire.jpg", 
                             r"https://media.team254.com/2016/03/86bb0776-2016.jpg", 
                             r"https://media.team254.com/2015/03/8cf8078d-Deadlift_medium.jpg", 
                             r"https://media.team254.com/2014/02/951707c4-2014-02-18.jpg", 
                             r"https://media.team254.com/2018/02/957e07d5-slipstream.jpg", 
                             r"https://media.team254.com/2012/08/shockwave-300x317.jpg"], 
                     "330": [r"https://i.imgur.com/KBiWCiE.jpg",
                             r"https://bit.ly/362jJG4",
                             r"https://i.imgur.com/r84x0vR.jpg",
                             r"https://i.imgur.com/QTVEqKX.jpg"],
                     "341": [r"https://i.imgur.com/IzTVKe1.jpg",
                             r"https://i.imgur.com/XhzLBGX.jpg",
                             r"https://i.imgur.com/O0I24yH.png",
                             r"https://imgur.com/qheiCYS"], 
                     "930": [r"https://i.imgur.com/UUpud6A.jpg",
                             r"https://i.imgur.com/sQ2TZbs.jpg",
                             r"https://bit.ly/2QtYwOT",
                             r"https://bit.ly/353NO6I"], 
                     "971": [r"https://i.imgur.com/ebEFB5L.png",
                             r"https://i.imgur.com/pa58RJb.jpg",
                             r"https://i.imgur.com/0RRoDQO.jpg",
                             r"https://i.imgur.com/zYtPwly.jpg"], 
                     "973": [r"https://i.imgur.com/IiNmPeH.jpg",
                             r"https://bit.ly/37hfgQc",
                             r"https://i.imgur.com/uqfNzcH.jpg",
                             r"https://i.imgur.com/TbisUE4.png"], 
                     "1114": [r"https://bit.ly/2SwSEHd",
                              r"https://i.imgur.com/tLyD2Vb.jpg",
                              r"https://i.imgur.com/NlxzeLR.jpg",
                              r"https://i.imgur.com/gt04pxA.jpg"],
                     "1155": [r"https://i.imgur.com/1L5lO8K.jpg",
                              r"https://bit.ly/2Zvx6fD",
                              r"https://bit.ly/39njnMb"],
                     "1323": [r"http://team1323.com/wp-content/uploads/2017/11/2017-MTTD-14-1024x683.jpg", 
                              r"http://team1323.com/wp-content/uploads/2017/07/2016-MTTD-14.jpg", 
                              r"http://team1323.com/wp-content/uploads/2019/05/DSC01749.jpg", 
                              r"http://team1323.com/wp-content/uploads/2018/04/2018-Sacramento-Regional-19-1.jpg"],
                     "1678": [r"https://i.imgur.com/iMmZMbz.jpg",
                              r"https://i.imgur.com/8izGPVG.jpg",
                              r"https://i.imgur.com/WhgoS5h.jpg",
                              r"https://i.imgur.com/JICzLpe.jpg"], 
                     "1986": [r"https://i.imgur.com/QbLGwTv.jpg",
                              r"https://bit.ly/2t7Vzvq",
                              r"https://bit.ly/2tZmjyz"], 
                     "2056": [r"https://i.imgur.com/eOiAIcs.jpg",
                              r"https://i.imgur.com/CAK1fqh.png",
                              r"https://i.imgur.com/mgEREZG.jpg",
                              r"https://i.imgur.com/fG2qq3Q.jpg"], 
                     "2767": [r"https://i.imgur.com/XRiCH8g.jpg",
                              r"https://i.imgur.com/XlLNmtH.jpg",
                              r"https://i.imgur.com/IU50hKq.jpg",
                              r"https://i.imgur.com/IkahYwq.jpg"], 
                     "2910": [r"https://i.imgur.com/89Ow3mW.jpg",
                              r"https://i.imgur.com/718N1IQ.png",
                              r"https://i.imgur.com/AmVSjKw.jpg",
                              r"https://i.imgur.com/TpxaWoc.jpg"],
                     "5160": [r"https://i.imgur.com/BHm397o.jpg",
                              r"https://i.imgur.com/e6vUfO0.png",
                              r"https://i.imgur.com/3qSq8Eg.jpg",
                              r"https://i.imgur.com/w51wJPy.jpg"]}

    return possibleImage

def getTimes(team, now):
    twoFiftyFourEndAM = now.replace(hour=2, minute=54, second=59, microsecond=999999)
    twoFiftyFourStartAM = now.replace(hour=2, minute=54, second=0, microsecond=0)
    twoFiftyFourEndPM = now.replace(hour=14, minute=54, second=59, microsecond=999999)
    twoFiftyFourStartPM = now.replace(hour=14, minute=54, second=0, microsecond=0)
    
    oneEighteenEndAM = now.replace(hour=1, minute=18, second=59, microsecond=999999)
    oneEighteenStartAM = now.replace(hour=1, minute=18, second=0, microsecond=0)
    oneEighteenEndPM = now.replace(hour=13, minute=18, second=59, microsecond=999999)
    oneEighteenStartPM = now.replace(hour=13, minute=18, second=0, microsecond=0)
    
    thirteenTwentyThreeEndPM = now.replace(hour=13, minute=23, second=59, microsecond=999999)
    thirteenTwentyThreeStartPM = now.replace(hour=13, minute=23, second=0, microsecond=0)

    zeroToTwelve = now.replace(hour=0, minute=0, second=0, microsecond=0)
    twelveToZero = now.replace(hour=12, minute=0, second=0, microsecond=0)
    
    allTimes = [[twoFiftyFourStartAM, twoFiftyFourEndAM, twoFiftyFourStartPM, twoFiftyFourEndPM], 
                [oneEighteenStartAM, oneEighteenEndAM, oneEighteenStartPM, oneEighteenEndPM],
                [thirteenTwentyThreeStartPM, thirteenTwentyThreeEndPM],
                [zeroToTwelve, twelveToZero]]

    return allTimes

def getTimeUntilEvent(event):
    valid = True
    if event.lower() == "guilford":
        date2 = datetime.datetime(2020, 3, 20)
    elif event.lower() == "wake":
        date2 = datetime.datetime(2020, 2, 28)
    elif event.lower() == "pembroke":
        date2 = datetime.datetime(2020, 3, 6)
    elif event.lower() == "ecu":
        date2 = datetime.datetime(2020, 3, 13)
    elif event.lower() == "asheville":
        date2 = datetime.datetime(2020, 3, 27)
    else: 
        date2 = datetime.datetime.now()
        valid = False
    
    date1 = datetime.datetime.now()
    
    timeDelta = date2 - date1
    seconds = timeDelta.days * 24 * 3600 + timeDelta.seconds
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds, valid

def notifyTeam():
    notes = {}
    with open('notes.txt') as json_file:
        notes = json.load(json_file)
        for k, v in notes.items():
            v = "\n\t - ".join(v)
            response = "Today's notes:\n"
            response += f"<@{k}>\n\t - {v}"

    return response

bot.run(TOKEN)