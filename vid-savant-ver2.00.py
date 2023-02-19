# ## Getting videos from Baseball Savant ###

# import urllib.request
import re
import os
import glob
import shutil
import requests
import youtube_dl
from bs4 import BeautifulSoup
import pandas as pd


def find_video_links(webpage_html):
    expression = r'"(/sporty-v.*?)" target'
    return re.findall(expression, webpage_html)


def find_pitch_types(webpage_html):
    expression = r'search-pitch-label-.*?</span>'
    return re.findall(expression, webpage_html)


def download_video(url, name):
    url_2 = f"https://baseballsavant.mlb.com{url}"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_2])


def download_all_matches(matches):
    i = 1
    for match in matches:
        print(f"Downloading video {i} of {len(matches)} with url: https://baseballsavant.mlb.com{match}")
        download_video(match, i)
        i += 1


def rename(directory):
    os.chdir(directory)
    num = 1
    for file in [file for file in sorted(os.listdir(), key=os.path.getctime, reverse=False) if os.path.splitext(file)[1] == ".mp4"]:
        if os.path.splitext(file)[1] == ".mp4":
            os.rename(file, "name{:03d}.mp4".format(num))
            num += 1


ydl_opts = {}


# Expects date arguments in the format 2019-05-11
start_date = input("Enter start date (YYYY-MM-DD): ")
end_date = input("Enter end date (YYYY-MM-DD): ")
season = start_date[:4]
player_id = input("Enter player ID: ")
is_last_pitch_str = input("Is last pitch (True/False)? ")

is_last_pitch = is_last_pitch_str.lower() == "true"
flag = "is...last...pitch|" if is_last_pitch else ""
url = f"https://baseballsavant.mlb.com/statcast_search?hfPTM=&hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea={season}%7C&hfSit=&player_type=pitcher&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_date}&game_date_lt={end_date}&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag={flag}&pitchers_lookup%5B%5D={player_id}&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&type=details&player_id={player_id}"
r = requests.get(url, allow_redirects=True)
html = r.content

open('site.txt', 'wb').write(html)

with open('site.txt', encoding='utf-8') as f:
    lines = f.read()

matches = find_video_links(lines)
matches.reverse()

soup = BeautifulSoup(r.text, "html.parser")
# Obtain information from tag <table>
table1 = soup.find('table', id=f"ajaxTable_{player_id}")

# Obtain every title of columns with tag <th>
headers = []
for i in table1.find_all('th'):
    title = i.text
    headers.append(title)


df = pd.read_html(lines, encoding='latin1', header=0)[0]
del df[df.columns[-1]]
df = df.loc[::-1].reset_index(drop=True)


if len(matches) <= 1:
    print("ERROR, 0 matches found in request")
    exit()

pitch = input("Enter pitch  type: ")
found = df.index[df['Pitch'] == pitch].tolist()
df2 = df.loc[df['Pitch'] == pitch]
result = [matches[i] for i in found]

"""
download_all_matches(result)
rename(os.getcwd())

src_folder = os.getcwd()
dst_folder = os.getcwd() + "/vids/"

try: 
    os.mkdir(dst_folder) 
except OSError as error: 
    print(error) 


# Search files with .mp4 extension in source directory
pattern = "\*.mp4"
files = glob.glob(src_folder + pattern)

# move the files with mp4 extension
for file in files:
    # extract file name form file path
    file_name = os.path.basename(file)
    shutil.move(file, dst_folder + file_name)
    print('Moved:', file)

"""
df2['MPH'] = df2['MPH'].astype(float)
avg = df2["MPH"].mean()
print(avg)