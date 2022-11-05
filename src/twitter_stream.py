import httpx
import asyncio
import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from .RawConfigParser import RawConfigParser

'''
Currently aims to retrieve realtime streams of tweets related to twitter's recent layoffs.
# TODO: Add support for other topics
'''

class TwitterStream:
    def __init__(self, bearer_token: str, config: RawConfigParser, logger: logging.Logger):
        self.bearer_token = bearer_token
        self.config = config
        self.logger = logger
    
    async def main(self) -> None:
        rules = await self.get_rules()
        delete = await self.delete_all_rules(rules)
        set = await self.set_rules(delete)
        await self.get_stream(set)

    def bearer_oauth(self, r: httpx.AsyncClient) -> httpx.AsyncClient:
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r


    async def get_rules(self) -> dict:
        session = httpx.AsyncClient(timeout=30)
        response = await session.get(self.config["LINKS"]["twitter_stream_rules_link"], auth=self.bearer_oauth)
        await session.aclose()

        if response.status_code != 200:
            raise Exception(f"Cannot get rules (HTTP {response.status_code}): {response.text}")
        self.logger.info(f"Get Rules: {json.dumps(response.json(), sort_keys=True)}")
        return response.json()


    async def delete_all_rules(self, rules) -> None:
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}

        session = httpx.AsyncClient(timeout=30)
        response = await session.post(self.config["LINKS"]["twitter_stream_rules_link"], auth=self.bearer_oauth, json=payload)
        await session.aclose()

        if response.status_code != 200:
            raise Exception(f"Cannot delete rules (HTTP {response.status_code}): {response.text}")
        self.logger.info(f"Delete All Rules: {json.dumps(response.json(), sort_keys=True)}")


    async def set_rules(self, delete) -> dict:
        rules = []

        for option in self.config.options("STREAMRULE", no_defaults=True):
            rules.append({"value": self.config.get('STREAMRULE', option)})

        payload = {"add": rules}

        session = httpx.AsyncClient(timeout=30)
        response = await session.post(self.config["LINKS"]["twitter_stream_rules_link"], auth=self.bearer_oauth, json=payload)
        await session.aclose()

        if response.status_code != 201:
            raise Exception(f"Cannot add rules (HTTP {response.status_code}): {response.text}")
        self.logger.info(f"Set Rules: {json.dumps(response.json(), sort_keys=True)}")


    async def get_stream(self, set) -> None:
        session = httpx.AsyncClient(timeout=30)

        async with session.stream("GET", self.config["LINKS"]["twitter_stream_link"], auth=self.bearer_oauth) as response:
            # If rate limit has been reached, wait until reset time
            if response.status_code == 429:
                await asyncio.sleep(int(response.headers["x-rate-limit-reset"]) - time.time())
            elif response.status_code != 200:
                raise Exception(f"Cannot get stream (HTTP {response.status_code}): {response.aiter_raw()}")

            async for response_line in response.aiter_text():
                if response_line and response_line != "\r\n" and response_line != "\n":
                    json_response = json.loads(response_line)
                    self.logger.info(json.dumps(json_response, sort_keys=True))


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
        config["DEFAULT"]["stream_tweet_log_file"],
        mode='a',
        maxBytes=1024 * 1024,
        backupCount=100,
        encoding="utf8",
    )
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)

    twitter_stream = TwitterStream(bearer_token, config, logger)
    asyncio.run(twitter_stream.main())