'''
    Ultimate Whitecream
    Copyright (C) 2020

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import xbmcplugin
from resources.lib import utils

SITE_URL = 'https://www.peekvids.com'


def make_url(url, options=False):
    if options:
        sortoption = Get_Sort()
        if sortoption:
            url += '&sort_by=' + sortoption
        filteroptions = Get_Filters()
        if filteroptions['uploaded']:
            url += '&uploaded=' + filteroptions['uploaded']
        if filteroptions['duration']:
            url += '&duration=' + filteroptions['duration']
        if filteroptions['quality']:
            url += '&hd=' + filteroptions['quality']
    return url if url.startswith('http') else 'https:' + url if url.startswith('//') else SITE_URL + url


@utils.url_dispatcher.register('890')
def Main():
    utils.addDir('[COLOR hotpink]Categories[/COLOR]', SITE_URL + '/categories', 893, '', '')
    utils.addDir('[COLOR hotpink]Models[/COLOR]', SITE_URL + '/pornstars', 896, '', '')
    utils.addDir('[COLOR hotpink]Search[/COLOR]', SITE_URL + '/sq?q=', 894, '', '')
    utils.addDir('[COLOR hotpink]Channels[/COLOR]', SITE_URL + '/channels', 897, '', '')
    List(SITE_URL)


@utils.url_dispatcher.register('891', ['url'])
def List(url, options=False):
    try:
        listhtml = utils.getHtml(url, SITE_URL + '/')
    except:
        pass
    try:
        match = re.compile(r'video-item-.*?href="([^"]+)".*?<img[\s]+class="card-img-top"[\s]+src="([^"]+)"[\s]+alt="([^"]+)".*?duration[^>]+>([^<]+)<',
                           re.DOTALL | re.IGNORECASE).findall(listhtml)
        for video, img, name, duration in match:
            name = utils.cleantext(name + " [COLOR deeppink]" + duration.strip() + "[/COLOR]")
            utils.addDownLink(name, make_url(video), 892, make_url(img), '')
    except:
        return None
    try:
        next_page = re.search(r'"next"[\s]+href="([^"]+)"', listhtml).group(1)
        utils.addDir('Next Page', make_url(next_page, options), 891, '')
    except:
        pass
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('892', ['url', 'name'], ['download'])
def Playvid(url, name, download=None):
    videopage = utils.getHtml(url, SITE_URL + '/')
    videos = re.compile('data-hls-src([^=]+)="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(videopage)
    list = {}
    for quality, video_link in videos:
        list[quality + 'p'] = video_link.replace('&amp;', '&')
    videourl = utils.selector('Select quality', list, dont_ask_valid=True, sort_by=lambda x: int(re.findall(r'\d+', x)[0]), reverse=True)
    if not videourl:
        return
    utils.playvid(videourl, name, download)


@utils.url_dispatcher.register('893', ['url'])
def Categories(url):
    listhtml = utils.getHtml(url, SITE_URL + '/')
    try:
        match = re.compile(r'<li>[\s]*<a href="(/category/[^"]+)">([^<]+)<', re.DOTALL | re.IGNORECASE | re.UNICODE).findall(listhtml)
        for catpage, name in match:
            utils.addDir(name, make_url(catpage), 891, '')
    except:
        pass
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('894', ['url'], ['keyword'])
def Search(url, keyword=None):
    if not keyword:
        utils.searchDir(url, 894)
    else:
        List(make_url(url+keyword.replace(' ', '+'), True), True)


@utils.url_dispatcher.register('895')
def Change_Settings():
    utils.addon.openSettings()
    Main()


def Get_Sort():
    sortoptions = {0: 'time', 1: 'rating', 3: None}
    sortvalue = int(utils.addon.getSetting("sortwxf"))
    if sortvalue not in sortoptions:
        # PeekVids Default Sort by Relevance
        sortvalue = 3
        utils.notify('SortError', 'Selected Sort by not available. Using Site Default.')
    return sortoptions[sortvalue]


def Get_Filters():
    filteroption_uploaded = {0: None, 1: 'today', 2: 'week', 3: 'month', 4: 'year'}
    filteroption_duration = {0: None, 1: 'long', 2: 'short'}
    filteroption_quality = {0: None, 1: '1', 2: '2'}
    uploadedvalue = int(utils.addon.getSetting("filteruploaded"))
    if uploadedvalue not in filteroption_uploaded:
        uploadedvalue = 0
        utils.notify('FilterError', 'Selected Uploaded Date Filter not available. Using Site Default.')
    durationvalue = int(utils.addon.getSetting("filterduration"))
    if durationvalue == 3:
        durationvalue = 1
    if durationvalue not in filteroption_duration:
        durationvalue = 0
        utils.notify('FilterError', 'Selected Duration Filter not available. Using Site Default.')
    qualityvalue = int(utils.addon.getSetting("filterquality"))
    if qualityvalue not in filteroption_quality:
        qualityvalue = 0
        utils.notify('FilterError', 'Selected Quality Filter not available. Using Site Default.')
    filteroptions = {'uploaded': filteroption_uploaded[uploadedvalue],
                     'duration': filteroption_duration[durationvalue], 'quality': filteroption_quality[qualityvalue]}
    return filteroptions


@utils.url_dispatcher.register('896', ['url'])
def Models(url):
    listhtml = utils.getHtml(url, SITE_URL + '/')
    try:
        match = re.compile('<li class="overflow-visible">.*?href="/pornstar/([^"]+)"', re.DOTALL | re.IGNORECASE).findall(listhtml)
        for model in match:
            utils.addDir(model.replace('-', ' '), make_url('/pornstar/' + model), 891, '')
    except:
        return None
    try:
        next_page = re.search(r'"next"[\s]+href="([^"]+)"', listhtml).group(1)
        utils.addDir('Next Page', make_url(next_page), 896, '')
    except:
        pass
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('897', ['url'])
def Channels(url):
    listhtml = utils.getHtml(url, SITE_URL + '/')
    try:
        match = re.compile('class="card-img".*?href="(/[^"]+)".*?<img class="card-img-top".*?src="[^"]+".*?alt="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(listhtml[listhtml.find('popular_channels'):])
        for channel, name in match:
            utils.addDir(name.strip(), make_url(channel), 891, '')
    except:
        return None
    try:
        next_page = re.search(r'"next"[\s]+href="([^"]+)"', listhtml).group(1)
        utils.addDir('Next Page', make_url(next_page), 897, '')
    except:
        pass
    xbmcplugin.endOfDirectory(utils.addon_handle)
