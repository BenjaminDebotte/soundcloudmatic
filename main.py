import youtube_dl
import requests
import json
import logging

#######################

CLIENT_ID_TOKEN = "egDzE3xmafwb5ki9VMXAstPEmrdBItZq"
TARGET_USER_ID = "408014859"
TARGET_URL = f"https://api-v2.soundcloud.com/users/{TARGET_USER_ID}/track_likes?client_id={CLIENT_ID_TOKEN}"

YDL_FORMAT="%(uploader)s - %(title)s.%(ext)s"

#######################

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

ydl = youtube_dl.YoutubeDL({"outtmpl": YDL_FORMAT})


def fix_url(url):
    if not CLIENT_ID_TOKEN in url:
        url = f"{url}&client_id={CLIENT_ID_TOKEN}"
    if "limit=10" in url:
        url = url.replace("limit=10", "limit=200")
    return url

def retrieve_infos():

    def _retrieve_infos(sc_url):
        logging.info(sc_url)

        response = requests.get(sc_url)

        if not response.ok:
            response.raise_for_status()

        data = response.json()

        if not 'next_href' in data or data['next_href'] is None:
            return None, []

        next_url = data['next_href']
        collection = data['collection']

        tracks = list(map(lambda c : c['track'], collection))

        return fix_url(next_url), tracks

    TRACKS = []
    next_url, tracks = _retrieve_infos(TARGET_URL)

    TRACKS += tracks

    try:
        while(next_url is not None):
            next_url, tracks = _retrieve_infos(next_url)
            TRACKS += tracks
    except Exception as e:
        logging.exception(e)
    finally:
        return TRACKS

tracks = retrieve_infos()
logging.info(f"Retrieved {len(tracks)} tracks. Starting download.")

urls = list(map(lambda i: i['permalink_url'], tracks))

ydl.download(urls)

logging.info("Finished downloading.")
