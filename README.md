twitter-helper
==============

Some code to try out stuff with the Twitter API.

Intended features:

 - List most engaged with users
 - Find "creeps", or people you're following but not interacting with (no likes, replies, retweets).
   - Can be used to help clean up who you're following.

## Getting started

First, you need to obtain API keys from Twitter, you can read about how to do so here: https://docs.tweepy.org/en/stable/authentication.html#oauth-1-0a-user-context

Then, copy `.env.example` to `.env` and fill it out with the API credentials.

Then install with:

```sh
pip install -e .
# or...
poetry install
```

## Usage

```
$ twitter-helper --help
Usage: twitter-helper [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  creeps          List creeps
  info            Prints info about the current user
  limits          Checks rate limits
  users-by-likes  List users, sorted by number of your likes
```

Note: If you are using poetry, you either need to first activate the venv with `poetry shell` or by prefixing with `poetry run`, as in: `poetry run twitter-helper --help`

## Limitations

The Twitter API has pretty strict rate limits that make it difficult to work with the data.

To make things easier in the future, there's a need for some form of smart caching/incremental download of tweets/likes/accounts.

## Links

You may also be interested in [chatalysis](https://github.com/ErikBjare/chatalysis), which does similar things but for (group)chats.
