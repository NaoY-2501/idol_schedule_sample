import logging

import utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, lambda_context):
    api = utils.get_twitter_api()

    logger.info('Start to tweet streaming urls')

    msg = ('#オサカナ の楽曲は音楽ストリーミングサービスで配信中です！\n'
           'お昼のBGMにオサカナを聴いてみませんか？\n')

    for streaming_info in utils.STREAMING_URLS:
        service = streaming_info['service']
        url = streaming_info['url']
        msg += f'{service}: {url}\n'

    api.update_status(msg=msg)
    logger.info('Tweet Succeed')
