#
#       Copyright (C) 2018
#       John Moore (jmooremcc@hotmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
from datetime import datetime, timedelta
import time
from kodiflags import KODI_ENV
from kodijson import Kodi, PLAYER_VIDEO
import json
from resources.lib.Utilities.DebugPrint import DbgPrint

__Version__ = "1.2.0"

def GetOE2():
    """
    :rtype Kodi
    :return:
    """
    return(Kodi("http://192.168.3.107:8080/jsonrpc"))


if KODI_ENV:
    kodiObj=Kodi('')
else:
    kodiObj=GetOE2()

KODI_OPERATION_FAILED= "Kodi Operation Failed: "


def getRecordings2(kodiObj,params=None):
    """
    :param kodiObj: Kodi
    :param params:
    :return: list[string]
    """
    try:
        rList = getRecordings(kodiObj, params)
        newList = []
        for item in rList:
            recordingID = item['recordingid']
            details=getRecordingDetails(kodiObj, recordingID)
            newData= {'recordingid': recordingID, 'tvshow': details['directory'], 'episode': item['label']}
            newList.append(newData)

        tmp = sorted(newList, key=lambda item: (item['tvshow'],item['episode']))
        return(tmp)
    except:
        raise Exception(KODI_OPERATION_FAILED + "Could Not Retrieve Recordings")

    
def getRecordingDetails(kodiObj, recordingID):
    """
    :param kodiObj: Kodi
    :param recordingID:
    :return:
    """
    try:
        return(kodiObj.PVR.GetRecordingDetails({"recordingid":recordingID,\
                'properties':["plot","title","runtime","directory"]})['result']['recordingdetails'])
    except:
        raise Exception(KODI_OPERATION_FAILED + "Could Not Retrieve Recording Details")


def getRecordings(kodiObj, params=None):
    """
    :param kodiObj: Kodi
    :param params:
    :return:
    """
    try:
        if params is None:
            return(kodiObj.PVR.GetRecordings()['result']['recordings'])
        else:
            return(kodiObj.PVR.GetRecordings(params)['result']['recordings'])
    except:
        raise Exception(KODI_OPERATION_FAILED + "Could Not Retrieve Recordings")


def getChannelGroups(kodiObj):
    """
    :param kodiObj: Kodi
    :return:
    """
    try:
        channelGroups = kodiObj.PVR.GetChannelGroups({"channeltype":"tv"})['result']['channelgroups']
        groupList = [(dItem['label'],dItem['channelgroupid']) for dItem in channelGroups]
        return([dict(groupList)])
    except:
        raise Exception(KODI_OPERATION_FAILED + "Cannot Retrieve Channel Groups")


def processChannelNumber(channelNumber):
    """
    :param channelNumber: float
    :return: list[int,int]
    """
    t1=str(channelNumber).split('.')
    if len(t1) == 2:
        c=int(t1[0])
        s=int(t1[1])
        return([c,s])

    return([int(channelNumber), 0])

def getLastChannelInfo(kodiObj, chGroup=1):
    p1 = {"channelgroupid": chGroup, \
          'properties': ['channel', 'channelnumber', 'subchannelnumber']}

    d1 = [item for item in (kodiObj.PVR.GetChannels(p1)) \
        ['result']['channels']]

    numchannels = len(d1)
    x = d1[numchannels -1]
    channel = 'channelnumber', float("{}.{}".format(x['channelnumber'], x['subchannelnumber']))

    return dict([channel])

def getChannelInfoByChannelNumber(kodiObj,channelNumber,chGroup=1,params=None):
    """
    :param kodiObj: Kodi
    :param channelNumber: float
    :param chGroup: int
    :param params:
    :return: list
    """
    try:
        chanNums = processChannelNumber(channelNumber)
        if chanNums is not None:
            channelNumber, subChanneNumber = chanNums
            try:
                p1={"channelgroupid":chGroup,\
                'properties':['channel','channelnumber','subchannelnumber']}

                if params is not None:
                    p1.update(params)

                d1=[item for item in (kodiObj.PVR.GetChannels(p1))\
            ['result']['channels']if channelNumber == item['channelnumber']\
            and subChanneNumber == item['subchannelnumber']]

                z1=[(('stationID',x['label']),('channelid',x['channelid']),\
                     ('channelnumber',float("{}.{}".format(x['channelnumber'],
                       x['subchannelnumber'])))) for x in d1]


                return([dict(z) for z in z1])

            except:
                d1=[item for item in (kodiObj.PVR.GetChannels({"channelgroupid":chGroup,\
                'properties':['channel']}))['result']['channels']\
                 if channelNumber in item['channelnumber']]

                z1=[(('label',x['label']),('channelid',x['channelid'])) for x in d1]
                return([dict(z) for z in z1])
        else:
            return(None)
    except:
        raise Exception(KODI_OPERATION_FAILED + "Could Not Retrieve Channel Info by Channel Number {}".format(channelNumber))


def getChannelInfoByCallSign(kodiObj,callSign,chGroup=1,params=None):
    """
    :param kodiObj: Kodi
    :param callSign: string
    :param chGroup: int
    :param params:
    :return: list
    """
    try:
        p1={"channelgroupid":chGroup,\
        'properties':['channel','channelnumber','subchannelnumber']}

        if params is not None:
            p1.update(params)
        
        d1=[item for item in (kodiObj.PVR.GetChannels(p1))['result']['channels']\
         if callSign in item['channel']]

        z1=[(('stationID',x['label']),('channelid',x['channelid']),\
             ('channelnumber',float("{}.{}".format(x['channelnumber'],
               x['subchannelnumber'])))) for x in d1]
        
        return([dict(z) for z in z1])
    
    except:
        d1=[item for item in (kodiObj.PVR.GetChannels({"channelgroupid":chGroup,\
        'properties':['channel']}))['result']['channels']\
         if callSign in item['channel']]

        z1=[(('label',x['label']),('channelid',x['channelid'])) for x in d1]        
        return([dict(z) for z in z1])


def getChannelInfo(kodiObj,chGroup=1,params=None):
    """
    :param kodiObj: Kodi
    :param chGroup: int
    :param params:
    :return: list
    """
    try:
        p1={"channelgroupid":chGroup, 'properties':['channel','channelnumber','subchannelnumber']}
        
        if params is not None:
            p1.update(params)

        d1=[item for item in (kodiObj.PVR.GetChannels(p1))['result']['channels']]
            
        z1=[(('stationID',x['label']),('channelid',x['channelid']),\
             ('channelnumber',float("{}.{}".format(x['channelnumber'],
               x['subchannelnumber'])))) for x in d1]
        
        return([dict(z) for z in z1])
    
    except Exception as e:
        d1=[item for item in (kodiObj.PVR.GetChannels({"channelgroupid":chGroup,\
        'properties':['channel']}))['result']['channels']\
         if callSign in item['channel']]

        z1=[(('label',x['label']),('channelid',x['channelid'])) for x in d1]        
        return([dict(z) for z in z1])
    


def getPlayerInfo(kodiObj):
    """
    :param kodiObj: Kodi
    :return:
    """
    pList = kodiObj.Player.GetActivePlayers()['result']
    if len(pList) > 0:
        return(pList[0])
    else:
        return(None)
	    

def playerStop(kodiObj):
    """
    :param kodiObj: Kodi
    :return:
    """
    data=getPlayerInfo(kodiObj)
    if data is not None:
        id = data['playerid']
        kodiObj.Player.Stop({"playerid": id})
    

def changeChannelByChannelID(kodiObj, channelID):
    """
    :param kodiObj: Kodi
    :param channelID: int
    :return:
    """
    kodiObj.Player.Open({'item':{'channelid':channelID}})


def changeChannelByCallSign(kodiObj, callSign):
    """
    :param kodiObj: Kodi
    :param callSign: string
    :return:
    """
    channelInfo = getChannelInfoByCallSign(kodiObj, callSign)
    kodiObj.Player.Open({'item':{'channelid':channelInfo[0]['channelid']}})


def changeChannelByChannelNumber(kodiObj, channelNumber):
    """
    :param kodiObj: Kodi
    :param channelNumber: float
    :return:
    """
    channelInfo = getChannelInfoByChannelNumber(kodiObj, channelNumber)
    kodiObj.Player.Open({'item':{'channelid':channelInfo[0]['channelid']}})
    
def prettyPrintJSON(txt):
    data=json.dumps(txt, sort_keys=True,indent=4,separators=(',', ': '))
    print(data)


def datetime_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def getChannelId(kodiObj, channel):
    info = getChannelInfoByChannelNumber(kodiObj, channel)
    channelid = info[0]['channelid']
    return channelid


def getBroadcastIdList(broadcasts, tvshow):
    tvshowlc = tvshow.lower()
    idlist = [broadcast['broadcastid'] for broadcast in broadcasts if tvshowlc in broadcast['label'].lower()]
    # for broadcast in broadcasts:
    #     if tvshowlc in broadcast['label'].lower():
    #         return broadcast['broadcastid']

    return idlist


def getBroadcast_startTimeList(kodiObj, channel, tvshow):
    fmt = '%Y-%m-%d %H:%M:%S'
    channelid = getChannelId(kodiObj, channel)
    args = {"channelid": channelid}
    DbgPrint("tvshow:{}, channel:{}, args:{}".format(tvshow, channel,args))
    broadcastinfo = kodiObj.PVR.GetBroadcasts(args)
    DbgPrint("broadcastinfo:{}".format(broadcastinfo))
    broadcastidList = getBroadcastIdList(broadcastinfo['result']['broadcasts'], tvshow)
    startTimeList = []
    if broadcastidList is not None:
        for broadcastid in broadcastidList:
            pgminfo = kodiObj.PVR.GetBroadcastDetails({'broadcastid': broadcastid, 'properties': ['starttime']})
            starttime = datetime.strptime(pgminfo['result']['broadcastdetails']['starttime'], fmt)
            starttime = datetime_utc_to_local(starttime)
            startTimeList.append(starttime)

        return startTimeList


def TvGuideIsPresent(kodiObj, channel):
    try:
        channelid = getChannelId(kodiObj, channel)
        args = {"channelid": channelid}
        broadcastinfo = kodiObj.PVR.GetBroadcasts(args)
        DbgPrint("broadcastinfo:{}".format(broadcastinfo))
        broadcastdata = broadcastinfo['result']['broadcasts']
        if len(broadcastdata) > 0 and type(broadcastdata[0]['broadcastid']) == int:
            return True
    except: pass

    return False

