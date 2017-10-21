#!/usr/bin/env python

import xmlrpclib, io, gzip, re, os
import get_hash
from imdb import IMDb


def get_subtitles(title, path, language, sub_no):

    url = 'https://api.opensubtitles.org/xml-rpc'
    server = xmlrpclib.Server(url)
    try:
        token = server.LogIn('', '', 'en', 'OSTestUserAgentTemp')['token']
    except xmlrpclib.ProtocolError:
        message = "Error when loggin into OpenSubtitles"
        return message

    moviehash = get_hash.hashFile(path)
    resp = server.SearchSubtitles(token, [{'sublanguageid':language, 'moviehash':moviehash}])
    if resp['status'] == '200 OK':
        count = len(resp['data'])
        if count > 0:
            if sub_no < count:
                print resp['data'][sub_no]['SubFileName']
                subtitle_id = resp['data'][sub_no]['IDSubtitleFile']
                encoding = resp['data'][sub_no]['SubEncoding']
                print "Encoding: " + encoding
                resp = server.DownloadSubtitles(token, [int(subtitle_id)])
                if resp['status'] == '200 OK':
                    match_type = 'exact'
                    message = save_subs(resp, path, count, match_type, encoding)
                else:
                    message = resp['status']
                    print resp['status']
            else:
                message = 'Subtitle number out of range'
                print 'Subtitle number out of range'
        else:
            print "No subtitles found for file. Trying to find subtitles for title."
            match_type = 'title'
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
                                if sub_no < count:
                                    if resp['data'][sub_no]['SubFileName'][-4:] == '.srt':
                                        print resp['data'][sub_no]['SubFileName']
                                        subtitle_id = resp['data'][sub_no]['IDSubtitleFile']
                                        encoding = resp['data'][sub_no]['SubEncoding']
                                        print "Encoding: " + encoding
                                        resp = server.DownloadSubtitles(token, [int(subtitle_id)])
                                        if resp['status'] == '200 OK':
                                            message = save_subs(resp, path, count, match_type, encoding)
                                        else:
                                            message = resp['status']
                                            print resp['status']
                                    else:
                                        message = 'Incorrect format of subtitles.'
                                        print 'Incorrect format of subtitles.'
                                else:
                                    message = 'Subtitle number out of range'
                                    print 'Subtitle number out of range'
                            else:
                                message =  "No subtitles found for movie title."
                                print "No subtitles found for movie title."
                        else:
                            message = resp['status']
                            print resp['status']
                    else:
                        ia.update(results[0], 'episodes')
                        episodeid = results[0]['episodes'][season][episode].movieID
                        print "episodeid: " + episodeid
                        resp = server.SearchSubtitles(token, [{'sublanguageid':language, 'imdbid':episodeid}])
                        if resp['status'] == '200 OK':
                            count = len(resp['data'])
                            if count > 0:
                                if sub_no < count:
                                    print resp['data'][sub_no]['SubFileName']
                                    subtitle_id = resp['data'][sub_no]['IDSubtitleFile']
                                    encoding = resp['data'][sub_no]['SubEncoding']
                                    print "Encoding: " + encoding
                                    resp = server.DownloadSubtitles(token, [int(subtitle_id)])
                                    if resp['status'] == '200 OK':
                                        message = save_subs(resp, path, count, match_type, encoding)
                                    else:
                                        message = resp['status']
                                        print resp['status']
                                else:
                                    message = 'Subtitle number out of range'
                                    print 'Subtitle number out of range'
                            else:
                                message =  "No subtitles found for tv series title."
                                print "No subtitles found for tv series title."
                        else:
                            message = resp['status']
                            print resp['status']
                else:
                    message = resp['status']
                    print resp['status']
            else:
                message =  "Movie " + title + " not found in database."
                print "Movie " + title + " not found in database."
    else:
        message = resp['status']
        print resp['status']
    
    return message

def save_subs(resp, path, count, match_type, encoding):
    compressed_data = resp['data'][0]['data'].decode('base64')
    sub_text = gzip.GzipFile(fileobj=io.BytesIO(compressed_data)).read()
    path = path.replace('\ ',' ').replace('\(','(').replace('\)',')')
    sub_path = path[:-4] + '.srt' 
    if encoding.lower() == 'utf-8':
        with open(sub_path, 'w') as file:
            file.write(sub_text)
    else:
        sub_conv = path[:-4] + '_2.srt' 
        sub_path = sub_path.replace('\ ',' ').replace('\(','(').replace('\)',')')
        sub_conv = sub_conv.replace('\ ',' ').replace('\(','(').replace('\)',')')
        with open(sub_path, 'w') as file:
            file.write(sub_text)
        os.system("cp '" + sub_path + "' '" + sub_conv + "'")
        os.system("rm '" + sub_path + "'")
        os.system("iconv -f " + encoding + " -t utf-8 '" + sub_conv + "' -o '" + sub_path + "'")
        print "Encoding changed from " + encoding + " to utf-8."
        os.system("rm '" + sub_conv + "'")
    print "Subtitles downloaded using " + match_type + " search (" + str(count) + " available)."
    message =  "Subtitles downloaded using " + match_type + " search (" + str(count) + " available)."
    return message

