from datetime import datetime
import logging
import time

import requests
from dateutil.relativedelta import relativedelta

import utils


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, lambda_context):

    api = utils.get_twitter_api()

    today = datetime.today()
    time_max = datetime(today.year, today.month, today.day, 23, 59, 59) + relativedelta(days=6)
    time_min = datetime(today.year, today.month, today.day, 0, 0, 0)

    payload = {
        'maxResults': 50,
        'order_by': 'startTime',
        'timeMax': time_max.strftime('%Y-%m-%dT23:59:59Z'),
        'timeMin': time_min.strftime('%Y-%m-%dT00:00:00Z'),
        'singleEvents': True,
        'key': utils.GOOGLE_APIKEY,
    }

    logger.info('Start to fetch events at %s .', today.strftime('%Y-%m-%d'))

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
        link = event['htmlLink']
        if date < time_max and utils.is_live(summary) or utils.is_event_schedule(summary):
            target_events.append({
                'summary': summary,
                'link': link,
                'date': event['start']['date'].replace('-', '/')
            })

    logger.info('%s events within %s to %s',
                len(target_events),
                time_min.strftime('%Y-%m-%d'),
                time_max.strftime('%Y-%m-%d')
                )
    logger.info('Start to tweet events info')

    if target_events:
        for event in sorted(target_events, key=lambda x: x['date']):
            summary = event['summary']
            link = event['link']
            date = event['date']
            msg = f'【今週の #オサカナ 】{date}  {summary} ({link})'
            api.update_status(status=msg)
            logger.info('[%s] was tweeted', summary)
            time.sleep(3)

    logger.info('Tweet succeed')
