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
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os

import sickbeard
from sickbeard import encodingKludge as ek
from sickbeard import tv
from sickbeard import common
from sickbeard import logger
from sickbeard.name_parser.parser import NameParser, InvalidNameException

from common import Quality, DOWNLOADED

name_presets = ('%SN - %Sx%0E - %EN',
                '%S.N.S%0SE%0E.%E.N',
                '%Sx%0E - %EN',
                'S%0SE%0E - %EN',
                'Season %0S/%S.N.S%0SE%0E.%Q.N-%RG'
                )

name_abd_presets = ('%SN - %A-D - %EN',
                    '%S.N.%A.D.%E.N.%Q.N',
                    '%Y/%0M/%S.N.%A.D.%E.N-%RG'
                    )

name_ae_presets = ('%SN - %0AE - %EN',
                   '%S.N.%0AE.%E.N',
                   '%0AE - %EN',
                   'Episodes/%S.N.%0AE.%Q.N-%RG'
                   )

name_sn_presets = ('%SN %SSN - %0E - %EN',
                   '%S.N.%SS.N.%0E.%E.N',
                   '%SSN - %0E - %EN',
                   '%0S %SS.N/%S.N.%SS.N.%0E.%Q.N-%RG'
                   )
class TVShow():
    def __init__(self):
        self.name = "Show Name"
        self.genre = "Comedy"
        self.air_by_date = 0
        self.anime = 0

class TVEpisode(tv.TVEpisode):
    def __init__(self, season, episode, name, absolute_number):
        self.relatedEps = []
        self._name = name
        self._season = season
        self._episode = episode
        self._absolute_number = absolute_number
        self._airdate = datetime.date(2010, 3, 9)
        self.show = TVShow()
        self._status = Quality.compositeStatus(common.DOWNLOADED, common.Quality.SDTV)
        self._release_name = 'Show.Name.S02E03.HDTV.XviD-RLSGROUP'
        self._is_proper = True
        self._season_name = "Season Name"

def check_force_season_folders(pattern=None, multi=None, sn=False):
    """
    Checks if the name can still be parsed if you strip off the folders to determine if we need to force season folders
    to be enabled or not.
    
    Returns true if season folders need to be forced on or false otherwise.
    """
    if pattern == None:
        pattern = sickbeard.NAMING_PATTERN
    
    valid = not validate_name(pattern, None, file_only=True, sn=sn)
    
    if multi != None:
        valid = valid or not validate_name(pattern, multi, file_only=True, sn=sn)

    return valid

def check_valid_naming(pattern=None, multi=None):
    """
    Checks if the name is can be parsed back to its original form for both single and multi episodes.
    
    Returns true if the naming is valid, false if not.
    """
    if pattern == None:
        pattern = sickbeard.NAMING_PATTERN
        
    logger.log(u"Checking whether the pattern "+pattern+" is valid for a single episode", logger.DEBUG)
    valid = validate_name(pattern, None)

    if multi != None:
        logger.log(u"Checking whether the pattern "+pattern+" is valid for a multi episode", logger.DEBUG)
        valid = valid and validate_name(pattern, multi)

    return valid

def check_valid_abd_naming(pattern=None):
    """
    Checks if the name is can be parsed back to its original form for an air-by-date format.
    
    Returns true if the naming is valid, false if not.
    """
    if pattern == None:
        pattern = sickbeard.NAMING_PATTERN
        
    logger.log(u"Checking whether the pattern "+pattern+" is valid for an air-by-date episode", logger.DEBUG)
    valid = validate_name(pattern, abd=True)

    return valid

def check_valid_ae_naming(pattern=None):
    """
    Checks if the name is can be parsed back to its original form for an absolute-episode format.
    
    Returns true if the naming is valid, false if not.
    """
    if pattern == None:
        pattern = sickbeard.NAMING_PATTERN
        
    logger.log(u"Checking whether the pattern "+pattern+" is valid for an absolute episode", logger.DEBUG)
    valid = validate_name(pattern, ae=True)

    return valid

def check_valid_sn_naming(pattern=None):
    """
    Checks if the name is can be parsed back to its original form for an season-name format.
    
    Returns true if the naming is valid, false if not.
    """
    if pattern == None:
        pattern = sickbeard.NAMING_PATTERN
        
    logger.log(u"Checking whether the pattern "+pattern+" is valid for an season-name episode", logger.DEBUG)
    valid = validate_name(pattern, sn=True)

    return valid


def validate_name(pattern, multi=None, file_only=False, abd=False, ae=False, sn=False):
    ep = _generate_sample_ep(multi, abd, ae, sn)

    parser = NameParser(True, show=ep.show)

    new_name = ep.formatted_filename(pattern, multi) + '.ext'
    new_path = ep.formatted_dir(pattern, multi)
    if not file_only:
        new_name = ek.ek(os.path.join, new_path, new_name)

    if not new_name:
        logger.log(u"Unable to create a name out of "+pattern, logger.DEBUG)
        return False

    logger.log(u"Trying to parse "+new_name, logger.DEBUG)

    try:
        result = parser.parse(new_name)
    except InvalidNameException:
        logger.log(u"Unable to parse "+new_name+", not valid", logger.DEBUG)
        return False
    
    logger.log("The name "+new_name + " parsed into " + str(result), logger.DEBUG)

    if abd:
        if result.air_date != ep.airdate:
            logger.log(u"Air date incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
    elif ae:
        if result.ab_episode_numbers != [x.absolute_number for x in [ep] + ep.relatedEps]:
            logger.log(u"Absolute episode incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
    elif sn:
        
        if str(result.series_name).find(ep._season_name) == -1:
            logger.log(u"Season name incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
    else:
        if result.season_number != ep.season:
            logger.log(u"Season incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
        if result.episode_numbers != [x.episode for x in [ep] + ep.relatedEps]:
            logger.log(u"Episode incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False

    return True

def _generate_sample_ep(multi=None, abd=False, ae=False, sn=False):
    # make a fake episode object
    ep = TVEpisode(2,3,"Ep Name",73)
    ep._status = Quality.compositeStatus(DOWNLOADED, Quality.HDTV)
    ep._airdate = datetime.date(2011, 3, 9)
    if abd:
        ep._release_name = 'Show.Name.2011.03.09.HDTV.XviD-RLSGROUP'
    elif ae:
        ep._release_name = 'Show.Name.073.HDTV.XviD-RLSGROUP'
        ep.show.anime=1
    elif sn:
        ep._release_name = 'Show.Name.Season.Name.03.HDTV.XviD-RLSGROUP'
    else:
        ep._release_name = 'Show.Name.S02E03.HDTV.XviD-RLSGROUP'

    if multi != None:
        ep._name = "Ep Name (1)"
        if ae:
            ep._release_name = 'Show.Name.073-074-075.HDTV.XviD-RLSGROUP'
        elif sn:
            ep._release_name = 'Show.Name.Season.Name.E03E04E05.HDTV.XviD-RLSGROUP'
        else:
            ep._release_name = 'Show.Name.S02E03E04E05.HDTV.XviD-RLSGROUP'

        secondEp = TVEpisode(2,4,"Ep Name (2)",74)
        secondEp._status = Quality.compositeStatus(DOWNLOADED, Quality.HDTV)
        secondEp._release_name = ep._release_name

        thirdEp = TVEpisode(2,5,"Ep Name (3)",75)
        thirdEp._status = Quality.compositeStatus(DOWNLOADED, Quality.HDTV)
        thirdEp._release_name = ep._release_name

        ep.relatedEps.append(secondEp)
        ep.relatedEps.append(thirdEp)

    return ep

def test_name(pattern, multi=None, abd=False, ae=False, sn=False):

    ep = _generate_sample_ep(multi, abd, ae, sn)

    return {'name': ep.formatted_filename(pattern, multi), 'dir': ep.formatted_dir(pattern, multi)}