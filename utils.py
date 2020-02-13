from datetime import datetime
import random

import tweepy

GOOGLE_APIKEY = 'YOUR_GOOGLE_APIKEY'

CAL_ID = 'YOUR_OSHI_CALENDAR_ID'
URL = f'https://www.googleapis.com/calendar/v3/calendars/{CAL_ID}/events'

# Twitter API
CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_TOKEN_SECRET'


YOUTUBE_PREFIX = 'https://www.youtube.com/watch?v='

MV_IDS = (
    # Youtubeの動画ID
)

STREAMING_URLS = (
    {
        'service': 'Amazon Music',
        'url': 'https://music.amazon.co.jp/artists/',
    },
    {
        'service': 'Apple Music',
        'url': 'https://music.apple.com/jp/artist/',
    },
    {
        'service': 'Spotify',
        'url': 'https://open.spotify.com/artist/',

    },
    {
        'service': 'YouTube Music',
        'url': 'https://music.youtube.com/channel/'

    },
)


def get_mv() -> str:
    mv_id = random.choice(MV_IDS)
    return YOUTUBE_PREFIX + mv_id


def is_live(summary: str) -> bool:
    """予定のsummaryからライブであるか判定"""
    if '【イベント出演】' in summary or '【定期公演】' in summary\
            or '【リリイベ】' in summary or '【主催ライブ】' in summary\
            or '【2マン】' in summary:
        return True
    return False


def get_twitter_api():
    """Twitter APIのインスタンス取得"""
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def to_datetime(dt: str) -> datetime:
    """datetime型に変換"""
    return datetime.strptime(dt, '%Y-%m-%d')


def is_event_schedule(summary: str) -> bool:
    """予定のsummaryからライブ予定であるか判定"""
    return 'ライブ予定' in summary
