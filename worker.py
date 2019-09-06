import os
import yaml
import logging
import logging.config
import sentry_sdk
from datetime import datetime
from envparse import env
from pymongo import MongoClient

from tools_news.utils import get_subscribed_services, create_text_from_updates
from tools_news.mattermost import init_mattermost, update_bot_status
from tools_news.subscriptions import init_updates_fetcher

_LOGGER = logging.getLogger(__name__)


def load_config(path):
    config = dict()

    with open(os.path.join(path, 'tools_news.yaml')) as f:
        config['subscribers'] = yaml.safe_load(f)

    with open(os.path.join(path, 'logging.yaml')) as f:
        config['logging'] = yaml.safe_load(f)

    config['logging']['DSN'] = env('DSN', '')

    env.read_envfile()
    config['mongo'] = dict()
    config['mongo']['connection_string'] = env('MONGO_CONNECTION_STRING')

    config['mattermost'] = dict()
    config['mattermost']['host'] = env('MATTERMOST_HOST')
    config['mattermost']['port'] = env('MATTERMOST_PORT')
    config['mattermost']['token'] = env('MATTERMOST_TOKEN')
    config['mattermost']['scheme'] = env('MATTERMOST_SCHEME')

    return config


def init_db(connect_string):
    client = MongoClient(connect_string['connection_string'])
    db = client['tools_news']

    return db


def init_logging(config):
    logging.config.dictConfig(config['logging'])

    dsn = config.get('logging', {}).get('DSN')
    if dsn:
        sentry_sdk.init(dsn=dsn)


def run():
    config = load_config('./config')

    init_logging(config['logging'])

    db = init_db(config['mongo'])

    fetch_updates = init_updates_fetcher(db)

    services_updates = get_subscribed_services(config['subscribers'])

    for host, services in services_updates.items():
        for service in services:
            services_updates[host][service] = fetch_updates[host](service)

    mailing_list = dict()
    for subscriber, subscriptions in config['subscribers'].items():
        for host, services in subscriptions.items():
            message = ''.join([create_text_from_updates(service, services_updates[host][service]) for service in services])
            if len(message.replace("\n", "")) == 0:
                continue
            mailing_list[subscriber] = message

    if mailing_list:
        mm = init_mattermost(config['mattermost'])
        mm(mailing_list)

    update_bot_status(config['mattermost'], datetime.strftime(datetime.now(), '%A, %-d %b %H:%M'))


if __name__ == '__main__':
    run()
