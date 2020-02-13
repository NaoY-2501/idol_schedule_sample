from datetime import datetime
import logging
import time

import requests

import utils


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def is_not_release_event(summaries):
    for summary in summaries:
        if '【リリイベ】' in summary:
            return False
    return True


def lambda_handler(event, lambda_context):

    api = utils.get_twitter_api()

    today = datetime.today()
    time_max = datetime(today.year, today.month, today.day, 23, 59, 59)
    time_min = datetime(today.year, today.month, today.day, 0, 0, 0)

    payload = {
        'maxResults': 5,
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
        if date < time_max and utils.is_live(summary):
            target_events.append({
                'summary': summary,
                'link': link,
            })

    logger.info('%s events in %s', len(target_events), today.strftime('%Y-%m-%d'))
    logger.info('Start to tweet events info')

    date = today.strftime('%Y/%m/%d')
    if target_events:
        summaries = []
        for event in sorted(target_events, key=lambda x: x['summary']):
            summary = event['summary']
            link = event['link']
            msg = f'【{date}の #オサカナ 】  {summary} ({link})'
            api.update_status(status=msg)
            logger.info('[%s] was tweeted', summary)
            summaries.append(summary)
            time.sleep(5)
        if is_not_release_event(summaries):
            msg = ('#オサカナ 特典会レギュレーション\n'
                   '特典券1枚: 全員握手\n'
                   '特典券2枚: 2ショットチェキ+サイン\n'
                   '特典券3枚: 4ショットチェキ+サイン\n'
                   '特典券はグッズ購入でもらえます。詳しくは物販でご確認ください！')
            api.update_status(status=msg)
    else:
        mv_url = utils.get_mv()
        msg = f'【{date}の #オサカナ 】 イベントはありません。オサカナの映像を観て気持ちを高めよう！{mv_url}'
        api.update_status(status=msg)
        logger.info('MV URL(%s) was tweeted', mv_url)

    logger.info('Tweet succeed')
