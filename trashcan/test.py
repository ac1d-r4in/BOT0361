import requests, lxml
from bs4 import BeautifulSoup

url = "https://vk.com/audio225729518_456239726_f49b3be7cefd310e2c"
response = requests.get(url)

bs = BeautifulSoup(response.text,"lxml")

print(bs.text)

# names = []
# artists = []
# if "playlist" in url:
#     p_artists = bs.find_all('a')
#     p_names = bs.find_all('span', {'class': 'ai_title'})
#     for entry in p_artists:
#         artists.append(entry.text)
#     for entry in p_names:
#         names.append(entry.text)
#     artists = artists[4:][:-1]
#     if(len(artists) == len(names)):
#         tracklist = []
#         for i in range(len(artists)):
#             tracklist.append(names[i] + ' ' + artists[i])
#         for entry in tracklist:
#             print(entry)
#     else:
#         print("not equal")