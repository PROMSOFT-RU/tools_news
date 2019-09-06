import requests
from mattermostdriver import Driver


def init_mattermost(config):
    mm = Driver({
        'url': config['host'],
        'port': int(config['port']),
        'token': config['token'],
        'scheme': config['scheme']
    })
    bot_data = mm.login()
    bot_id = bot_data['id']

    def send_updates_to_subscribers(mailing_list):
        usernames = list(mailing_list.keys())

        for user, message in zip(mm.users.get_users_by_usernames(usernames), mailing_list.values()):
            user_dm_id = mm.channels.create_direct_message_channel([
                bot_id, user['id']
            ])['id']

            mm.posts.create_post({
                'channel_id': user_dm_id,
                # because mattermost API has restrictions on message size
                'message': message[:16000]
            })

    return send_updates_to_subscribers


def update_bot_status(config, message):
    mm = Driver({
        'url': config['host'],
        'port': int(config['port']),
        'token': config['token'],
        'scheme': config['scheme']
    })
    bot_data = mm.login()
    bot_id = bot_data['id']
    bot_name = bot_data['first_name']

    requests.put(
        f'{config["scheme"]}://{config["host"]}:{config["port"]}/api/v4/bots/{bot_id}',
        json={'username': bot_name,
              'description': message
              },
        headers={'Authorization': 'Bearer ' + config['token']},
        verify=True
    )
