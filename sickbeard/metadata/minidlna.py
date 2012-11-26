# Author: Nic Wolfe <nic@wolfeden.ca>
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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import os

import generic

from sickbeard import logger, exceptions, helpers
from sickbeard import encodingKludge as ek

class MinidlnaMetadata(generic.GenericMetadata):    
    def __init__(self,
                 show_metadata=False,
                 episode_metadata=False,
                 poster=False,
                 fanart=False,
                 episode_thumbnails=False,
                 season_thumbnails=False):

        generic.GenericMetadata.__init__(self,
                                         show_metadata,
                                         episode_metadata,
                                         poster,
                                         fanart,
                                         episode_thumbnails,
                                         season_thumbnails)
        
        self.poster_name = 'cover.jpg'
        self.name = 'minidlna'

        self.eg_show_metadata = "<i>not supported</i>"
        self.eg_episode_metadata = "<i>filename</i>.nfo"
        self.eg_fanart = "<i>not supported</i>"
        self.eg_poster = "cover.jpg"
        self.eg_episode_thumbnails = "<i>filename</i>.jpg"
        self.eg_season_thumbnails = "<i>not supported</i>"
    
    # all of the following are not supported, so do nothing
    def create_show_metadata(self, show_obj):
        pass
    
    def create_episode_metadata(self, ep_obj):
        pass
    
    def create_fanart(self, show_obj):
        pass
    
    def create_season_thumbs(self, show_obj):
        pass
    
    def get_episode_thumb_path(self, ep_obj):
        """
        Returns the path where the episode thumbnail should be stored. Defaults to
        the same path as the episode file but with a .metathumb extension.
        
        ep_obj: a TVEpisode instance for which to create the thumbnail
        """
        if ek.ek(os.path.isfile, ep_obj.location):
            tbn_filename = helpers.replaceExtension(ep_obj.location, 'jpg')
        else:
            return None

        return tbn_filename

    def get_season_thumb_path(self, show_obj, season):
        """
        Season thumbs for WDTV go in Show Dir/Season X/folder.jpg
        
        If no season folder exists, None is returned
        """
        
        dir_list = [x for x in ek.ek(os.listdir, show_obj.location) if ek.ek(os.path.isdir, ek.ek(os.path.join, show_obj.location, x))]
        
        season_dir_regex = '^Season\s+(\d+)$'
        
        season_dir = None
        
        for cur_dir in dir_list:
            if season == 0 and cur_dir == 'Specials':
                season_dir = cur_dir
                break
            
            match = re.match(season_dir_regex, cur_dir, re.I)
            if not match:
                continue
        
            cur_season = int(match.group(1))
            
            if cur_season == season:
                season_dir = cur_dir
                break

        if not season_dir:
            logger.log(u"Unable to find a season dir for season "+str(season), logger.DEBUG)
            return None

        logger.log(u"Using "+str(season_dir)+"/folder.jpg as season dir for season "+str(season), logger.DEBUG)

        return ek.ek(os.path.join, show_obj.location, season_dir, 'folder.jpg')

    def retrieveShowMetadata(self, dir):
        return (None, None)

    def _ep_data(self, ep_obj):
        """
        Creates an elementTree XML structure for an XBMC-style episode.nfo and
        returns the resulting data object.
        
        show_obj: a TVEpisode instance to create the NFO for
        """

        eps_to_write = [ep_obj] + ep_obj.relatedEps

        tvdb_lang = ep_obj.show.lang
        # There's gotta be a better way of doing this but we don't wanna
        # change the language value elsewhere
        ltvdb_api_parms = sickbeard.TVDB_API_PARMS.copy()

        if tvdb_lang and not tvdb_lang == 'en':
            ltvdb_api_parms['language'] = tvdb_lang

        try:
            t = tvdb_api.Tvdb(actors=True, **ltvdb_api_parms)
            myShow = t[ep_obj.show.tvdbid]
        except tvdb_exceptions.tvdb_shownotfound, e:
            raise exceptions.ShowNotFoundException(e.message)
        except tvdb_exceptions.tvdb_error, e:
            logger.log(u"Unable to connect to TVDB while creating meta files - skipping - "+ex(e), logger.ERROR)
            return

        if len(eps_to_write) > 1:
            rootNode = etree.Element( "xbmcmultiepisode" )
        else:
            rootNode = etree.Element( "episodedetails" )

        # Set our namespace correctly
        for ns in XML_NSMAP.keys():
            rootNode.set(ns, XML_NSMAP[ns])

        # write an NFO containing info for all matching episodes
        for curEpToWrite in eps_to_write:

            try:
                myEp = myShow[curEpToWrite.season][curEpToWrite.episode]
            except (tvdb_exceptions.tvdb_episodenotfound, tvdb_exceptions.tvdb_seasonnotfound):
                logger.log(u"Unable to find episode " + str(curEpToWrite.season) + "x" + str(curEpToWrite.episode) + " on tvdb... has it been removed? Should I delete from db?")
                return None

            if not myEp["firstaired"]:
                myEp["firstaired"] = str(datetime.date.fromordinal(1))

            if not myEp["episodename"]:
                logger.log(u"Not generating nfo because the ep has no title", logger.DEBUG)
                return None

            logger.log(u"Creating metadata for episode "+str(ep_obj.season)+"x"+str(ep_obj.episode), logger.DEBUG)

            if len(eps_to_write) > 1:
                episode = etree.SubElement( rootNode, "episodedetails" )
            else:
                episode = rootNode

            title = etree.SubElement( episode, "title" )
            if curEpToWrite.name != None:
                title.text = curEpToWrite.name

            season = etree.SubElement( episode, "season" )
            season.text = str(curEpToWrite.season)

            episodenum = etree.SubElement( episode, "episode" )
            episodenum.text = str(curEpToWrite.episode)

            aired = etree.SubElement( episode, "aired" )
            if curEpToWrite.airdate != datetime.date.fromordinal(1):
                aired.text = str(curEpToWrite.airdate)
            else:
                aired.text = ''

            plot = etree.SubElement( episode, "plot" )
            if curEpToWrite.description != None:
                plot.text = curEpToWrite.description

            displayseason = etree.SubElement( episode, "displayseason" )
            if myEp.has_key('airsbefore_season'):
                displayseason_text = myEp['airsbefore_season']
                if displayseason_text != None:
                    displayseason.text = displayseason_text

            displayepisode = etree.SubElement( episode, "displayepisode" )
            if myEp.has_key('airsbefore_episode'):
                displayepisode_text = myEp['airsbefore_episode']
                if displayepisode_text != None:
                    displayepisode.text = displayepisode_text

            thumb = etree.SubElement( episode, "thumb" )
            thumb_text = myEp['filename']
            if thumb_text != None:
                thumb.text = thumb_text

            watched = etree.SubElement( episode, "watched" )
            watched.text = 'false'

            credits = etree.SubElement( episode, "credits" )
            credits_text = myEp['writer']
            if credits_text != None:
                credits.text = credits_text

            director = etree.SubElement( episode, "director" )
            director_text = myEp['director']
            if director_text != None:
                director.text = director_text

            rating = etree.SubElement( episode, "rating" )
            rating_text = myEp['rating']
            if rating_text != None:
                rating.text = rating_text

            gueststar_text = myEp['gueststars']
            if gueststar_text != None:
                for actor in gueststar_text.split('|'):
                    cur_actor = etree.SubElement( episode, "actor" )
                    cur_actor_name = etree.SubElement(
                        cur_actor, "name"
                        )
                    cur_actor_name.text = actor

            for actor in myShow['_actors']:
                cur_actor = etree.SubElement( episode, "actor" )

                cur_actor_name = etree.SubElement( cur_actor, "name" )
                cur_actor_name.text = actor['name']

                cur_actor_role = etree.SubElement( cur_actor, "role" )
                cur_actor_role_text = actor['role']
                if cur_actor_role_text != None:
                    cur_actor_role.text = cur_actor_role_text

                cur_actor_thumb = etree.SubElement( cur_actor, "thumb" )
                cur_actor_thumb_text = actor['image']
                if cur_actor_thumb_text != None:
                    cur_actor_thumb.text = cur_actor_thumb_text

        #
        # Make it purdy
        helpers.indentXML( rootNode )

        data = etree.ElementTree( rootNode )

        return data

# present a standard "interface"
metadata_class = MinidlnaMetadata

