import httpx
import asyncio
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from .RawConfigParser import RawConfigParser

'''
Currently aims to retrieve the tweets of the users in the usernames.txt file.
As of now, it plans to retrieve elon musk, donald trump
# TODO: Remove the nextToken from data log, as it is sensitive
# TODO: Listen to user tweets realtime
# TODO: (Tentative, may not implement if realtime preferred) Specify the rate limit for the API / Use pagination
# Refer to: https://developer.twitter.com/en/docs/twitter-api/pagination
'''

class TwitterUser:
    def __init__(self, bearer_token: str, config: RawConfigParser, logger: logging.Logger):
        self.bearer_token = bearer_token
        self.config = config
        self.logger = logger

    async def main(self) -> None:
        # Retrieve the user IDs
        users_url = self.create_users_url()
        users_params = self.get_users_params()
        users_response = await self.connect_to_endpoint(users_url, users_params)

        # Separate successful and errorneous user IDs 
        users_id = {}
        for item in users_response["data"]:
            users_id[item["id"]] = item

        error_data = {}
        for item in users_response["errors"]:
            error_data[item.get("resource_id", "Unknown")] = item
        
        self.logger.info(f"users_id = {json.dumps(users_id, sort_keys=True)}")
        self.logger.info(f"error_data = {json.dumps(error_data, sort_keys=True)}")
        
        # Retrieve the tweets for each successful user ID
        for user_id in users_id:
            tweets_url = self.create_tweets_url(user_id)
            tweets_params = self.get_tweets_params()

            tweets_response = await self.connect_to_endpoint(tweets_url, tweets_params)
            self.logger.info(f"tweets_response = {json.dumps(tweets_response, sort_keys=True)}")

    # Handles Twitter authetification and the connection to Twitter's Streaming API
    def bearer_oauth(self, r: httpx.AsyncClient) -> httpx.AsyncClient:
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2UserLookupPython"
        return r

    async def connect_to_endpoint(self, url: str, params: dict) -> dict:
        """
        Connects to the endpoint and returns the response.
        """
        session = httpx.AsyncClient(timeout=30)

        response = await session.request("GET", url, auth=self.bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(f"Request returned an error: {response.status_code} {response.text}")

        await session.aclose()
        return response.json()


    # Handles the API URLs and parameters for users
    def get_users_params(self) -> dict:
        userfields_section = self.config["USERFIELDS"]
        userfields = [key for key in userfields_section if userfields_section[key] == "True"]
        return {"user.fields": ",".join(userfields)}

    def create_users_url(self) -> str:
        with open(self.config["DEFAULT"]["usernames_file"]) as f:
            usernames = f.read().splitlines()
        return self.config["LINKS"]["twitter_user_link"].format(",".join(usernames))


    # Handles the API URLs and parameters for tweets
    def get_tweets_params(self) -> dict:
        tweetfields_section = self.config["TWEETFIELDS"]
        tweetsfields = [key for key in tweetfields_section if tweetfields_section[key] == "True"]
        return {"tweet.fields": ",".join(tweetsfields), "max_results":5}

    def create_tweets_url(self, user_id) -> str:
        return self.config["LINKS"]["twitter_user_tweets_link"].format(user_id)
    

if __name__ == "__main__":
    # Initialize logging, config and environment variables
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s]:%(levelname)5s:%(message)s')
    
    config = RawConfigParser()
    config.read("config.ini")

    load_dotenv()
    try:
        bearer_token = os.environ["Bearer_Token"]
    except KeyError:
        logging.critical("Bearer Token not found in environment!")

    # Initialize services
    logger_file_handler = RotatingFileHandler(
        config["DEFAULT"]["user_tweet_log_file"],
        mode='a',
        maxBytes=1024 * 1024,
        backupCount=100,
        encoding="utf8",
    )
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)

    twitter_user = TwitterUser(bearer_token, config, logger)
    asyncio.run(twitter_user.main())