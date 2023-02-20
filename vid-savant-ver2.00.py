# Getting videos and info from Baseball Savant ###
""" The following code allows a throughful extraction
of data from Baseball Savant """

import re
import os
import glob
import shutil
from urllib.parse import urlencode, urljoin
import requests
import youtube_dl
from bs4 import BeautifulSoup
import pandas as pd
import unicodecsv as csv
from fuzzywuzzy import fuzz

def find_video_links(webpage_html):
    """ Extracts the portion of the link that points to
    the video file """
    expression = r'"(/sporty-v.*?)" target'
    return re.findall(expression, webpage_html)


def find_pitch_types(webpage_html):
    """ Extracts the portion of the tag that points
     to the pitch type """
    expression = r'search-pitch-label-.*?</span>'
    return re.findall(expression, webpage_html)


def download_video(url, name):
    """ Downloads the video file, according to the
     pitch url """
    url_2 = f"https://baseballsavant.mlb.com{url}"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_2])


def download_all_matches(matches):
    """ Download all pitches video files """
    i = 1
    for match in matches:
        print(f"Downloading video {i} of {len(matches)} with url: https://baseballsavant.mlb.com{match}")
        download_video(match, i)
        i += 1


def rename(directory):
    """ Rename all the downloaded video files """
    os.chdir(directory)
    num = 1
    for file in [file for file in sorted(os.listdir(), key=os.path.getctime, reverse=False) if os.path.splitext(file)[1] == ".mp4"]:
        if os.path.splitext(file)[1] == ".mp4":
            os.rename(file, "name{:03d}.mp4".format(num))
            num += 1


def save_to_file(player, player_data):
    """ Save the full data for each pitch to a csv file """
    if not player_data:
        print("No player data to save to file.")
        return

    player_name = player.replace(".", "").strip().lower()
    filename = "_".join(player_name.split(" ")) + ".csv"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "wb") as csv_file:
        rows = []
        writer = csv.writer(
            csv_file,
            delimiter=",",
            quotechar="\""
        )

        header = player_data[0].keys()
        rows.append(header)

        for data in player_data:
            row = [data[key] for key in header]
            rows.append(row)

        reversed_rows = rows[:0:-1]
        rows = rows[:1] + reversed_rows
        writer.writerows(rows)
 

# Parameters for youtube
ydl_opts = {}


# Expects date arguments in the format 2019-05-11
start_date = input("Enter start date (YYYY-MM-DD): ")
end_date = input("Enter end date (YYYY-MM-DD): ")
season = start_date[:4]


# player_id = input("Enter player ID: ")


url_id_map='https://drive.google.com/file/d/1KdSy7hWrrvpBbDVlR07yv5xxjZdfKK2F/view?usp=share_link'
url_id_map='https://drive.google.com/uc?id=' + url_id_map.split('/')[-2]
df_id_map = pd.read_csv(url_id_map)

exect = True
player_name = ""
while exect:
    player_name = input('Enter player name - NAME LASTNAME: ')

    # Create an empty dataframe to store matching rows
    matching_df = pd.DataFrame(columns=df_id_map.columns)

    # Loop through each row of the original dataframe
    for index, row in df_id_map.iterrows():
        # Use the fuzzywuzzy library to compare the name variable to the value in column B
        # If the match score is above the threshold of 70, add the row to the matching dataframe
        if fuzz.token_sort_ratio(player_name, row["MLBNAME"]) > 75:
            matching_df = matching_df.append(row)
    if (len(matching_df)) == 0:
        print("There were no matches")
    else:
        for a in range(0, len(matching_df)):
            print(str(a+1) + "-" + str(matching_df['MLBNAME'].iloc[a]) + 
            ", " + str(matching_df['BIRTHDATE'].iloc[a])  + 
            ", " + str(matching_df['POS'].iloc[a])) 
        selection = int(input("Enter the number for your selection: "))
        matching_df = matching_df.iloc[[selection-1]]
    
    print("Your selection: ")
    print(str(matching_df['MLBNAME'].iloc[0]) + 
            ", " + str(matching_df['BIRTHDATE'].iloc[0])  + 
            ", " + str(matching_df['POS'].iloc[0]))
    test = input("Do you want to change the player? (y/n)")
    if (test.lower() == "n"):
        exect = False


    
    """
is_last_pitch_str = input("Is last pitch (True/False)? ")

is_last_pitch = is_last_pitch_str.lower() == "true"
flag = "is...last...pitch|" if is_last_pitch else ""
url = f"https://baseballsavant.mlb.com/statcast_search?hfPTM=&hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea={season}%7C&hfSit=&player_type=pitcher&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_date}&game_date_lt={end_date}&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag={flag}&pitchers_lookup%5B%5D={player_id}&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&type=details&player_id={player_id}"
r = requests.get(url, allow_redirects=True, timeout=100)
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

pitches = ['EP', 'CU', 'CH', 'SI', 'SL', 'FF', 'FA', 'FC',
           'KC', 'FS', 'CS', 'PO', 'IN', 'SC']
pitch = input("Enter pitch  type: ")
if pitch.upper() in pitches:
    found = df.index[df['Pitch'] == pitch.upper()].tolist()
    df2 = df.loc[df['Pitch'] == pitch.upper()]
    result = [matches[i] for i in found]
else:
    pitch = ""
    found = df.index.tolist()
    df2 = df
    result = [matches[i] for i in found]


down = input("Do you want to download the pitches? (y/n): ")

if (down.lower() == 'y'):
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

url_feed = "https://baseballsavant.mlb.com/feed"
query_params = {
    "warehouse": "True",
    "hfPTM": pitch + "|",
    "hfAB": "",
    "hfGT": "",
    "hfPR": "",
    "hfZ": "",
    "hfStadium": "",
    "hfBBL": "",
    "hfNewZones": "",
    "hfPull": "",
    "hfC": "",
    "hfSea": season + "|",
    "hfSit": "",
    "player_type": "pitcher",
    "hfOuts": "",
    "hfOpponent": "",
    "pitcher_throws": "",
    "batter_stands": "",
    "hfSA": "",
    "game_date_gt": start_date,
    "game_date_lt": end_date,
    "hfMo": "",
    "hfTeam": "",
    "home_road": "",
    "hfRO": "",
    "position": "",
    "hfInfield": "",
    "hfOutfield": "",
    "hfInn": "",
    "hfBBT": "",
    "hfFlag": "",
    "pitchers_lookup[]": player_id,
    "metric_1": "",
    "group_by": "name",
    "min_pitches": "",
    "min_results": "",
    "min_pas": "",
    "sort_col": "pitches",
    "player_event_sort": "api_p_release_speed",
    "sort_order": "desc",
    "type": "details",
    "player_id": player_id
}

url2 = urljoin(url_feed, "?" + urlencode(query_params))

print(url_feed)
print(url2)

with requests.get(url_feed, params=query_params, timeout=100) as r:
    r.raise_for_status()
    response = r.json()

save_to_file("player", response)
"""