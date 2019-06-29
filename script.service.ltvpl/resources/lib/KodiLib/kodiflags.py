
try:
    import xbmc
    KODI_ENV = False

    if xbmc.getFreeMem() == long:
        KODI_ENV = False
    else:
        KODI_ENV = True
except:
    KODI_ENV = False
