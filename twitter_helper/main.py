import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from tabulate import tabulate
import click
import joblib
import tweepy

# get path to project root
PROJECT_ROOT = Path(__file__).parent.parent

memory = joblib.Memory(location=PROJECT_ROOT / ".cache")


@click.group()
def main():
    # init dotenv
    from dotenv import load_dotenv

    load_dotenv()


@main.command()
def info():
    """Prints info about the current user"""
    try:
        print_info()
    except tweepy.errors.TooManyRequests:
        check_limits()
        raise


@main.command()
def limits():
    """Checks rate limits"""
    check_limits()


def check_limits():
    limits_used = False
    api = get_api()
    status = api.rate_limit_status()
    # print(status["resources"]["users"].keys())
    for group in status["resources"].values():
        for endpoint in group.keys():
            remaining = group[endpoint]["remaining"]
            limit = group[endpoint]["limit"]
            if remaining != limit:
                # timestamp of when rate limit resets
                reset_dt = datetime.fromtimestamp(group[endpoint]["reset"])

                now = datetime.now()
                delta = reset_dt - now
                print(
                    f"{endpoint}: {remaining}/{limit}   (resets in {round(delta.total_seconds(), 1)})"
                )
                limits_used = True
    if not limits_used:
        print("No rate limits active")


@main.command()
def creeps():
    """List creeps"""
    creeps = get_creep_following()
    print(tabulate(creeps, headers=["User"]))


@main.command()
def users_by_likes():
    """List users, sorted by number of your likes"""
    likes_per_user = get_most_engaged()
    likes_per_user = dict(
        sorted(likes_per_user.items(), key=lambda x: x[1], reverse=True)
    )
    # for user, likes in sorted(likes_per_user.items(), key=lambda x: x[1], reverse=True):
    #     print(f"{user}: {likes}")
    print(
        tabulate(
            likes_per_user.items(),
            headers=["User", "Likes"],
        )
    )


def print_info():
    """Print a bunch of useful info/summary stats"""
    api = get_api()
    user = api.verify_credentials()
    print(f"{user.screen_name}")
    print(f"{user.followers_count} followers")
    print(f"{user.friends_count} following")
    print(f"{user.statuses_count} tweets")
    print(f"{user.favourites_count} likes")
    print(f"{user.listed_count} lists")
    print(f"On Twitter since {user.created_at}")

    # Slow/rate limit exceeded
    # print(f"{len(get_friends())} mutuals")


def get_auth():
    assert all(
        key in os.environ
        for key in [
            "CONSUMER_KEY",
            "CONSUMER_SECRET",
            "ACCESS_TOKEN",
            "ACCESS_TOKEN_SECRET",
        ]
    ), "API keys not set in the environment, read the README!"
    # read keys from env vars
    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

    return tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )


def get_api() -> tweepy.API:
    auth = get_auth()
    return tweepy.API(auth)


@memory.cache
def get_creep_following():
    """
    List users who have:
     - not followed back
     - not had any (recent) tweets liked by you
    """
    api = get_api()
    following = set(get_followers())
    liked_by_you = set(get_likes())

    creeps = []
    for user in tweepy.Cursor(api.get_friends, count=10).items():
        if user.screen_name not in following:
            creeps.append(user.screen_name)

    return creeps


@memory.cache
def get_following() -> set[str]:
    """
    Return a list of all users you are following ("friends" in Twitter terms).
    """
    api = get_api()
    following = set()
    for user in tweepy.Cursor(api.get_friends).items():
        following |= {user.screen_name}

    return following


@memory.cache
def get_followers() -> set[str]:
    """
    Return a list of all users who follow you.
    """
    api = get_api()
    followers = set()
    for user in tweepy.Cursor(api.get_followers).items():
        followers |= {user.screen_name}

    return followers


def get_mutuals() -> set[str]:
    """
    Return a list of all users who you follow and who follow you back.
    """
    api = get_api()
    return get_followers() & get_following()


def get_most_engaged() -> dict:
    """
    List users, sorted by number of likes each user has received
    """
    likes_per_user: dict[str, int] = defaultdict(int)
    for like in get_likes():
        likes_per_user[like.user.screen_name] += 1
    return likes_per_user


def test_get_most_engaged():
    most_engaged = get_most_engaged()
    assert most_engaged


@memory.cache
def get_likes(limit: int = 4000):
    """
    Get all likes by a user
    """
    api = get_api()
    likes = []

    # fetch likes in batches of 200
    batch_size = 200 if limit < 200 else limit
    for like in tweepy.Cursor(api.get_favorites, count=batch_size).items():
        likes.append(like)
        if len(likes) >= limit:
            break

    assert len(likes) <= limit
    print(f"Retrieved {len(likes)} likes")
    return likes


def test_get_likes():
    likes = get_likes(limit=10)
    assert likes


if __name__ == "__main__":
    main()
