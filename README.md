# Automated Twitter Dashboard with Python, ReactJS, and Github Actions

<b>Work in progress</b>

## Overview
This project aims to identify the relationship between users (Elon Musk & Donald Trump) as well as compile relevant posts (related to the 2022 Twitter mass layoff). We identify these posts through hashtags #OneTeam and #LoveWhereYouWorked.

Data collection and processing will be using Python and stored into logs while the dashboarding and analysis will be using ReactJS.

This will be done incrementally, in the following order:
1. Automate data collection via Github Runners
2. Enable concurrent collection of User Tweets and Stream Tweets
3. Establish CLI for custom username, rules, and action selection (e.g. user tweets or stream tweets)
4. Include unit testings for Github CI/CD pipelining
5. Perform data processing via Python FastAPI
6. Develop dashboard and analysis with ReactJS
7. Develop a webapp version (similar to 3)

## Features

### User Tweets
|                   |   |
|-------------------|---|
|<b>Input</b>       | config.ini |
|<b>Output</b>      | data/twitter_user_data.log |
|<b>How It Works</b>|  Based on the usernames and query fields defined, query Twitter for the user metadata and 5 recent tweets | 
   

### Stream Tweets
|                   |   |
|-------------------|---|
|<b>Input</b>       | config.ini |
|<b>Output</b>      | data/twitter_stream_data.log |
<b>How It Works</b>| Based on the rules and query fields defined, establish a real-time stream to listen to new Twitter posts fulfilling the rules |


### CLI
- Created using <i>[argpase](https://realpython.com/command-line-interfaces-python-argparse/)</i> library
- Contains main parser to execute all actions (both usertweet and streamtweet)
- Contains 2 subparsers {usertweet, streamtweet} to separately execute each action
```
$ python cli/twiquery_cli.py --help
usage: twiquery [options]

Customisable queries to Twitter API by username, rules, fields for User Tweets and/or Stream Tweets

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Execute All Actions:
  -u x [x ...], --user x [x ...]
                        Query the tweets for these user(s)
  -c x, --count x       Number of tweets to query for each username
  -r rule [rule ...], --rule rule [rule ...]
                        Rules to filter the Tweet stream
  -t rule [rule ...], --tag rule [rule ...]
                        Tags mapping to the filter rules defined in the --rule option
  -d XmYs, --duration XmYs
                        Duration to stream tweets for, in the format of X minutes and Y seconds. Default -1 for indefinite
  --update-settings     Set custom options in config file without executing service
  --use-previous        Use previously-set custom options in config file

Execute Single Actions:
  Execute a single action with the following subcommands

  {usertweet,streamtweet}
    usertweet           customise with username [-u], tweet count [-c], and many more
    streamtweet         customise with rules [-r], timeout duration [-t] and many more

This executes both user tweets and stream tweets. To execute only one, please use the subparsers {usertweet, streamtweet}
```
```
$ python cli/twiquery_cli.py usertweet --help
usage: twiquery [options] usertweet [-h] [-u x [x ...]] [-c x] [--u_created_at] [--u_description] [--u_entities] [--u_id] [--u_location] [--u_name]   
                                    [--u_pinned_tweet_id] [--u_profile_image_url] [--u_protected] [--u_public_metrics] [--u_url] [--u_username]       
                                    [--u_verified] [--u_withheld] [--t_attachments] [--t_author_id] [--t_context_annotations] [--t_conversation_id]   
                                    [--t_created_at] [--t_entities] [--t_geo] [--t_id] [--t_in_reply_to_user_id] [--t_lang] [--t_non_public_metrics]  
                                    [--t_organic_metrics] [--t_possibly_sensitive] [--t_promoted_metrics] [--t_public_metrics] [--t_referenced_tweets]
                                    [--t_source] [--t_text] [--t_withheld] [--update-settings] [--use-previous]

optional arguments:
  -h, --help            show this help message and exit
  -u x [x ...], --user x [x ...]
                        Query the tweets for these user(s)
  -c x, --count x       Number of tweets to query for each username
  --u_created_at        (User query) Remove the created_at field
  --u_description       (User query) Remove the description field
  --u_entities          (User query) Remove the entities field
  --u_id                (User query) Remove the id field
  --u_location          (User query) Remove the location field
  --u_name              (User query) Remove the name field
  --u_pinned_tweet_id   (User query) Remove the pinned_tweet_id field
  --u_profile_image_url
                        (User query) Remove the profile_image_url field
  --u_protected         (User query) Remove the protected field
  --u_public_metrics    (User query) Remove the public_metrics field
  --u_url               (User query) Remove the url field
  --u_username          (User query) Remove the username field
  --u_verified          (User query) Remove the verified field
  --u_withheld          (User query) Remove the withheld field
  --t_attachments       (Tweet query) Remove the attachments field
  --t_author_id         (Tweet query) Remove the author_id field
  --t_context_annotations
                        (Tweet query) Remove the context_annotations field
  --t_conversation_id   (Tweet query) Remove the conversation_id field
  --t_created_at        (Tweet query) Remove the created_at field
  --t_entities          (Tweet query) Remove the entities field
  --t_geo               (Tweet query) Remove the geo field
  --t_id                (Tweet query) Remove the id field
  --t_in_reply_to_user_id
                        (Tweet query) Remove the in_reply_to_user_id field
  --t_lang              (Tweet query) Remove the lang field
  --t_non_public_metrics
                        (Tweet query) Include the non_public_metrics field
  --t_organic_metrics   (Tweet query) Include the organic_metrics field
  --t_possibly_sensitive
                        (Tweet query) Remove the possibly_sensitive field
  --t_promoted_metrics  (Tweet query) Include the promoted_metrics field
  --t_public_metrics    (Tweet query) Remove the public_metrics field
  --t_referenced_tweets
                        (Tweet query) Remove the referenced_tweets field
  --t_source            (Tweet query) Remove the source field
  --t_text              (Tweet query) Remove the text field
  --t_withheld          (Tweet query) Remove the withheld field
  --update-settings     Set custom options in config file without executing service
  --use-previous        Use previously-set custom options in config file
```

```
$ python cli/twiquery_cli.py streamtweet --help
usage: twiquery [options] streamtweet [-h] [-r rule [rule ...]] [-t rule [rule ...]] [-d XmYs] [--update-settings] [--use-previous]

optional arguments:
  -h, --help            show this help message and exit
  -r rule [rule ...], --rule rule [rule ...]
                        Rules to filter the Tweet stream
  -t rule [rule ...], --tag rule [rule ...]
                        Tags mapping to the filter rules defined in the --rule option
  -d XmYs, --duration XmYs
                        Duration to stream tweets for, in the format of X minutes and Y seconds. Default -1 for indefinite
  --update-settings     Set custom options in config file without executing service
  --use-previous        Use previously-set custom options in config file
```

## How to Run the Code
##### Run Locally
Step 1: Update the `Bearer_Token` in `.env.stub` to your Twitter Developer account bearer token <br>
Step 2: Rename `.env.stub` to `.env` <br>
Step 3: Install dependencies with `pip install -r requirements.txt` <br>
Step 4: Run `python main.py` <br>

## Design Considerations & Implementations

### Github Actions & Runners
- Configured to activate every 6hrs via cronjob (due to Github runner's runtime limitations)
- Timeout occurs after 5hrs (due to Github runner's cronjob imprecision)
    - Inbuilt command timeout is used instead of Github action's timeout-minutes
- Errorneous runner is successful only if timeout (error code 124); otherwise runner fails (other error exit codes)
- Caching is used to speed up runner and dependency initialisation
- Strategy matrix used for cross-platform testing

### Exception Handling
- For each function (user tweet and stream tweet), exceptions are raised to parent for handling wherever reasonable
    - main() and create_thread() functions will handle all exceptions eventually
- Exceptions are usually due to network communication via httpx
    - For exception hierarchy, refer to: https://www.python-httpx.org/exceptions/
    - Network related exceptions are handled by attempting again
    - All other exceptions (e.g. developer-introduced) are designed to crash the program (thus exit code non-0/124)

### Logging
- [Logger hierarchy](https://www.toptal.com/python/in-depth-python-logging) is as follow:
    ```
    Root [WARNING]
    |
    |-- __main__ [WARNING] (RotatingFileHandler; Propagate=True; main.log)
    |   |-- user_tweets [WARNING] (RotatingFileHandler; Propagate=True; data/twitter_user_data.log)
    |   |
    |   |-- stream_tweets [WARNING] (RotatingFileHandler; Propagate=True; data/twitter_stream_data.log)
    |
    ```
- Logs are allowed to propagate upwards:
    1. Does not cause issue
        - Exceptions are explicitly and implicitly propagated, therefore no issue of double logging
        - For non exceptions (e.g. INFO), we ignore these by setting the handler level to >= WARNING
    2. Makes more design sense
        - Log files are at the bottom are intended more for data collection, not purely for logging
        - Easier to sync and identify the errors via 1 log file

### Asynchronous vs Multithreading
- Asynchronous has higher performance than multithreading
    - Therefore, I have tested asynchronous web communication with streaming
- Though not efficient, I have tested multi-threading by adding on top of the functionalities
    - For learning, this approach will be used in developing subsequent functionalities (such as FastAPI and web app) as compared to pure async

### CLI
- For our CLI stored in the `/cli` folder, the primary entrypoint is via main.py
- Provided generic options to execute both User Tweets & Stream Tweets services
- Provided 2 subparsers with more options for User Tweets and Stream Tweets each
    - subparsers work similar to `git init`, `git commit`, `git rebase`, etc 
- Included update-settings to set custom options in config file without executing the services
    - Typically used together with `--use-previous` option
- Included use-previous to use previously-set custom options in config file
    - Typically used together with `--update-settings` option
    - `--use-previous` is necessary even if we use defaults for CLI options
    - A use case for this is when we wish to execute all services concurrently, with custom fields set
- When designing a CLI application, it is important to understand:
    1. What customisable features are required of the application (e.g. usernames, stream filter rules)
    2. What added/convenience features can be further provided (e.g. --use-previous)
    3. What are the default values for the options (e.g. lists of strings, int values)
    4. What are the input type (e.g. str, int)
    5. How many input to expect for each option
    6. What are the appropriate metavar and help descriptions
- Note that when reading from config.ini, we do not require `ast.literal_eval()` as the format can be identified and is unchanged

## Research
### Web Servers vs Web Frameworks
- Web Servers:
    - Decouples the server implementation from the application framework. This allows for an ecosystem of interoperating webservers and application frameworks
    - Pays attention to connection and resource management to provide a robust server implementation
    - Ensures graceful behavior to either server or client errors, and resilience to poor client behavior or denial of service attacks
    - E.g. HTTP Headers, Flow Control, Request and Response bodies, Timeouts, Resource Limits, Server Errors, Graceful Process Shutdown, HTTP Pipelining
- Comparison of different frameworks & servers: https://fastapi.tiangolo.com/alternatives/
    - Starlette is used for Python async server (ASGI standards)
        - FastAPI is "Starlette on steroids" for web framework and uses Uvicorn / Gunicorn for server
        - Speed Benchmarking: Uvicorn > Starlette > FastAPI
            - Reason: The latter builds upon the former for each
            - Refer: https://fastapi.tiangolo.com/benchmarks/

    - Uvicorn vs Gunicorn: https://fastapi.tiangolo.com/deployment/server-workers/

        |                   | Uvicorn | Gunicorn |
        |-------------------|---------|----------|
        | <b>Standards</b>  | ASGI    | WSGI     |
        | <b>Role</b>       | Worker Class  | Process Manager |
        | <b>How it Works</b> | [Official Doc][2] | [Official Doc][1] |

        - Note the choice of number of worker class & number of threads
        - TLDR; Gunicorn is process manager that can run different worker class of choice, and Uvicorn is an async worker class that is compatible with Gunicorn process manager (there are other process managers available)


[1]: https://docs.gunicorn.org/en/stable/design.html#server-model
[2]: https://www.uvicorn.org/server-behavior/