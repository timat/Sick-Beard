# Author: Nyaran
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

try:
    import json
except ImportError:
    from lib import simplejson as json

import re

import sickbeard
import generic

from sickbeard import show_name_helpers

from sickbeard import logger
from sickbeard.common import Quality
from sickbeard import tvcache

REMOTE_DBG = False

class FrozenLayerProvider(generic.TorrentProvider):

    def __init__(self):
        generic.TorrentProvider.__init__(self, "Frozen-Layer")
        
        self.supportsBacklog = True
        
        self.supportsAbsoluteNumbering = True

        self.cache = FrozenLayerCache(self)

        self.url = 'http://www.frozen-layer.com/'

    def isEnabled(self):
        return sickbeard.FROZENLAYER
        
    def imageName(self):
        return 'frozenlayer.png'
      
    def getQuality(self, item, anime=False):
        title = item['descarga']['titulo_formatted']    
        quality = Quality.nameQuality(title, anime)
        return quality        
        
    def _get_season_search_strings(self, show, season=None):
        names = []
        for name in show_name_helpers.makeSceneShowSearchStrings(show):
            names.append(name.replace('.', '-'))
        return names

    def _get_episode_search_strings(self, ep_obj):
        return self._get_season_search_strings(ep_obj.show, ep_obj.season)
    
    def _get_title_and_url(self, item):
        """
        Retrieves the title and URL data from the item XML node

        item: An xml.dom.minidom.Node representing the <item> tag of the RSS feed

        Returns: A tuple containing two strings representing title and URL respectively
        """
        episode = item['descarga']['titulo_formatted']
        fansub = item['descarga']['fansub_formatted']
        title = '['+fansub+'] '+episode.replace('Episodio ', '')
        url = item['descarga']['magnet']
        
        return (title, url)

    def _doSearch(self, search_string, show=None):
        searchURL = self.url+'animes/'+search_string+'/descargas.json'

        logger.log(u"Search string: " + searchURL, logger.DEBUG)

        data = self.getURL(searchURL)
        
        if not data:
            return []
        
        results = []

        for curItem in json.loads(data):
            (title, url) = self._get_title_and_url(curItem)
            
            if not title or not url:
                logger.log(u"The JSon returned from the Frozen-Layer API is incomplete, this result is unusable: "+data, logger.ERROR)
                continue
    
            results.append(curItem)
        
        return results

    def _extract_name_from_filename(self, filename):
        name_regex = '(.*?)\.?(\[.*]|\d+\.TPB)\.torrent$'
        logger.log(u"Comparing "+name_regex+" against "+filename, logger.DEBUG)
        match = re.match(name_regex, filename, re.I)
        if match:
            return match.group(1)
        return None

   
class FrozenLayerCache(tvcache.TVCache):

    def __init__(self, provider):

        tvcache.TVCache.__init__(self, provider)

        # only poll Frozen-Layer every 15 minutes max
        self.minTime = 15


    def _getRSSData(self):

        url = 'http://feeds.feedburner.com/bittorrent'

        logger.log(u"Frozen-Layer cache update URL: "+ url, logger.DEBUG)

        data = self.provider.getURL(url)

        return data

    def _parseItem(self, item):

        (title, url) = self.provider._get_title_and_url(item)

        if not title or not url:
            logger.log(u"The XML returned from the Frozen-Layer RSS feed is incomplete, this result is unusable", logger.ERROR)
            return

        logger.log(u"Adding item from RSS to cache: "+title, logger.DEBUG)

        self._addCacheEntry(title, url)

provider = FrozenLayerProvider()
