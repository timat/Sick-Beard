#!/usr/bin/env python
#
# This file is part of aDBa.
#
# aDBa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aDBa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with aDBa.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement
import hashlib
import os
import requests
import xml.etree.cElementTree as etree


# http://www.radicand.org/blog/orz/2010/2/21/edonkey2000-hash-in-python/
def get_file_hash(filePath):
    """ Returns the ed2k hash of a given file."""
    if not filePath:
        return None
    md4 = hashlib.new('md4').copy

    def gen(f):
        while True:
            x = f.read(9728000)
            if x: yield x
            else: return

    def md4_hash(data):
        m = md4()
        m.update(data)
        return m

    with open(filePath, 'rb') as f:
        a = gen(f)
        hashes = [md4_hash(data).digest() for data in a]
        if len(hashes) == 1:
            return hashes[0].encode("hex")
        else: return md4_hash(reduce(lambda a,d: a + d, hashes, "")).hexdigest()
        
        
def get_file_size(path):
    size = os.path.getsize(path)
    return size

def read_anidb_xml(filePath, forceDownload=False):
    if not filePath:
        filePath = os.path.join(os.path.dirname(os.path.abspath( __file__ )), "animetitles.xml")
        if not os.path.exists(filePath):
            forceDownload = True
    elif os.path.isdir(filePath):
        filePath = os.path.join(filePath, "animetitles.xml")

    if forceDownload:
        download_tvdb_map_xml(filePath)

    return read_xml_into_etree(filePath)

def read_tvdb_map_xml(filePath, forceDownload=False):
    if not filePath:
        filePath = os.path.join(os.path.dirname(os.path.abspath( __file__ )), "anime-list.xml")
        if not os.path.exists(filePath):
            forceDownload = True
    elif os.path.isdir(filePath):
        filePath = os.path.join(filePath, "anime-list.xml")

    if forceDownload:
        download_tvdb_map_xml(filePath)

    return read_xml_into_etree(filePath)

def download_anidb_xml(filePath):
    r = requests.get("http://anidb.net/api/animetitles.xml.gz")
    with open(filePath, "wb") as code:
        code.write(r.content)

def download_tvdb_map_xml(filePath):
    r = requests.get("https://raw.github.com/ScudLee/anime-lists/master/anime-list-full.xml")
    with open(filePath, "wb") as code:
        code.write(r.content)

def read_xml_into_etree(filePath):
        if not filePath:
            return None
        
        f = open(filePath,"r")
        xmlASetree = etree.ElementTree(file = f)
        return xmlASetree
    
