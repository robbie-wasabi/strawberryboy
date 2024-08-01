import tweepy
import json
import time
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Initialize Tweepy client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)


def check_auth():
    try:
        me = client.get_me()
        print(f"Authentication successful. Logged in as: {me.data.username}")
        return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return False


def fetch_all_tweets(username):
    try:
        user = client.get_user(username=username)
        user_id = user.data.id

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{username}_tweets_{timestamp}.json"

        tweet_count = 0
        pagination_token = None

        while True:
            try:
                response = client.get_users_tweets(
                    user_id,
                    tweet_fields=["created_at", "text"],
                    max_results=100,
                    pagination_token=pagination_token,
                )

                if not response.data:
                    break

                with open(file_name, "a") as file:
                    for tweet in response.data:
                        json.dump(tweet.data, file)
                        file.write("\n")
                        tweet_count += 1

                print(f"Batch saved. Total tweets: {tweet_count}")

                if "next_token" not in response.meta:
                    break

                pagination_token = response.meta["next_token"]
                time.sleep(1)  # Respect rate limits

            except tweepy.TooManyRequests:
                print("Rate limit exceeded. Waiting 15 minutes...")
                time.sleep(900)  # 15 minutes
            except Exception as e:
                print(f"An error occurred while fetching tweets: {str(e)}")
                return False, tweet_count, file_name

        return True, tweet_count, file_name

    except tweepy.errors.Forbidden as e:
        print(f"Authentication Error: {str(e)}")
        print("Error details:", e.api_errors)
    except tweepy.errors.NotFound:
        print(f"User @{username} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return False, 0, None


def main():
    if not check_auth():
        print("Please check your API credentials and permissions.")
        return

    # username = input("Enter the username of the Twitter account: ")
    username = "iruletheworldmo"
    success, tweet_count, file_name = fetch_all_tweets(username)

    if success:
        print(
            f"All {tweet_count} tweets from @{username} have been downloaded and saved to {file_name}"
        )
    else:
        if tweet_count > 0:
            print(
                f"Tweet fetching was incomplete. {tweet_count} tweets were saved to {file_name}"
            )
        else:
            print("No tweets were fetched. Please check the error messages above.")


if __name__ == "__main__":
    main()
