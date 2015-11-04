import os
import sys
import csv
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import urllib2
import cookielib
import mechanize
import datetime
import re
from bs4 import BeautifulSoup

MODE_SCHEDULE = 10
MODE_LIVE_STREAMS_HD = 20
MODE_LIVE_STREAMS_SD = 25
MODE_LIVE_STREAMS_HD_LEGACY = 26
MODE_LIVE_STREAMS_SD_LEGACY = 27
MODE_PLAY   = 30 
MODE_UPCOMING = 40
PARAMETER_KEY_MODE = "mode"
SCHEDULE = "Streams today"
UPCOMING = "Upcoming Streams for the next days"
VERSION = xbmc.getInfoLabel("System.BuildVersion").replace(" Git:",".") + "-" + xbmc.getInfoLabel("ListItem.Property(Addon.Version)")
schedule_path  = os.path.join(xbmc.translatePath('special://profile/addon_data'), 'plugin.video.hd-streaming-dollisdev/schedule.txt')
channels_path  = os.path.join(xbmc.translatePath('special://profile/addon_data'), 'plugin.video.hd-streaming-dollisdev/channels.txt')
upcoming_path  = os.path.join(xbmc.translatePath('special://profile/addon_data'), 'plugin.video.hd-streaming-dollisdev/upcoming.txt')
debug_path  = os.path.join(xbmc.translatePath('special://profile/addon_data'), 'plugin.video.hd-streaming-dollisdev/debug.txt')
icon_path = os.path.join(xbmc.translatePath('special://profile/addon_data'), 'plugin.video.hd-streaming-dollisdev/')
settings = xbmcaddon.Addon("plugin.video.hd-streaming-dollisdev");
my_addon = xbmcaddon.Addon('plugin.video.hd-streaming-dollisdev')
addon_path = my_addon.getAddonInfo('path') + '/'
picon_path = 'https://github.com/dollis-dev/kodi-repo-resources/raw/master/'
handle = int(sys.argv[1])
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

def parameters_string_to_dict(parameters):    
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

def login():
    channels_list=[]
    date_list=[]
    teams_list=[]
    channels_bar_list=[]
    schedule = []
    username = settings.getSetting("username")
    password = settings.getSetting("password")
    url = 'http://hd-streaming.tv/api/?request=login'
    url2 = 'http://hd-streaming.tv/watch/livehds'
    url3 = 'http://hd-streaming.tv/watch/upcoming-matches'
    req = mechanize.Browser()
    req.addheaders = [('User-agent','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0')]
    req.addheaders = [('Referer','http://news-source.tv/')]
    req.set_handle_robots(False)
    req.set_handle_redirect(True)
    values = {'platform':'XBMC','version':VERSION,'username':username,'password':password}
    logindata = urllib.urlencode(values)
    loginreq = urllib2.Request(url, logindata)
    loginresponse = urllib2.urlopen(loginreq)
    global auth_response
    auth_response = loginresponse.read()
    if "ERROR" in auth_response:
        return False
    response2 = req.open(url2)
    soup = BeautifulSoup(response2.read(), 'html.parser')
    channels_bar = soup.findAll('a', {"class" : "ch-link"})
    if len(channels_bar) > 0:
        for channel_name in channels_bar:
            channels_bar_list.append(channel_name.string)
        file = open(channels_path,'wb+')
        for i in channels_bar_list:
            file.write(i+"\n")
        file.close()
        file = open(schedule_path,'wb+')
        table_list = soup.findAll('table',{"class" : "views-table"})
        for table in table_list:
            try:
                file.write(table.find('caption').string+"|\n")
            except Exception:
                file.write("|\n")
            channels_list = []
            date_list=[]
            teams_list=[]
            channels = table.findAll('td', {"class" : "views-field-field-eum-channel"})
            date_time = table.findAll('td', {"class" : "views-field-field-eum-datetime-1"})
            teams = table.findAll('td', {"class" : "views-field-field-eum-title"})
            for i in channels:
                channels_list.append(i.find('a').string)
            for i in date_time:
                date_list.append(i.find('span').string)
            for i in teams:
                teams_list.append(i.string.strip())
            for i in range(0,len(channels_list)):
                file.write("   "+channels_list[i].encode('utf-8') + "|" + date_list[i].encode('utf-8') + " " + teams_list[i].encode('utf-8')+"\n")
        file.close()
        upcoming_file = open(upcoming_path,'wb+')
        response3 = req.open(url3)
        upcoming_soup = BeautifulSoup(response3.read(), 'html.parser')
        days_div = upcoming_soup.findAll('div',{"class" : "view-grouping"})
        for day in days_div:
            days = day.findAll('div',{"class" : "view-grouping-header"})
            for j in days:
                upcoming_days_list=[]
                upcoming_file.write(j.string+"\n")
                upcoming_days_list.append(j.string)
                tables = day.findAll('table',{"class" : "views-table"})
                for table in tables:    
                    upcoming_sport_list = []
                    upcoming_channels_list = [] 
                    upcoming_date_list = []
                    upcoming_teams_list = []
                    upcoming_leagues_list =[]
                    upcoming_schedule = []
                    upcoming_sport  = table.findAll('caption')
                    upcoming_channels = table.findAll('td', {"class" : "views-field-field-eum-channel"})
                    upcoming_date_time = table.findAll('td', {"class" : "views-field-field-eum-datetime-1"})
                    upcoming_teams = table.findAll('td', {"class" : "views-field-field-eum-title"})
                    upcoming_leagues = table.findAll('td', {"class" : "views-field-field-eum-league"})
                    for i in upcoming_sport:
                        upcoming_sport_list.append(i.string)
                    for i in upcoming_channels:
                        upcoming_channels_list.append(i.find('a').string)
                    for i in upcoming_date_time:
                        upcoming_date_list.append(i.find('span',{"class":"date-display-single"}).string)
                    for i in upcoming_teams:
                        upcoming_teams_list.append(i.string.strip())
                    for i in upcoming_leagues:
                        upcoming_leagues_list.append(i.string.strip())
                    for i in range(0,len(upcoming_channels_list)):
                        upcoming_schedule.append(upcoming_channels_list[i]+" "+upcoming_date_list[i]+" "+upcoming_teams_list[i]+" "+upcoming_leagues_list[i])
                    for i in range(0,len(upcoming_sport_list)):
                        upcoming_file.write("    "+upcoming_sport_list[i]+"\n")
                        for j in range(0,len(upcoming_schedule)):
                            upcoming_file.write("       "+upcoming_schedule[j].encode('utf-8')+"\n") 
        upcoming_file.close()
        return True
    else:
        return False

def get_schedule():
    matches = []
    data = csv.reader(open(schedule_path, 'rb'), delimiter="|")
    for row in data:
        matches.append(row[0] + " " +row[1])
    return matches

def get_channels():
    channels=['ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','ch9','ch10','ch11','ch12','ch13','ch14','ch15','ch16','ch17','ch18','ch19','ch20','ch21','ch22','ch23','ch24','ch25','ch26','ch27','ch28','ch29','ch30']
    return channels

def get_upcoming_schedule():
    upcoming_schedule=[]
    f = open(upcoming_path, 'rb+')
    for line in f:
        upcoming_schedule.append(line)
    return upcoming_schedule
    
def getepginfo(picon, epg, name):
    channel = name.rsplit(None, 1)[-1]
    if epg == 'skip':
        li = xbmcgui.ListItem(name, iconImage=picon_path + picon + '.png', thumbnailImage=picon_path + picon + '.png')
        li.setProperty('fanart_image', picon_path + picon + '.png')
        return li
    if 'Sky Sports' in name:
        URL = "http://www.skysports.com/watch/sky-sports-" + channel
        soup = BeautifulSoup(urllib2.urlopen(URL).read(), 'html.parser')
        img = soup.find("img",src=re.compile(r'epgstatic.sky.com'))
        try:
        	title = soup.find("h4")
        except (AttributeError, TypeError):
            title = 'No show info available'
        try:
            description = soup.find("p")
        except (AttributeError, TypeError):
            description = 'No description available'
        try:
            li = xbmcgui.ListItem(name.title() + ' - ' + title.text, iconImage=picon_path + picon + '.png', thumbnailImage=picon_path + picon + '.png')
        except (AttributeError, TypeError):
            li = xbmcgui.ListItem(name.title() + ' - ' + title, iconImage=picon_path + picon + '.png', thumbnailImage=picon_path + picon + '.png')
        try:
            li.setProperty('fanart_image', img["src"])
        except (AttributeError, TypeError):
            li.setProperty('fanart_image', picon_path + picon + '.png')
        try:
            details={'plot'   : description.text.replace('Also in HD', '')}
        except (AttributeError, TypeError):
            details={'plot'   : description}            
        li.setInfo('video', details)
    elif epg is 'locatetv':
        if 'ESPN' in name:
            URL = "http://www.locatetv.com/uk/listings/espn"
        elif 'BT Sport' in name:
            URL = URL = "http://www.locatetv.com/uk/listings/bt-sport-" + channel
        elif name == 'Setanta Ireland':
            URL = "http://www.locatetv.com/uk/listings/setanta-ireland"
        elif name == 'Setanta Sports 1':
            URL = "http://www.locatetv.com/uk/listings/setantasports-1-ireland"
        elif name == 'BoxNation':
                    URL = "http://www.locatetv.com/uk/listings/boxnation-boxnation"
        elif name == 'Racing UK':
            URL = "http://www.locatetv.com/uk/listings/racing-uk"
        else:
            li = xbmcgui.ListItem(name.title(), iconImage=picon_path + picon + '.png', thumbnailImage=picon_path + picon + '.png')
            return li
        soup = BeautifulSoup(urllib2.urlopen(URL).read(), 'html.parser')
        div = soup.find('li', attrs={'class' : 'schedTv'})
        try:
            title = div('a')[1].text 
        except (AttributeError, TypeError):
            title = 'No show info available'
        try:
            description = div.p.text 
        except (AttributeError, TypeError):
            description = 'No description available'
        if 'europe' in name:
            name = 'BT Sport Europe'
        li = xbmcgui.ListItem(name + ' - ' + title, iconImage=picon_path + picon + '.png', thumbnailImage=picon_path + picon + '.png')
        try:
            li.setProperty('fanart_image', div.a.img['alt'].replace("/mid/", "/large/", 1))
        except (AttributeError, TypeError):
            li.setProperty('fanart_image', picon_path + picon + '.png')
        details={'plot'   : description }
        li.setInfo('video', details)
    else:
        li = xbmcgui.ListItem(name, iconImage=picon_path + picon + '.png', thumbnailImage=picon_path + picon + '.png')
    return li
    
def addDirectoryItem(picon, epg, name, isPlayable=False, isFolder=True, parameters={}):
    li = getepginfo(picon, epg, name)
    if isPlayable==False:
        li.setProperty('IsPlayable', 'false')
    elif isPlayable==True:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def addDirectoryItem_Legacy(name, isPlayable=False, isFolder=True, parameters={}):
    li = xbmcgui.ListItem(name)
    if isPlayable==False:
        li.setProperty('IsPlayable', 'false')
    elif isPlayable==True:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    
def addDirectoryItemRoot(name, picon, isPlayable=False, isFolder=True, parameters={}):
    li = xbmcgui.ListItem(name, iconImage=picon, thumbnailImage=picon)
    li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
    if isPlayable==False:
        li.setProperty('IsPlayable', 'false')
    elif isPlayable==True:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def show_root_menu():
    if login():
        addDirectoryItemRoot('Live Streams - HD', picon_path + 'hd.png', parameters={ PARAMETER_KEY_MODE: MODE_LIVE_STREAMS_HD }, isFolder=True)
        addDirectoryItemRoot('Live Streams - SD', picon_path + 'sd.png', parameters={ PARAMETER_KEY_MODE: MODE_LIVE_STREAMS_SD }, isFolder=True)
        addDirectoryItemRoot('Live Streams - HD (Legacy Mode)', picon_path + 'hd.png', parameters={ PARAMETER_KEY_MODE: MODE_LIVE_STREAMS_HD_LEGACY }, isFolder=True)
        addDirectoryItemRoot('Live Streams - SD (Legacy Mode)', picon_path + 'sd.png', parameters={ PARAMETER_KEY_MODE: MODE_LIVE_STREAMS_SD_LEGACY }, isFolder=True)
        addDirectoryItemRoot(UPCOMING, picon_path + 'Upcoming.png', parameters={ PARAMETER_KEY_MODE: MODE_UPCOMING }, isFolder=True)
        favorite_team_game()
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    else:
        if 'password' in auth_response:
            dialog = xbmcgui.Dialog().ok("Login Failed",auth_response)
            settings.openSettings()
        else:
            dialog = xbmcgui.Dialog().ok("Login Failed",auth_response)
    
def show_schedule():
    if len(get_schedule()) == 0:
        addDirectoryItemRoot('No streaming planned for today', isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    else:   
        for i in get_schedule():
            addDirectoryItemRoot(i, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_upcoming_schedule():
    if len(get_upcoming_schedule()) == 0:
        addDirectoryItemRoot('No streaming planned for the next days', isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    else:   
        for i in get_upcoming_schedule():
            addDirectoryItemRoot(i, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def get_rtmp_url(path):
    streamer  = 'rtmp://vdn.hd-streaming.tv:443/live'
    playPath  = path
    appUrl    = 'live' 
    rtmp = ''.join([streamer,' playpath=', playPath,'?s=6hfu0', ' app=', appUrl, ' live=true'])
    return rtmp
    
def favorite_team_game():
    name='No ' + settings.getSetting("fav_team") + ' Games found'
    data = csv.reader(open(schedule_path, 'rb'), delimiter="|")
    for row in data:
        if row[1].find(settings.getSetting("fav_team")) != -1:
            path = 'channel' + row[0][5:]
            name = row[1]
            stream = get_rtmp_url(path)
            addDirectoryItemRoot(name, picon_path + 'icon.png', isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            return
    return
    
def set_path(quality, chan_num):

    if quality == 'sd':
        path = 'channel' + chan_num[2:] + '-sd'
    else:
        path = 'channel' + chan_num[2:]
    return path
        
def show_live_streams(quality, legacy):
    for i in get_channels():
        j = i.rstrip().lower().replace(" ","")
        if j == "ch1":
            path = set_path(quality, j)
            name = 'Sky Sports news'
            epg = 'sky'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch2":
            path = set_path(quality, j)
            epg = 'sky'
            name = 'Sky Sports 1'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch3":
            path = set_path(quality, j)
            epg = 'sky'
            name = 'Sky Sports 2'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch4":
            path = set_path(quality, j)
            epg = 'sky'
            name = 'Sky Sports 3'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch5":
            path = set_path(quality, j)
            epg = 'sky'
            name = 'Sky Sports 4'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch6":
            path = set_path(quality, j)
            epg = 'sky'
            name = 'Sky Sports 5'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch7":
            path = set_path(quality, j)
            epg = 'sky'
            name = 'Sky Sports f1'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch8":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'BT Sport 1'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch9":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'BT Sport 2'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch10":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'BT Sport europe'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch11":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'BT Sport ESPN'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch12":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'Setanta Sports 1'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch13":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'Setanta Ireland'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch14":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'BoxNation'
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch15":
            path = set_path(quality, j)
            epg = 'locatetv'
            name = 'Racing UK' 
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch16":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 16 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch17":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 17 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch18":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 18 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch19":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 19 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch20":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 20 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch21":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 21 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch22":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 22 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch23":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 23 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch24":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 24 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch25":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 25 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch26":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 26 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch27":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 27 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch28":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 28 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch29":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 29 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
        elif j == "ch30":
            path = set_path(quality, j)
            epg = 'skip'
            name = 'Channel 30 - '
            stream = get_rtmp_url(path)
            if legacy == False:
                addDirectoryItem(j, epg, name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
            else:
                addDirectoryItem_Legacy(name, isPlayable=True, isFolder=False, parameters={ PARAMETER_KEY_MODE: MODE_PLAY, 'url':stream,'name':name })
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def play_stream(url, name):
    item = xbmcgui.ListItem(path=url)
    item.setInfo('video', {'Title': name})
    return xbmcplugin.setResolvedUrl(handle, True, item)

params = parameters_string_to_dict(sys.argv[2])
mode = int(params.get(PARAMETER_KEY_MODE, "0"))

if not sys.argv[2]:
    username = settings.getSetting("username")
    password = settings.getSetting("password")
    if (len(username) and len(password)) == 0:
        dialog = xbmcgui.Dialog().ok("Username and password are not configured","            You need to input your username and password")
        settings.openSettings() 
    else:
        ok = show_root_menu()
elif mode == MODE_SCHEDULE:
    ok = show_schedule()
elif mode == MODE_UPCOMING:
    ok = show_upcoming_schedule()
elif mode == MODE_LIVE_STREAMS_HD:
    ok = show_live_streams('hd', False)
elif mode == MODE_LIVE_STREAMS_SD:
    ok = show_live_streams('sd', False)
elif mode == MODE_LIVE_STREAMS_HD_LEGACY:
    ok = show_live_streams('hd', True)
elif mode == MODE_LIVE_STREAMS_SD_LEGACY:
    ok = show_live_streams('sd', True)
elif mode == MODE_PLAY:
    name = urllib.unquote_plus(params["name"])
    url = urllib.unquote_plus(params["url"])
    ok = play_stream(url, name)