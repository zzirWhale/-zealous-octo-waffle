# -*- coding: cp1252 -*-
#---
#   /r/avfc Sidebar Update Bot, v2.0 by /u/zzirWhale\
#       Project Name:  zealous-octo-waffle
#
#   Version Plan:
#
#   v1.0:
#       Initial implementation of Update Bot
#
#   v2.0:
#       Implementation of BBC as primary source (replacing ESPN)
#
#       Rewrite of Goal/Assist Tables
#           Creation of Goals Scored [All Competitions] and Goals Assisted [All Competitions]
#           Increase number of entries per table to 7
#           Changed from: Goals/Assists - Premier League, Goals/Assists - Capital One Cup
#
#       Modification of fixtures table
#           Include 4 previous fixtures, new 4 fixtures
#
#       Code cleanup from v1.0
#
#       Implementation of new "Standby" Mode (Name to be changed)
#           Every hour (?) the bot will check for an update message. Will also check time and update daily at a set time. (15:00 ASST or something, I dunno)
#
#       Formatting of AV in league table.
#   
#       Added try except statements for FPL and Sidebar update.
#
#       Raged alot.
#
#   v3.0: Support for FA Cup and other competitons.
#       [Timed Update]: Will occur after FA Cup begins.
#
#   [Potential Update]
#       Current Injuries?
#       Expansion to other subreddit features - Match threads etc
#       Investigate Python 3 [Potential Rewrite]
#---

#--- Imports
import json
import urllib
import httplib
import datetime
import arrow
import pytz
import os
import subprocess
import praw
import tkMessageBox
import time
import webbrowser
import cPickle as pickle

from Tkinter import Tk

#--- External File Imports
from oAuth import *

#-------------------------------------------------------------------------------------------------------------- Start of Variables

#--- Globals
global Sidebar
global JSON_leagueTable
global VillaLeaguePosition
global SBar_LeagueTable
global Subject
global Message
global redditUser
global sub
global client_id
global client_secret
global redirect_uri
global refresh_token
global data
global PLdata

global SBar_Links
global Sbar_Upcoming
global Sbar_TopScore
global Sbar_TopAssist
global Sbar_FPL
global Sbar_COC_TopScore
global Sbar_COC_Discipline

#--- Variables
sub = ""
Sidebar = ""
Subject = ""
Message = ""

JSON_leagueTable = "/alpha/soccerseasons/398/leagueTable"
VillaLeaguePosition = 0
SBar_LeagueTable = ""

PRAWFlags = "flair identity modconfig modposts modwiki privatemessages read save submit vote wikiedit wikiread"

ProgramHeader = """#---
#   /r/avfc Sidebar Update Bot, v2.0
#
#   For questions, concerns and other: Contact (Reddit): /u/zzirWhale
#       Project Name:  zealous-octo-waffle
#---
"""

VersionHistory = """#---
#   /r/avfc Sidebar Update Bot, v2.0 by /u/zzirWhale
#
#   Version Plan:
#
#   v1.0:
#       Initial implementation of Update Bot
#
#   v2.0:
#       Implementation of BBC as primary source (replacing ESPN)
#
#       Rewrite of Goal/Assist Tables
#           Creation of Goals Scored [All Competitions] and Goals Assisted [All Competitions]
#           Increase number of entries per table to 7
#
#       Modification of fixtures table
#           Include 4 previous fixtures, blank line, 4 future fixtures
#
#       Code cleanup from v1.0
#
#       Implementation of new "All Rounder" Mode (Name to be changed)
#           Every hour (?) the bot will check for an update message. Will also check time and update daily at a set time. (15:00 ASST or something, I dunno)
#
#   v3.0: Support for FA Cup and other competitons.
#       [Timed Update]: Will occur after FA Cup begins.
#
#   [Potential Update]
#       Current Injuries?
#       Expansion to other subreddit features - Match threads etc
#       Investigate Python 3 [Potential Rewrite]
#---
"""

HelpScreenText = """Welcome. This is the /r/avfc Sidebar Update Bot's Help Menu. Here are some explanations to some of my features:

1. "Manually Update Sidebar"
Upon selecting this option, I will give you a code, which will be something like "Update518". I will ask you to inbox /u/AVFCSidebarBot on Reddit with that code in the subject line. In the body of that message, you can put the code for the updated sidebar. When I receive your message your message I will update the sidebar using the code that you specified in the body.

2. "Start Automatically Updating Sidebar"
This option will put me in a mode where I continously wait for a message from my bot friend, /u/AutoModerator (who should send me a message every Tuesday and Thursday). When I receieve this message I will automatically recollect data from my sources and update the sidebar.

3. "Force generate new sidebar."
"Force generate new sidebar" is an option that the mods can use to force me into updating the sidebar immediately. Mainly for use if /u/AutoModerator forgets to tell me to update myself :(

6. "Version History."
The "Version History" menu option shows the history of this script organised by versions.

7. "Force generate new FPL List."
In order for the goal scorer (Premier League) and Fantasy Premier League table to work this script makes use of data from the official Fantasy Premier League site. "Force generate new FPL list" is a command that will delete the previous Fantasy Premier League lists (Container Player ID's and Player Name's for players who play for Aston Villa), download and recompile the data into new files. This should only be used if you explicitly know what you're doing." 

8. Message script creator.
This section allows the user of this script to message my creator, incase something breaks (let's hope not!). On this screen you will be prompted to press 1 and then enter the subject of your message. Then you select 2, you can enter the body of your message. Once you confirm that you wish to send the message using option 3, you will be given a link to a Reddit Captcha image (I couldn't help this :(). You will need to open this link, and type in the characters you see into this program. If you're correct the message will send and you will be directed back to the home screen, otherwise you will be given another link, until such time as you provide the correct response.
"""

#--- Sidebar Content
SBar_Links = """
######Prepared

* r/avfc Community [Guidelines](http://www.reddit.com/r/avfc/wiki/rules)
* How To Make A [Match Thread](http://www.reddit.com/r/avfc/wiki/matchthread)
* What Do The Flairs [Represent](https://www.reddit.com/r/avfc/wiki/flairs)
* The History Of [AVFC](http://www.reddit.com/r/avfc/wiki/history)
* The Subreddits Of Premier League [Clubs](http://www.reddit.com/r/avfc/wiki/prem_clubs)
* Official AVFC club [links](http://www.reddit.com/r/avfc/wiki/Media)
* Please report any subreddit issues [here](https://www.reddit.com/message/compose?to=%2Fr%2Favfc)
"""

Sbar_Upcoming = """#Fixtures
Date | Opponent | Kick-Off
:---:|:---:|:----:|:----:|
"""

Sbar_BPL_SA = """\n#Player Goals/Assists
Assist = 1 Point | Goal = 3 Points

Player | Goals | Assists | Score
:---:|:---:|:---:|:---:
"""

Sbar_Discipline = """\n#Player Discipline
Yellow = 1 Point   |   Red = 3 Points

Name | Yellow | Red | Score
:---:|:---:|:---:|:---:
"""

Sbar_FPL = """\n#Fantasy Premier League Table (Top 5)
Pos|Team|GW Pts|Total Pts
:---:|:---:|:---:|:---:|:---:
"""

Sbar_COC_Score = """\n#Capital One Cup Goals/Assists
Assist = 1 Point   |   Goal = 3 Points

Rank|Name|Goals|Assists|Score
:---:|:---:|:---:|:---:|:---:
"""

Sbar_COC_Discipline = """\n#Capital One Cup Discipline
Yellow = 1 Point   |   Red = 3 Points

Rank|Name|Yellow|Red|Score
:---:|:---:|:---:|:---:|:---:
"""
#-------------------------------------------------------------------------------------------------------------- End of Variables

#-------------------------------------------------------------------------------------------------------------- Start of Functions
             
def Get_footballdata_API(APIAddress):
    global data

    #--- football-data.org API Authentication
    connection = httplib.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '1c77aa9e14ed42f78b17e954a3b67b2f' }
    connection.request('GET', APIAddress, None, headers )
    response = json.loads(connection.getresponse().read().decode())
    data = response

def GetFantasyPL_API(IDNumber):
    global PLdata
    
    jsonURL = "http://fantasy.premierleague.com/web/api/elements/" + IDNumber + "/"
    response = urllib.urlopen(jsonURL)
    PLdata = json.loads(response.read())
    
def returnMonth(input):
    if input == "01":
        return "Jan"
    if input == "02":
        return "Feb"
    if input == "03":
        return "Mar"
    if input == "04":
        return "Apr"
    if input == "05":
        return "May"
    if input == "06":
        return "Jun"
    if input == "07":
        return "Jul"
    if input == "08":
        return "Aug"
    if input == "09":
        return "Sep"
    if input == "10":
        return "Oct"
    if input == "11":
        return "Nov"
    if input == "12":
        return "Dec"

def AddToSidebarOutput(Input):
    global Sidebar
    Sidebar = Sidebar + Input

def ShortTeamName(teamName):
    if teamName == "Manchester City FC":
        return "Manchester City"
    if teamName == "Manchester United FC":
        return "Manchester Utd"
    if teamName == "West Ham United FC":
        return "West Ham"
    if teamName == "Leicester City FC":
        return "Leicester"
    if teamName == "Arsenal FC":
        return "Arsenal"
    if teamName == "Everton FC":
        return "Everton"
    if teamName == "Swansea City FC":
        return "Swansea"
    if teamName == "Crystal Palace FC":
        return "Crystal Palace"
    if teamName == "Tottenham Hotspur FC":
        return "Spurs"
    if teamName == "Watford FC":
        return "Watford"
    if teamName == "Norwich City FC":
        return "Norwich"
    if teamName == "West Bromwich Albion FC":
        return "West Brom"
    if teamName == "Liverpool FC":
        return "Liverpool"
    if teamName == "AFC Bournemouth":
        return "Bournemouth"
    if teamName == "Chelsea FC":
        return "Chelsea"
    if teamName == "Southampton FC":
        return "Southampton"
    if teamName == "Aston Villa FC":
        return "Aston Villa"
    if teamName == "Stoke City FC":
        return "Stoke"
    if teamName == "Newcastle United FC":
        return "Newcastle"
    if teamName == "Sunderland AFC":
        return "Sunderland"
    else:
        return teamName

def ShortCompName(compName):
    if "Premier League" in compName:
        return "PL" 
    if "FA Cup" in compName:
        return "FA"
    if "League Cup" in compName:
        return "LC"
    else:
        return compName

def LoginToReddit():                                                
    global r
    
    r = praw.Reddit(user_agent="/r/AVFC Sidebar Updater v2.0, by /u/zzirWhale")
    r.set_oauth_app_info(client_id, client_secret, redirect_uri)
    r.refresh_access_information(refresh_token)

def HelpScreen():
    ClearScreen()
    print HelpScreenText
    Respond = raw_input("Please press 1 to return to the main menu: ")
    if Respond == "1":
        MainMenu()
    else:
        HelpScreen()

def ShowVersionHistory():
    ClearScreen()
    print VersionHistory
    Respond = raw_input("Please press 1 to return to the main menu: ")
    if Respond == "1":
        MainMenu()
    else:
        ShowVersionHistory()

def MainMenu():
    ClearScreen()
    print ProgramHeader

    print "Current Connected to: /r/" + str(sub)
    print "\nMain Menu:\n"
    print "1. Manually Update Sidebar. [Future Update Feature --- Do not use ===]"
    print "2. Start Automatically Updating Sidebar."
    print "3. Force generate new sidebar."
    for i in range(4,6):
        print str(i) + ". --- No Current Use Yet.---"
    print "6. Version History."
    print "7. Force generate new FPL list."
    print "8. Message script creator."
    print "9. Help."
    
    MenuSelection = raw_input("Please select option from menu\n")
    if MenuSelection == "1":
        MainMenu()
    elif MenuSelection == "2":
        WaitForUpdate()
    elif MenuSelection == "3":
        UpdateSidebar(True)
    elif MenuSelection == "6":
        ShowVersionHistory()
    elif MenuSelection == "7":
        Gen_New_FPL_List(True)
    elif MenuSelection == "8":
        MessageMenu(Subject, Message)
    elif MenuSelection == "9":
        HelpScreen()
    else:
        print "Error. Invalid selection."
        MainMenu()

def WaitForUpdate():
    print "To stop the bot waiting for an update command, you will have to close the entire program."
    while True:
        for msg in r.get_unread(limit=None):
            if msg.subject == "Update" or msg.subject == "update":
                print "Update command received. Updating sidebar now."
                msg.mark_as_read()
                UpdateSidebar(True)
            else:
                pass
        print "No update command received. Sleeping for 2 hours, and then re-checking."
        time.sleep(7200)
        
def MessageMenu(Subject, Message):
    ClearScreen()
    
    print "Send a message to the bot creator. Please select an option below to complete the relevant field."
    if Subject == "":
        print "1. Enter Subject."
    else:
        print "Subject: " + str(Subject)
    if Message == "":
        print "2. Enter Message."
    else:
        print "Message: " + str(Message)
    print ""
    print "3. Send message to creator."
    print "4. Cancel."
    global Response
    Response = raw_input("Response: ")
    MessageBotCreator(Response, Subject, Message)

def MessageBotCreator(Response, Subject, Message):
    if Response == "1":
        Subject = raw_input("Please enter the subject of your message:\n")
        MessageMenu(Subject, Message)
    elif Response == "2":
        Message = raw_input("Please enter the message content that you wish to send.\n")
        MessageMenu(Subject, Message)
    elif Response == "4":
        MainMenu()
    elif Response == "3":
        Confirmation = raw_input("Are you sure you would like to send the message? Y/N\n")
        if Confirmation == "Y":
            print "You will soon be presented with a link to a Reddit Captcha. Please open this link and input the characters you see into this program. Then press Enter."
            Subject = "BotMsg: " + Subject
            r.send_message("zzirWhale", Subject, Message)
            print "Message sent."
            time.sleep(3)
            MainMenu()
        elif Confirmation == "N":
            MainMenu()
        else:
            print "Invalid response received."
            MessageMenu(Subject, Message)
    else:
        print "Invalid response received."
        MessageMenu(Subject, Message)

def ClearScreen():
    subprocess.call("cls", shell=True)

def Gen_New_FPL_List(Menu):
    print "\nFantasy Premier League data missing. Regenerating required files.\n"
    
    #Get rid of previous, regenerate lists from scratch.
    try:
        os.remove("PlayerID.p")
    except:
        print "Couldn't find PlayerID.p. That's ok, I'll just make a new one."
    try:
        os.remove("PlayerName.p")
    except:
        print "Couldn't find PlayerName.p. That's ok, I'll just make a new one."

    global FPLdata1
    global Name
    
    NewPlayerID = []
    NewPlayerName = []
    Name = ""
    
    try:
        for p in range(1,700):
            
                
            jsonURL = "http://fantasy.premierleague.com/web/api/elements/" + str(p) + "/"
            response = urllib.urlopen(jsonURL)
            FPLdata1 = json.loads(response.read())

            Name = FPLdata1['first_name'] + " " + FPLdata1['second_name']
            
            if FPLdata1['team_name'] == "Aston Villa":
                print "Adding Data for Player: " + Name + " with ID: " + str(FPLdata1['id'])
                NewPlayerID.append(FPLdata1['id'])
                NewPlayerName.append(Name)
            else:
                print "Player: " + Name + " is not an Aston Villa Player."
    except:
        print "Couldn't find player with ID: " + str(p)

    pickle.dump(NewPlayerID, open("PlayerID.p", "wb"))
    pickle.dump(NewPlayerName, open("PlayerName.p", "wb"))
    if Menu == True:
        MainMenu()
    else:
        UpdateSidebar(False)

def returnShortName(Name):
    if Name == "Bradley Guzan" or Name == "Brad Guzan":
        return "Guzan"
    elif Name == "Leandro Bacuna":
        return "Bacuna"
    elif Name == "Kieran Richardson":
        return "Richardson"
    elif Name == "Ron Vlaar":
        return "Vlaar"
    elif Name == "Philippe Senderos":
        return "Senderos"
    elif Name == "Aly Cissokho":
        return "Cissokho"
    elif Name == "Alan Hutton":
        return "Hutton"
    elif Name == "Ciaran Clark":
        return "Clark"
    elif Name == "Jores Okore":
        return "Okore"
    elif Name == "Nathan Baker":
        return "Baker"
    elif Name == "Lewis Kinsella":
        return "Kinsella"
    elif Name == "Micah Richards":
        return "Richards"
    elif Name == "Carles Gil de Pareja Vicent":
        return "Carles Gil"
    elif Name == "Charles N'Zogbia":
        return "N'Zogbia"
    elif Name == "Joe Cole":
        return "Cole"
    elif Name == "Jack Grealish":
        return "Grealish"
    elif Name == "Scott Sinclair":
        return "Sinclair"
    elif Name == "Ashley Westwood":
        return "Westwood"
    elif Name == "Carlos Sánchez" or Name == "Carlos Sanchez":
        return "Sánchez"
    elif Name == "Gabriel Agbonlahor":
        return "Agbonlahor"
    elif Name == "Libor Kozak" or Name == "Libor Kozák":
        return "Kozák"
    elif Name == "Rushian Hepburn-Murphy":
        return "Hepburn-Murphy"
    elif Name == "Tiago Ilori":
        return "Ilori"
    elif Name == "Joleon Lescott":
        return "Lescott"
    elif Name == "Mark Bunn":
        return "Bunn"
    elif Name == "Idrissa Gueye":
        return "Gueye"
    elif Name == "Jordan Amavi":
        return "Amavi"
    elif Name == "José Ángel Crespo" or Name == "José Crespo":
        return "Crespo"
    elif Name == "Jordan Ayew":
        return "Ayew"
    elif Name == "Jordan Veretout":
        return "Veretout"
    elif Name == "Rudy Gestede":
        return "Gestede"
    elif Name == "Adama Traoré" or Name == "Adama Traore":
        return "Traoré"
    elif Name == "Gary Gardner":
        return "Gardner"
    else:
        return Name

def UpdateSidebar(ReturnToAutoUpdate):

    #---
    #   Why do I redeclare these variables?
    #   Haven't a clue, they just seem to work,
    #   so I leave them be.
    #---

    global Sbar_Upcoming
    global Sbar_TopScore
    global Sbar_TopAssist
    global Sbar_Discipline
    global Sbar_BPL_SA
    global Sbar_FPL
    global Sbar_COC_TopScore
    global Sbar_COC_Discipline
    global Sbar_COC_Score

    ClearScreen()
    print "Updating sidebar. Please wait while the program updates. The program may seem like it's doing nothing, but this is not the case."

    #---    Premier League Scorers and Assisters
    try:
            PlayerID = pickle.load(open("PlayerID.p", "rb"))
    except:
            Gen_New_FPL_List()
            
    try:
            PlayerName = pickle.load(open("PlayerName.p", "rb"))
    except:
            Gen_New_FPL_List()

    Player_Goals = []
    Player_Assists = []
    Player_Score = []

    Player_Yellow = []
    Player_Red = []
    Player_Discipline_Score = []

    count = 0

    for x in PlayerID:
            jsonURL = "http://fantasy.premierleague.com/web/api/elements/" + str(x) + "/"
            response = urllib.urlopen(jsonURL)
            try:
                FPLdata = json.loads(response.read())
            except ValueError:
                print "I'm sorry. There seems to be an issue with the Fantasy Premier League. I suggest checking http://fantasy.premierleague.com for deatils."
                time.sleep(3.5)
                MainMenu()
            except:
                print "I'm really sorry. I'm not quite sure what happened, but whatever it was, it didn't work. :("
                time.sleep(3.5)
                MainMenu()
            print "[PL] Getting information for player: " + FPLdata['first_name'] + " " + FPLdata['second_name'] + " (" + str(count + 1) + "/" + str(len(PlayerID)) + ")"

            Player_Yellow.append(FPLdata['yellow_cards'])
            Player_Red.append(FPLdata['red_cards'])

            Player_Goals.append(FPLdata['goals_scored'])
            Player_Assists.append(FPLdata['assists'])

            count = count + 1

    #---    Capital One Cup Scorers
    COC_Score_URL = "https://www.kimonolabs.com/api/efc9okwe?apikey=6GvkNHivZxklnk4Llqi1TX0op91T0tdk"
    response_Score = urllib.urlopen(COC_Score_URL)
    COC_Score_Data = json.loads(response_Score.read())

    global CurName
    global Count1
    global totalGoals
    global currentGoals
    global completeGoals

    CurName = ""
    Count1 = 0
    totalGoals = 0
    currentGoals = 0
    completeGoals = 0

    print "\nPremier League Data complete. Beginning Capital One Cup\n"

    for i in range(0,50):
        print "[COC Scorers] Working with data for: " + COC_Score_Data['results']['collection1'][i]['playerName']['text'] + " [" + str(i + 1) + "/50]" 
        if COC_Score_Data['results']['collection1'][i]['clubName']['text'] == "Aston Villa":
            for x in PlayerName:
                if Count1 < 34:
                    CurName = PlayerName[Count1]
                    if COC_Score_Data['results']['collection1'][i]['playerName']['text'] == CurName:
                        totalGoals = str(COC_Score_Data['results']['collection1'][i]['totalGoals'])
                        currentGoals = Player_Goals[Count1]
                        completeGoals = int(currentGoals) + int(totalGoals)
                        Player_Goals[Count1] = str(completeGoals)
                    Count1 = Count1 + 1
            Count1 = 0

    #---    Capital One Cup Assists
    print "\nStarting COC Assists."
    COC_Assist_URL = "https://www.kimonolabs.com/api/7r0ey9ek?apikey=6GvkNHivZxklnk4Llqi1TX0op91T0tdk"
    response_Assist = urllib.urlopen(COC_Assist_URL)
    COC_Assist_Data = json.loads(response_Assist.read())

    global totalAssists
    global currentAssists
    global completeAssists

    CurName = ""
    Count1 = 0
    totalAssists = 0
    currentAssists = 0
    completeAssists = 0

    for i in range(0,50):
        print "[COC Assists] Working with data for: " + COC_Assist_Data['results']['collection1'][i]['playerName']['text'] + " [" + str(i + 1) + "/50]" 
        if COC_Assist_Data['results']['collection1'][i]['clubName']['text'] == "Aston Villa":
            for x in PlayerName:
                if Count1 < 34:
                    CurName = PlayerName[Count1]
                    if COC_Assist_Data['results']['collection1'][i]['playerName']['text'] == CurName:
                        totalAssists = str(COC_Assist_Data['results']['collection1'][i]['totalAssists'])
                        currentAssists = Player_Assists[Count1]
                        completeAssists = int(currentAssists) + int(totalAssists)
                        Player_Assists[Count1] = str(completeAssists)
                    Count1 = Count1 + 1
            Count1 = 0

    #---    Sorting Data and printing

    global GoalScore
    global AssistScore
    global TotalGoalScore
    global RedScore
    global YellowScore
    global TotalDisciplineScore
    global PlayName

    GoalScore = 0
    AssistScore = 0
    TotalGoalScore = 0
    RedScore = 0
    YellowScore = 0
    TotalDisciplineScore = 0

    for b in range(0,33):
        GoalScore = int(Player_Goals[b]) * 3
        AssistScore = int(Player_Assists[b])
        TotalGoalScore = int(GoalScore) + int(AssistScore)
        
        Player_Score.append(TotalGoalScore)

        RedScore = int(Player_Red[b]) * 3
        YellowScore = int(Player_Yellow[b])
        TotalDisciplineScore = int(RedScore) + int(YellowScore)

        Player_Discipline_Score.append(TotalDisciplineScore)

    TopScorers = sorted(zip(Player_Goals, PlayerName), reverse=True)[:7]
    TopAssists = sorted(zip(Player_Assists, PlayerName), reverse=True)[:7]
    TopScore = sorted(zip(Player_Score, PlayerName), reverse=True)[:7]
    TopYellow = sorted(zip(Player_Yellow, PlayerName), reverse=True)[:7]
    TopRed = sorted(zip(Player_Red, PlayerName), reverse=True)[:7]
    TopDiscipline = sorted(zip(Player_Discipline_Score, PlayerName), reverse=True)[:7]


    for d in range(0,7):
        Player = str(TopScore[int(d)][1])
        PlayerGoals = Player_Goals[int(PlayerName.index(Player))]
        PlayerAssists = Player_Assists[int(PlayerName.index(str(Player)))]
        PlayerScore = Player_Score[int(PlayerName.index(str(Player)))]

        PlayName = returnShortName(Player)
                    
        Sbar_BPL_SA = Sbar_BPL_SA + PlayName + "|" + str(PlayerGoals) + "|" + str(PlayerAssists) + "|" + str(PlayerScore) + "\n"

    for i in range(0,7):
        Player = str(TopDiscipline[int(i)][1])        
        PlayerYellow = Player_Yellow[int(PlayerName.index(str(Player)))]
        PlayerRed = Player_Red[int(PlayerName.index(str(Player)))]
        PlayerDisciplineScore = Player_Discipline_Score[int(PlayerName.index(str(Player)))]

        PlayName = returnShortName(Player)
        
        Sbar_Discipline = Sbar_Discipline + PlayName + "|" + str(PlayerYellow) + "|" + str(PlayerRed) + "|" + str(PlayerDisciplineScore) + "\n"

    #--- football-data.org: League Table
    Get_footballdata_API(JSON_leagueTable)
    
    if sub == "avfcnaut":
        SBar_LeagueTable = """
# Premier League Table Matchweek: """ + str(data['matchday']) + """
Pos | Team | Pld | Gd | Pts
:---:|---|:--:|:--:|:--:
"""
    else:
        SBar_LeagueTable = """
# Premier League Table - Matchweek: """ + str(data['matchday']) + """
Pos | Team | Pld | Gd | Pts
:---:|---|:--:|:--:|:--:
"""                                             
    
    for Team in data['standing']:
        if Team['teamName'] == "Aston Villa FC":
            VillaLeaguePosition = Team['position']
            if VillaLeaguePosition == 19 or VillaLeaguePosition == 20:
                for Team in data['standing']:
                    if Team['position'] == 16 or Team['position'] == 17 or Team['position'] == 18 or Team['position'] == 19 or Team['position'] == 20:
                        if Team['teamName'] == "Aston Villa FC":
                            SBar_LeagueTable = SBar_LeagueTable + "**" + str(Team['position']) + "**|" + "**" + ShortTeamName(Team['teamName']) + "**|" + "**" + str(Team['playedGames']) + "**|" + "**" + str(Team['goalDifference']) + "**|" + "**" + str(Team['points']) + "\n"
                        else:
                            SBar_LeagueTable = SBar_LeagueTable + str(Team['position']) + "|" + ShortTeamName(Team['teamName']) + "|" + str(Team['playedGames']) + "|" + str(Team['goalDifference']) + "|" + str(Team['points']) + "\n"
            else:
               for Team in data['standing']:
                    if Team['position'] == VillaLeaguePosition - 2 or Team['position'] == VillaLeaguePosition - 1 or Team['position'] == VillaLeaguePosition or Team['position'] == VillaLeaguePosition + 1 or Team['position'] == VillaLeaguePosition + 2:
                        if Team['teamName'] == "Aston Villa FC":
                            SBar_LeagueTable = SBar_LeagueTable + "**" + str(Team['position']) + "**|" + "**" + ShortTeamName(Team['teamName']) + "**|" + "**" + str(Team['playedGames']) + "**|" + "**" + str(Team['goalDifference']) + "**|" + "**" + str(Team['points']) + "\n"
                        else:
                            SBar_LeagueTable = SBar_LeagueTable + str(Team['position']) + "|" + ShortTeamName(Team['teamName']) + "|" + str(Team['playedGames']) + "|" + str(Team['goalDifference']) + "|" + str(Team['points']) + "\n"

    today = datetime.date.today()

    SBar_LeagueTable = SBar_LeagueTable + "Updated: " + str(today.strftime('%d-%b-%Y')) + "\n\n"

    #--- BBC: Fixtures
          
    jsonURL = "https://www.kimonolabs.com/api/3w2rgwhg?apikey=6GvkNHivZxklnk4Llqi1TX0op91T0tdk"
    response = urllib.urlopen(jsonURL)
    BBCdata = json.loads(response.read())

    Sbar_Upcoming = """#Previous Fixtures

Date | Opponent | Result | Comp
:---:|:---:|:----:|:----:|
"""
    
    DateBackwards = [3, 2, 1, 0]

    for i in DateBackwards:
        
        DateOriginal = BBCdata['results']['PreviousMatch'][i]['PM_Date']
        Date = DateOriginal[4:10]

        Opponent = ""
        if BBCdata['results']['PreviousMatch'][i]['PM_HomeTeam']['text'] == "Aston Villa":
            AVHomeTeam = True
            Opponent = ShortTeamName(BBCdata['results']['PreviousMatch'][i]['PM_AwayTeam']['text']) + " (H)"
        else:
            AVHomeTeam = False
            Opponent = ShortTeamName(BBCdata['results']['PreviousMatch'][i]['PM_HomeTeam']['text']) + " (A)"

        if BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'][0] > BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'][4] and AVHomeTeam == True:
            Result = BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'] + " (W)"
        elif BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'][0] == BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'][4]:
            Result = BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'] + " (D)"
        else:
            Result = BBCdata['results']['PreviousMatch'][i]['PM_Score']['text'] + " (L)"

        Comp = str(ShortCompName(BBCdata['results']['PreviousMatch'][i]['PM_Comp']))

        Sbar_Upcoming = Sbar_Upcoming + Date + " | " + Opponent + " | " + Result + " | " + Comp + "\n"

    Sbar_Upcoming = Sbar_Upcoming + """\n#Future Fixtures\n
Date | Opponent | Time | Comp
:---:|:---:|:----:|:----:|
"""

    for i in range(0,5):
    
        DateOriginal = BBCdata['results']['FutureMatch'][i]['FM_Date']
        Date = DateOriginal[4:10]

        Opponent = ""
        if BBCdata['results']['FutureMatch'][i]['FM_HomeTeam']['text'] == "Aston Villa":
            AVHomeTeam = True
            Opponent = ShortTeamName(BBCdata['results']['FutureMatch'][i]['FM_AwayTeam']['text']) + " (H)"
        else:
            AVHomeTeam = False
            Opponent = ShortTeamName(BBCdata['results']['FutureMatch'][i]['FM_HomeTeam']['text']) + " (A)"

        Time = BBCdata['results']['FutureMatch'][i]['FM_Time']

        Comp = str(ShortCompName(BBCdata['results']['FutureMatch'][i]['FM_Comp']))

        if len(Date) == 5:
            Sbar_Upcoming = Sbar_Upcoming + "0" + Date + " | " + Opponent + " | " + Time + " | " + Comp + "\n"
        else:
            Sbar_Upcoming = Sbar_Upcoming + Date + " | " + Opponent + " | " + Time + " | " + Comp + "\n"    
    
    Sbar_Upcoming = Sbar_Upcoming + "\nListed Kick off times are GMT. A time zone converter is available [here](http://www.timezoneconverter.com/cgi-bin/tzc.tzc)\n"
                
    #--- Fantasy Premier League Table
        #API: https://www.kimonolabs.com/apis/5mut7xze

    jsonURL = "https://www.kimonolabs.com/api/5mut7xze?apikey=6GvkNHivZxklnk4Llqi1TX0op91T0tdk"
    response = urllib.urlopen(jsonURL)
    FPLdata = json.loads(response.read())

    #Table Seperator
    tS = "|" 
    for i in range(0,5):
        Sbar_FPL = Sbar_FPL + str(FPLdata['results']['Fantasy Premier League'][i]['teamRank']) + tS + FPLdata['results']['Fantasy Premier League'][i]['teamName']['text'] + tS + str(FPLdata['results']['Fantasy Premier League'][i]['gameweekTotal']) + tS + str(FPLdata['results']['Fantasy Premier League'][i]['totalScore']) + "\n"

    Sbar_FPL + Sbar_FPL + " | | | |"
    
    #--- Getting sidebar ready to print

    AddToSidebarOutput("This sidebar was generated using a bot. Any concerns or queries should be sent [here](https://www.reddit.com/message/compose?to=%2Fu%2FzzirWhale)\n\n")
    AddToSidebarOutput(SBar_Links)
    AddToSidebarOutput(SBar_LeagueTable)
    AddToSidebarOutput(Sbar_Upcoming)
    AddToSidebarOutput(Sbar_BPL_SA)
    AddToSidebarOutput(Sbar_Discipline)
    AddToSidebarOutput(Sbar_FPL)
    AddToSidebarOutput("\n#")

    print "---------- Printing New Sidebar ----------"
    print "\n"
    print(Sidebar)
    print "\n"
    print "---------- New Sidebar Printed ----------"
    time.sleep(5)
    EditSidebar(ReturnToAutoUpdate)

def EditSidebar(ReturnToAutoUpdate):
    settings = r.get_settings(sub)
    try:
        r.update_settings(r.get_subreddit(sub), description = Sidebar, raise_captcha_exception=True)
        print "Sidebar should be updated."
    except praw.errors.APIException:
        print "PRAW API Exception occured. I bet it's those damn captchas again."
        
        time.sleep(3)
        MainMenu()
    except:
        print "I don't know what happened, but it was something bad. :("
        time.sleep(3)
        MainMenu()
    if ReturnToAutoUpdate == True:
        WaitForUpdate()
    else:
        MainMenu()
    
def ManualSidebarEdit():
    ClearScreen()
    EditSidebar()
    MainMenu()

def SubSelect():
    global sub
    
    print "Please enter which subreddit you are working with."
    print "Remember: The account /u/AVFCSidebarBot must have moderator privileges."
    SubSelection = raw_input("Enter Subreddit name here: /r/")
    sub = SubSelection
    print "Starting Program and Logging into Reddit. One moment please."
    LoginToReddit()
#-------------------------------------------------------------------------------------------------------------- End of Functions

#-------------------------------------------------------------------------------------------------------------- Start of Runcode

SubSelect()
MainMenu()

#-------------------------------------------------------------------------------------------------------------- End of Runcode
