import urllib.request as urllib2
import xml.etree.ElementTree as ET
import requests
from xml.dom.minidom import parseString
import pickle
import App
import threading
import ctypes
import json
import queue

API = '32EADD85E6F53CB6AAF6D21558ED6C73' #your steam api key
gameid = '440' #tf2 is 440
itemschema = {}
run = True
restart = True
count = 0
fcount = 0
ecount = 0

def schema(tf):#get item schema to find item names
    global API
    if tf:
        ctypes.windll.user32.MessageBoxW(0, 'Updating schema, please wait', "Hold on", 0)
        itemschema = {}
        try:
            url = 'http://api.steampowered.com/IEconItems_440/GetSchema/v0001/?key={}&format=json'.format(API)
            data = json.loads(((urllib2.urlopen(url)).read()).decode("utf8"))
        except:
            ctypes.windll.user32.MessageBoxW(0, 'Steam is acting slow, please wait', "Hold on", 0)
            return schema(tf)
        for i in data["result"]["items"]:
            print(i['name'])
            itemschema[i['defindex']] = i['name']
        pickle.dump(itemschema, open(".\data\save.p", "wb"))
        ctypes.windll.user32.MessageBoxW(0, 'Schema updated', "Done", 0)
        return itemschema
    else:
        try:
            return pickle.load(open(".\data\save.p", "rb" ))
        except:
            return schema(True)

def reset(tf): #resets text files that contain steam ids
    global past, future, found
    if tf:
        past = []
        future = []
        found = []
    else:
        try:
            with open('.\data\past.txt', 'r+') as in_file:
                past = in_file.read().split('\n')
        except:
            past = []
        try:
            with open('.\data\\future.txt', 'r+') as in_file:
                future = in_file.read().split('\n')
        except:
            future = []
        try:
            with open('.\data\\found.txt', 'r+') as in_file:
                found = in_file.read().split('\n')
        except:
            found = []

def getid(vanity): #converts vanity url to steam id
    global API
    try:
        url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}&format=json'.format(API, vanity)
        data = json.loads(((urllib2.urlopen(url)).read()).decode("utf8"))
        return data['response']['steamid']
    except:
        ctypes.windll.user32.MessageBoxW(0, 'Steam is acting slow, please wait', "Hold on", 0)
        return getid(vanity)

def getfriend(id): #get user ids of friends
    global future
    global API
    count = 0
    try:
        url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={}&steamid={}&relationship=friend&format=json'.format(API, id)
        data = json.loads(((urllib2.urlopen(url)).read()).decode("utf8"))
        for i in data['friendslist']['friends']:
            count += 1
            if count >25:
                return
            future.append(i['steamid'])
    except Exception as e:
        print(e)
        pass

def hours(id): #find steam hours
    global API, gameid, ecount, future
    try:
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&format=json&input_json={{"appids_filter":[{}],"include_played_free_games":1,"steamid":{}}}'.format(API, gameid, id)
        data = json.loads(((urllib2.urlopen(url)).read()).decode("utf8"))
        hours = ((data['response']['games'][0]['playtime_forever'])/60)
        if len(future) < 200 and hours>500:
            getfriend(id)
        return hours
    except:
        return 50000

def backpack(id, gen, bud, bill, unu, maxs, bmoc, salv, traded): # check backpack
    global API, gameid, found, fcount, run, ecount, itemschema
    try:
        url = 'http://api.steampowered.com/IEconItems_{}/GetPlayerItems/v0001/?key={}&steamid={}&format=json'.format(gameid, API, id)
        data = json.loads(((urllib2.urlopen(url)).read()).decode("utf8"))
    except Exception as e:
        return ''
    got = ''
    if 'items' in data['result']:
        for item in data['result']['items']:
            if (item['quality'] == 5 and item['defindex'] not in [267, 266] and unu):
                pass
            elif(item['quality'] == 1 and gen):
                pass
            elif(item['defindex'] == 143 and bud):
                pass
            elif(item['defindex'] == 126 and bill):
                pass
            elif(item['defindex'] in [160,161,162] and maxs):
                pass
            elif(item['defindex'] == 666 and bmoc):
                pass
            elif(item['defindex'] == 5068 and salv):
                pass
            else:
                continue
            if traded and not (item['id'] == item['original_id']):
                continue
            if got != '':
                got+= ', '
            try:
                got += itemschema[int(item['defindex'])]
            except:
                print(item['defindex'])
                print(str(item['defindex']))
                print(itemschema[str(item['defindex'])])
        if got != '':
            found.append(id)
            fcount+= 1
    return got

def files(): #save lists to files
    global past, future, found
    with open('.\data\past.txt', 'w') as out_file:
        out_file.write('\n'.join(past))
    with open('.\data\\future.txt', 'w') as out_file:
        out_file.write('\n'.join(future))
    with open('.\data\\found.txt', 'w') as out_file:
        out_file.write('\n'.join(found))

if __name__ == '__main__':
    global app
    app = App.Application()

def start(schea, res, id):
    global past, future, found, itemschema, run, qid, qhour, qgot, qcount, iq
    itemschema = schema(schea)
    reset(res)
    if id != '':
        if id.startswith("7656"):
            tempid = id
        else:
            tempid = getid(id)
        future.append(tempid)
    else:
        reset(False)
    qid = queue.Queue()
    qhour = queue.Queue()
    qgot = queue.Queue()
    qcount = 0
    iq = queue.Queue()

def hunt(a, iq, gen, bud, bill, unu, maxs, bmoc, salv, hour, traded):
    global past, run, count, qid, qhour, qgot, future, restart, API
    while iq.qsize() != 0 and run and restart:
        i = iq.get()
        if i in future:
            try:
                future.remove(i)
            except:
                pass
        if i == "":
            ctypes.windll.user32.MessageBoxW(0, 'Please enter an ID', "Error", 0)
            run = False
        if run:
            count +=1
            a.updateGUI()
            if i not in past:
                past.append(i)
                if len(past) % 51 == 0:
                        files()
                uhour = hours(i)
                if uhour<hour:
                    got = backpack(i, gen, bud, bill, unu, maxs, bmoc, salv, traded)
                    if got != '':
                        item = [i, int(uhour), got]
                        a.graph.tree.insert('', 'end', values=item)  

def go(threads, a, gen, bud, bill, unu, maxs, bmoc, salv, hour, traded):
    global future, run, qid, qcount, iq, past, restart,fcount
    while len(future) != 0:
        for i in future:
            if run:
                while i in future:
                    if not qid.empty():
                        item = [str(qid.get()), str(qhour.get()), str(qgot.get())]
                        a.graph.tree.insert('', 'end', values=item) 
                    if len(future) < 100:
                        getfriend(i)
                    if 100 >(iq.qsize()):
                        iq.put(i)
                        try:
                            future.remove(i)
                        except:
                            pass
                    if (qid.empty() and qcount<threads):
                        qcount += 1
                        t = threading.Thread(target=hunt, args = (a, iq, gen, bud, bill, unu, maxs, bmoc, salv, hour, traded))
                        t.daemon = True
                        t.start()
            else:
                a.stop()
                return
            if not restart:
                restart = True
                a.stop()
                a.start()
                return
    a.stop()
    a.start()