### Getting videos from Baseball Savant ###
import requests
import urllib.request
import re
import os
import wget
import youtube_dl
import glob
import shutil

def find_video_links(webpageHTML):
    expression = r'"(/sporty-v.*?)" target'
    return re.findall(expression, webpageHTML)

def download_video(url, name):
    url2=f"https://baseballsavant.mlb.com{url}"
    #command = f"youtube-dl https://baseballsavant.mlb.com{url} -o {name}.mp4"
    #os.system(command)
    #urllib.request.urlretrieve(url2,dest)
    #filename = wget.download(url)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url2])

# Downloads the list of given URLs with youtbe-dl
def download_all_matches(matches):
    i = 1
    for match in matches:
        print(f"Downloading video {i} of {len(matches)} with url: https://baseballsavant.mlb.com{match}")
        download_video(match, i)
        i += 1

def rename(directory):
    os.chdir(directory)
    num = 1
    for file in [file for file in sorted(os.listdir(), key=os.path.getctime, reverse=True) if os.path.splitext(file)[1] == ".mp4"]:
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
#url = f"https://baseballsavant.mlb.com/statcast_search?hfPTM=&hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2022%7C&hfSit=&player_type=pitcher&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2022-05-01&game_date_lt=2022-05-15&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=&pitchers_lookup%5B%5D=605400&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&type=details&player_id=605400"
r = requests.get(url, allow_redirects=True)
#open('site.txt', 'wb').write(r.content)
#with urllib.request.urlopen(url) as response:
#    html = response.read().decode()
html = r.content
open('site.txt', 'wb').write(html)

with open('site.txt') as f:
    lines = f.read()

matches = find_video_links(lines)
# open file in write mode
with open(r'links.txt', 'w') as fp:
    for item in matches:
        # write each item on a new line
        fp.write("%s\n" % item)

if len(matches) <= 1:
    print("ERROR, 0 matches found in request")
    #cleanup_leftover_files()
    exit()

download_all_matches(matches)
rename(os.getcwd())

src_folder = os.getcwd()
dst_folder = os.getcwd() + "/videos/"

try: 
    os.mkdir(dst_folder) 
except OSError as error: 
    print("Directory 'videos' already exists") 


# Search files with .mp4 extension in source directory
pattern = "\*.mp4"
files = glob.glob(src_folder + pattern)

# move the files with mp4 extension
for file in files:
    # extract file name form file path
    file_name = os.path.basename(file)
    shutil.move(file, dst_folder + file_name)
    print('Moved:', file)

### TESTING GIT