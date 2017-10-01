#!/usr/bin/env python

import xmlrpclib, io, gzip, re
import get_hash
from imdb import IMDb

url = 'https://api.opensubtitles.org/xml-rpc'
server = xmlrpclib.Server(url)
token = server.LogIn('', '', 'en', 'OSTestUserAgentTemp')['token']


def get_subtitles(title, path, language):
    moviehash = get_hash.hashFile(path)
    resp = server.SearchSubtitles(token, [{'sublanguageid':language, 'moviehash':moviehash}])
    if resp['status'] == '200 OK':
        count = len(resp['data'])
        if count > 0:
            subtitle_id = resp['data'][0]['IDSubtitleFile']
            resp = server.DownloadSubtitles(token, [int(subtitle_id)])
            if resp['status'] == '200 OK':
                message = download(resp, path)
        else:
            print "No subtitles found for file. Trying to find subtitles for title."
            ia = IMDb(accessSystem='http')
            if re.findall('(S[0-9]{1,2}E[0-9]{1,2})', title):
                season = int(re.findall('(S[0-9]{1,2})', title)[0][2:])
                print "season: " + str(season)
                episode = int(re.findall('(E[0-9]{1,2})', title)[0][2:])
                print "episode: " + str(episode)
            title = re.sub('( S[0-9]{1,2}E[0-9]{1,2})', '', title)
            results = ia.search_movie(title, results=1)
            if results:
                imdbid = results[0].movieID
                if imdbid:
                    if results[0]['kind'] != 'tv series':
                        resp = server.SearchSubtitles(token, [{'sublanguageid':language, 'imdbid':imdbid}])
                        if resp['status'] == '200 OK':
                            count = len(resp['data'])
                            if count > 0:
                                for data in resp['data']:
                                    if data['SubFileName'][-4:] == '.srt':
                                        print data['SubFileName']
                                        subtitle_id = resp['data'][0]['IDSubtitleFile']
                                        resp = server.DownloadSubtitles(token, [int(subtitle_id)])
                                        if resp['status'] == '200 OK':
                                            message = download(resp, path)
                                        break
                                    else:
                                        message = 'No subtitles in srt format found.'
                            else:
                                message =  "No subtitles found for title."
                                print "No subtitles found for title."
                    else:
                        ia.update(results[0], 'episodes')
                        episodeid = results[0]['episodes'][season][episode].movieID
                        print "episodeid: " + episodeid
                        resp = server.SearchSubtitles(token, [{'sublanguageid':language, 'imdbid':episodeid}])
                        if resp['status'] == '200 OK':
                            count = len(resp['data'])
                            if count > 0:
                                subtitle_id = resp['data'][0]['IDSubtitleFile']
                                resp = server.DownloadSubtitles(token, [int(subtitle_id)])
                                if resp['status'] == '200 OK':
                                    message = download(resp, path)
            else:
                message =  "Couldn't find imdbid for title: " + title
                print "Couldn't find imdbid for title: " + title
    return message

def download(resp, path):
    compressed_data = resp['data'][0]['data'].decode('base64')
    sub_text = gzip.GzipFile(fileobj=io.BytesIO(compressed_data)).read()
    path = path.replace('\ ',' ').replace('\(','(').replace('\)',')')
    with open(path[:-4] + '.srt', 'w') as file:
        file.write(sub_text)
    print "Subtitles downloaded successfully!"
    message =  "Subtitles downloaded successfully!"
    return message
    
