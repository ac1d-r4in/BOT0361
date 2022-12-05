import requests, lxml
from bs4 import BeautifulSoup

class Parsers:

    def YMusicParser(url):
        names = []
        artists = []
        try:
            response = requests.get(url)
        except:
            return None

        bs = BeautifulSoup(response.text,"lxml")
        tracklist = []

        if "playlists" in url:
            p_names = bs.find_all('a', {'class': 'd-track__title deco-link deco-link_stronger'})
            p_artists = bs.find_all('a', {'class': 'deco-link deco-link_muted'})
            try:
                for entry in p_names:
                    names.append(entry.text)
                for entry in p_artists:
                    artists.append(entry.text)
            except:
                return None
            if len(p_names) == len(p_artists):
                for i in range(len(p_names)):
                    tracklist.append(names[i] + artists[i])
            else:
                return None
        elif "album" in url:
            temp = bs.find('a', {'class': 'd-link deco-link'})
            artist = temp.text
            temp = bs.find_all('a', {'class': 'd-track__title deco-link deco-link_stronger'})
            try:
                for entry in temp:
                    tracklist.append(entry.text + artist)
            except:
                return None
        else:
            return None
        if tracklist[0] == None:
            return None
        else:
            print(tracklist)
            return tracklist