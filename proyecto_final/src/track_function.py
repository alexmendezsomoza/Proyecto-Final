
import pandas as pd
import tweepy

def track(user, number_tweets):
    # 4 authentication chains

    consumer_key = 'jQTzrkE7vlZbg2ntJu4LESCZs'
    consumer_secret = 'AS4B8YLOWXMcrHjJyZ8stWcm9Cp2qh0rCdIjiWaPBaTTc22tnO'
    access_key = '902474996-b1ltSFx5Y2EdJfi2s63pghsULdjLTF1lkW6oHBvj'
    access_secret = 'TrZr5nGmi2Q4RcAJJ3UHbwuWkAqjcNXOTfCHLm1eOzpnn'

    # authorize twitter, initialize tweepy

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # Parameters
    searchQuery = user
    retweet_filter = '-filter:retweets'
    q = searchQuery + retweet_filter

    # Lists

    created_at = []
    id_tweet = []
    full_text = []
    source = []
    in_reply_to_status_id = []
    in_reply_to_screen_name = []
    user_name = []
    user_screen_name = []
    user_location = []
    user_url = []
    user_followers_count = []
    user_verified = []
    user = []  # single-use

    for tweet in tweepy.Cursor(api.search, q, tweet_mode='extended').items(number_tweets):
        # List Append
        created_at.append(tweet.created_at)
        id_tweet.append(int(tweet.id_str))
        full_text.append(tweet.full_text)
        source.append(tweet.source)
        in_reply_to_status_id.append(tweet.in_reply_to_status_id)
        in_reply_to_screen_name.append(tweet.in_reply_to_screen_name)
        user.append(tweet.user)

    for i in user:
        user_name.append(i.name)
        user_screen_name.append(i.screen_name)
        user_location.append(i.location)
        user_url.append('https://twitter.com/' + i.screen_name)
        user_followers_count.append(i.followers_count)
        user_verified.append(i.verified)

    df = pd.DataFrame({'date': created_at, 'tweet_id': id_tweet, 'tweet_text': full_text, 'source': source,
                       'in_reply_to_screen_name': in_reply_to_screen_name,
                       'user_name': user_name, 'user_screen_name': user_screen_name, 'location': user_location,
                       'user_url': user_url, 'n_followers': user_followers_count, 'verified': user_verified})

    return df