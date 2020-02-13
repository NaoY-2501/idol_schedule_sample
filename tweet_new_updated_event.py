from datetime import datetime, timedelta
import logging
import time

import requests
from dateutil.relativedelta import relativedelta

import utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def is_new_event(created: str, time_min: datetime) -> bool:
    offset = time_min - datetime.strptime(created[:-5], '%Y-%m-%dT%H:%M:%S')
    return offset < timedelta(minutes=30)


def is_update_event(updated: str, time_min: datetime) -> bool:
    offset = time_min - datetime.strptime(updated[:-5], '%Y-%m-%dT%H:%M:%S')
    return offset < timedelta(minutes=30)


def lambda_handler(event, lambda_context):
    api = utils.get_twitter_api()
    now = datetime.today()
    time_max = datetime(now.year, now.month, now.day, 23, 59, 59) + relativedelta(months=3)
    time_min = datetime(now.year, now.month, now.day, now.hour, now.minute, 0)

    logger.info('Start to osakana_new_updated_events %s', time_min)

    payload = {
        'maxResults': 50,
        'order_by': 'startTime',
        'timeMax': time_max.strftime('%Y-%m-%dT23:59:59Z'),
        'timeMin': time_min.strftime('%Y-%m-%dT%H:%M:00Z'),
        'singleEvents': True,
        'key': utils.GOOGLE_APIKEY,
    }

    logger.info('Start to fetch events at %s .', now.strftime('%Y-%m-%d'))

    r = requests.get(utils.URL, params=payload)

    res = r.json()

    try:
        events = res['items']
        logger.info('Fetching events succeed.')
    except KeyError:
        logger.error('Fetching events failed.')
        raise KeyError

    target_events = []
    for event in events:
        date = utils.to_datetime(event['start']['date'])
        summary = event['summary']
        if date < time_max and (utils.is_live(summary) or utils.is_event_schedule(summary)):
            target_events.append({
                'summary': summary,
                'link': event['htmlLink'],
                'created': event['created'],
                'updated': event['updated'],
                'date': event['start']['date'],
            })

    logger.info('Fetch %s events', len(target_events))

    new_events = []
    updated_events = []
    for event in target_events:
        if is_new_event(event['created'], time_min):
            new_events.append(event)
            continue
        if is_update_event(event['updated'], time_min):
            updated_events.append(event)

    logger.info('%s new events', len(new_events))
    logger.info('Start to tweet new events info')
    if new_events:
        # イベント日時の昇順
        for event in sorted(new_events, key=lambda x: x['date']):
            date = event['date'].replace('-', '/')
            summary = event['summary']
            link = event['link']
            msg = f'【イベント追加！】{date} {summary} ({link})'
            api.update_status(status=msg)
            logger.info('%s %s was tweeted', date, event['summary'])
            time.sleep(2)

    logger.info('%s new events', len(updated_events))
    logger.info('Start to tweet updated events info')
    if updated_events:
        # イベント日時の昇順
        for event in sorted(updated_events, key=lambda x: x['date']):
            date = event['date'].replace('-', '/')
            summary = event['summary']
            link = event['link']
            msg = f'【イベント情報更新！】{date} {summary} ({link})'
            api.update_status(status=msg)
            logger.info('%s %s was tweeted', date, event['summary'])
            time.sleep(2)

    logger.info('Tweet succeed')
