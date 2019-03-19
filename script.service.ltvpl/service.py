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

import os, sys
import xbmc
import xbmcgui
import xbmcaddon

#from logger import logxbmc.log("***path")

# print str(sys.path)
myLog = xbmc.log

from util import ADDON, ADDON_PATH, ADDONID, ADDON_USERDATA_FOLDER, BASEPATH, DATAFILE_LOCATIONFILE, ADDON_DATAFILENAME,\
    DEFAULTPATH, DEBUGFILE_LOCATIONFILE, DEBUGFILE_LOCATIONCONTENT, ENUMPATH
from resources.lib.Network.SecretSauce import ServerPort, ServerHost
from resources.PL_Server import PL_Server
from resources.lib.Utilities.Messaging import VACATIONMODE, PREROLLTIME, DAILYSTOPCOMMAND, DEBUGMODE, STOPCMD_ACTIVE,\
    ALARMTIME, ACTIVATIONKEY, COUNTDOWN_DURATION, TRUE, FALSE, WRITEMODE
import Countdown

xbmc.log("***sys.path: "+str(sys.path))

LTVPL = 'Live TV Playlist'

LocalOperationFlag = False
RemoteOperationFlag = False


def establishDataLocations():
    if not os.path.exists(ADDON_USERDATA_FOLDER):
        xbmc.log("LTVPL: Making addonUserDataFolder")
        try:
            os.mkdir(ADDON_USERDATA_FOLDER)
        except:
            pass
    else:
        xbmc.log("LTVPL: addonUserDataFolder Exists")

    #Data File
    fs = open(DATAFILE_LOCATIONFILE,WRITEMODE)
    fs.write(DEFAULTPATH)
    fs.close()
    #

    # Debug File
    fs = open(DEBUGFILE_LOCATIONFILE, WRITEMODE)
    fs.write(DEBUGFILE_LOCATIONCONTENT)
    fs.close()
    xbmc.log("LTVPL: establishDataLocations Done")

xbmc.log("ltvpl data path: " + ADDON_USERDATA_FOLDER )

class Monitor(xbmc.Monitor):
    def __init__(self, server, cdService):
        """

        :type server: PL_Server
        """
        xbmc.Monitor.__init__(self)
        self.server = server #type: PL_Server
        self.cdService = cdService #type: Countdown.miniClient
        self.countdown_duration=int(ADDON.getSetting(COUNTDOWN_DURATION))
        self.debugMode=str(ADDON.getSetting(DEBUGMODE)).lower() == TRUE
        self.vacationMode=str(ADDON.getSetting(VACATIONMODE)).lower() == TRUE
        self.stopcmd_active=str(ADDON.getSetting(STOPCMD_ACTIVE)).lower() == TRUE
        self.strAlarmtime=str(ADDON.getSetting(ALARMTIME))
        self.preroll_time=int(ADDON.getSetting(PREROLLTIME))
        self.activationkey=ADDON.getSetting(ACTIVATIONKEY)

    def onSettingsChanged(self):
        global LocalOperationFlag
        global RemoteOperationFlag
        if RemoteOperationFlag:
            return

        settingsChangedFlag=False
        myLog("onSettingsChanged Called", level=xbmc.LOGDEBUG)
        #Local Settings

        # Countdown Duration
        countdown_duration = int(ADDON.getSetting(COUNTDOWN_DURATION))
        if self.countdown_duration != countdown_duration:
            self.countdown_duration=countdown_duration
            settingsChangedFlag = True

        self.cdService.CountDownDuration = countdown_duration

        # Activation Key
        activationkey=ADDON.getSetting(ACTIVATIONKEY)
        if self.activationkey != activationkey:
            self.activationkey=activationkey
            settingsChangedFlag = True

        #Debug_Mode
        LocalOperationFlag=True
        #Debug Mode
        debugMode = str(ADDON.getSetting(DEBUGMODE)).lower() == TRUE
        if self.debugMode != debugMode:
            self.debugMode=debugMode
            settingsChangedFlag=True

        #Vacation Mode
        vacationMode = str(ADDON.getSetting(VACATIONMODE)).lower() == TRUE
        # import web_pdb;web_pdb.set_trace()
        if self.vacationMode != vacationMode:
            self.vacationMode=vacationMode
            settingsChangedFlag = True

        #Daily Stop Command
        stopcmd_active = str(ADDON.getSetting(STOPCMD_ACTIVE)).lower() == TRUE
        strAlarmtime = str(ADDON.getSetting(ALARMTIME))
        if self.stopcmd_active != stopcmd_active or self.strAlarmtime != strAlarmtime:
            self.stopcmd_active = stopcmd_active
            self.strAlarmtime = strAlarmtime
            settingsChangedFlag = True


        #Preroll Time
        preroll_time = int(ADDON.getSetting(PREROLLTIME))
        if self.preroll_time!= preroll_time:
            self.preroll_time=preroll_time
            settingsChangedFlag = True

        #Process Changed Settings
        try:
            if settingsChangedFlag:
                # import web_pdb; web_pdb.set_trace()
                myLog("settingsChangedFlag: True", level=xbmc.LOGDEBUG)
                self.server.setSettings(vacationMode, debugMode, stopcmd_active, strAlarmtime, preroll_time=preroll_time)

        except ValueError as e:
            xbmcgui.Dialog().notification(LTVPL, e.message)

        LocalOperationFlag=False




def onServerSettingsChanged(setting, value):
    global LocalOperationFlag
    global RemoteOperationFlag
    if LocalOperationFlag:
        return

    RemoteOperationFlag = True
    # import web_pdb; web_pdb.set_trace()
    if setting==PREROLLTIME:
        ADDON.setSetting(PREROLLTIME, str(value))
    elif setting==VACATIONMODE:
        ADDON.setSetting(VACATIONMODE, str(value).lower())
    elif setting==DAILYSTOPCOMMAND:
        if value[STOPCMD_ACTIVE]:
            ADDON.setSetting(STOPCMD_ACTIVE, TRUE)
            ADDON.setSetting(ALARMTIME, value[ALARMTIME])
        else:
            ADDON.setSetting(STOPCMD_ACTIVE, FALSE)

    RemoteOperationFlag = False

if __name__ == '__main__':
    from resources.PL_Server import PLSERVERTAG
    from utility import isDialogActive, clearDialogActive
    cdService = None #type: Countdown.miniClient
    server = None #type: PL_Server

    if not isDialogActive(PLSERVERTAG):
        address = ('', ServerPort)
        establishDataLocations()
        vacationMode = str(ADDON.getSetting(VACATIONMODE)).lower() == TRUE
        debugMode = str(ADDON.getSetting(DEBUGMODE)).lower() == TRUE
        # import web_pdb;web_pdb.set_trace()
        server = PL_Server(address, vacationMode, debugMode)
        strAlarmtime = server.getDailyStopCmdAlarmtime()
        if strAlarmtime is not None:
            ADDON.setSetting(STOPCMD_ACTIVE, TRUE)
            ADDON.setSetting(ALARMTIME, strAlarmtime)

        server.startServer()
        server.addSettingsChangedEventHandler(onServerSettingsChanged)
        xbmc.log("Live TV Playlist Server Started...")

        while not server.server.isAlive():
            xbmc.sleep(500)

        # import Countdown
        try:
            countdown_duration= int(ADDON.getSetting(COUNTDOWN_DURATION))
            cdService = Countdown.StartCountdownService(ADDONID, clockstarttime=countdown_duration, abortChChange=server.dataSet.AbortChannelChangeOperation)
            xbmc.log("****Mini Client Service Successfully Started....")
        except: pass

        monitor = Monitor(server, cdService)
        monitor.waitForAbort()

        xbmc.log("vacationmode1:{}".format(ADDON.getSetting(VACATIONMODE)))
        cdService.Stop()
        server.stopServer()
        xbmc.log("vacationmode2:{}".format(ADDON.getSetting(VACATIONMODE)))

        monitor = None
        del monitor
        cdService = None
        del cdService
        server = None
        del server
        clearDialogActive(PLSERVERTAG)
        xbmc.log("Live TV Playlist Server Stopped...")
