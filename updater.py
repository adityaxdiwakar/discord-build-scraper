from dotenv import load_dotenv
load_dotenv(verbose=True)

import requests as r
import re, time, os

# defining channels to iterate over
channels = ['canary', 'ptb', 'stable']


def fetcher(channel):
    try:
        if channel == 'stable':  # deferring since stable.discordapp.com does not exist
            # getting the app information for stable
            discreq = r.get(f"https://discordapp.com/app")
        else:
            # getting the app information for all channels except stable
            discreq = r.get(f"https://{channel}.discordapp.com/app")
    except:
        exit()

    # receiving latest updated information to check for similarities
    persreq = r.get(f"http://localhost:1337/discord/{channel}/builds/latest")

    # has the build id changed since last time? if not, the function is done
    if discreq.headers['X-Build-ID'] == persreq.json()['build_id']:
        return 1338

    # regex to find all js asset files
    regex = re.compile('([a-zA-z0-9]+)\.js', re.I)
    # getting the last file, this contains hash/build
    asset_file = regex.findall(discreq.text)[-1]

    if channel == 'stable':  # deferring since stable.discordapp.com does not exist
        # getting the asset file for stable
        assetreq = r.get(f'https://discordapp.com/assets/{asset_file}.js')
    else:
        # getting the asset file for canary/ptb
        assetreq = r.get(f'https://{channel}.discordapp.com/assets/{asset_file}.js')

    try:
        # regex to find the build string collection
        regex = re.compile('Build Number: [0-9]+, Version Hash: [A-Za-z0-9]+')
        build_strings = regex.findall(assetreq.text)[0].replace(' ', '').split(
            ',')  # regex to remove all whitespace and get num/hash (unformatted)
    except:
        print("Shit's fucked")
        return 1339

    # splits off the : and gets the last index (build number)
    build_num = build_strings[0].split(':')[-1]
    # split off the : and gets the last index (build hash)
    build_hash = build_strings[1].split(':')[-1]
    # first 9 characters is equivelant to the build ID (also the header above)
    build_id = build_hash[:7]

    r.post(f"http://localhost:1337/discord/{channel}/builds", data={
        "build_num": build_num,
        "build_hash": build_hash,
        "build_id": build_id,
        "secret": os.getenv("API_TOKEN"),
        "build_time": time.time()
    })  # posts to the API (done locally) to update listing records, uses secret for privacy

def run_update():
    for channel in channels:
        fetcher(channel)

starttime = time.time()
def update_handler():
    while True:
        run_update()
        time.sleep(37 - ((time.time() - starttime) % 37))

update_handler()