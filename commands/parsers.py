import requests, lxml
from bs4 import BeautifulSoup

class Parsers:
    def __init__(self) -> None:
        pass

    @classmethod
    def crossroad(cls, url):
        if "music.yandex.ru" in url:
            return cls.YMusicParser(url)
        elif "vk.com" in url:
            return cls.VKMusicParser(url)
        else:
            return None

    @classmethod
    def YMusicParser(cls, url):
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
            if len(names) == len(artists):
                for i in range(len(names)):
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
            return tracklist
    
    @classmethod
    def VKMusicParser(cls, url):
        names = []
        artists = []
        try:
            response = requests.get(url)
        except:
            return None

        bs = BeautifulSoup(response.text,"lxml")
        tracklist = []

        if "playlist" in url:
            p_artists = bs.find_all('a')
            p_names = bs.find_all('span', {'class': 'ai_title'})
            try:
                for entry in p_artists:
                    artists.append(entry.text)
                for entry in p_names:
                    names.append(entry.text)
            except:
                return None
            artists = artists[3:][:-1]
            if len(names) == len(artists):
                for i in range(len(names)):
                    tracklist.append(names[i] + ' ' + artists[i])
            else:
                return None
        else:
            return None
        if tracklist[0] == None:
            return None
        else:
            return tracklist