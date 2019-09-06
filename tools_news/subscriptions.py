import requests
from functools import partial


def init_updates_fetcher(db):
    subscribed_services = db['subscribed_services']
    services = {
        'github': partial(fetch_github, db=subscribed_services),
        'dockerhub': partial(fetch_dockerhub, db=subscribed_services)
    }
    return services


def fetch_github(name, db):
    response = requests.get(f'https://api.github.com/repos/{name}/git/refs/tags', timeout=15)
    releases = response.json()

    if not releases:
        return []

    if isinstance(releases, dict) and 'Not Found' in releases.values():
        return [f"Project {name} doesn't exists on GitHub or it doesn't have tags."]

    releases = list(map(lambda x: x['ref'].split('/')[-1], releases))

    service = db.find_one({'name': name})
    if not service:
        db.insert_one({'name': name, 'host': 'github', 'releases': releases})
        return releases

    db.replace_one({'name': name}, {'name': name, 'host': 'github', 'releases': releases})

    updates = list(set(releases) - set(service['releases']))
    return updates


def fetch_dockerhub(name, db):
    response = requests.get(f'https://registry.hub.docker.com/v1/repositories/{name}/tags', timeout=5)

    releases = response.json()
    if "Resource not found" == releases:
        return []

    releases = [release['name'] for release in releases]

    service = db.find_one({'name': name})
    if not service:
        db.insert_one({'name': name, 'host': 'dockerhub', 'releases': releases})
        return releases

    db.replace_one({'name': name}, {'name': name, 'host': 'dockerhub', 'releases': releases})

    updates = list(set(releases) - set(service['releases']))
    return updates
