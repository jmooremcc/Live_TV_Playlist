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
import xml.etree.ElementTree as ET
from resources.lib.Utilities.indent import indent2

__Version__ = "1.0.0"

class myXML_io(object):
    def __init__(self):
        pass

    def ExportXML(self, fp):
        tree=None
        elem = self.XML
        print(ET.dump(elem))
        try:
            indent2(elem)
            tree = ET.ElementTree(elem)
        except Exception as e:
            pass
        tree.write(fp)

    def ImportXML(self, fp):
        try:
            tree = ET.ElementTree(file=fp)
            self.XML=tree
        except:
            pass