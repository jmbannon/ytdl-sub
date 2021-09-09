
from ytdl_subscribe.parse import parse_subscriptions



if __name__ == "__main__":
    # execute only if run as a script
    subscriptions = parse_subscriptions('subscriptions.yaml')
    for s in subscriptions:
        s.extract_info()
    print('hey')
