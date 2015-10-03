# -zealous-octo-waffle
[Python 2.7]

"zealous-octo-waffle" is a script written for the purpose of automating the process of updating the sidebar at /r/avfc. 

Version Plan:

   v1.0:
       Initial implementation of Update Bot

   v2.0:
       Implementation of BBC as primary source (replacing ESPN)

       Rewrite of Goal/Assist Tables
           Creation of Goals Scored [All Competitions] and Goals Assisted [All Competitions]
           Increase number of entries per table to 7
           Changed from: Goals/Assists - Premier League, Goals/Assists - Capital One Cup

       Modification of fixtures table
           Include 4 previous fixtures, new 4 fixtures

       Code cleanup from v1.0

       Implementation of new "Standby" Mode (Name to be changed)
           Every hour (?) the bot will check for an update message. Will also check time and update daily at a set time. (15:00 ASST or something, I dunno)

       Formatting of AV in league table.

   v3.0: Support for FA Cup and other competitons.
       [Timed Update]: Will occur after FA Cup begins.

   [Potential Update]
       Current Injuries?
       Expansion to other subreddit features - Match threads etc
       Investigate Python 3 [Potential Rewrite]
