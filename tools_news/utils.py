def get_subscribed_services(config):
    subscriptions = dict()

    for services in config.values():
        for name, repos in services.items():
            if name not in subscriptions:
                subscriptions[name] = set()
            subscriptions[name].update(repos)

    for key, values in subscriptions.items():
        subscriptions[key] = {name: [] for name in values}

    return subscriptions


def create_text_from_updates(service_name, service_updates):
    if not service_updates:
        return ""

    lines = [f"**{service_name}**"]

    for update in service_updates:
        lines.append(f"- {update}")
    lines.append('\n')

    return '\n'.join(lines)
