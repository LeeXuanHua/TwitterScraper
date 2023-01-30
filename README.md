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
|<b>Input</b>       | usernames.txt & config.ini|
|<b>Output</b>      | data/twitter_user_data.log |
|<b>How It Works</b>|  Based on the usernames (newline separated) and query fields (config.ini) specified in input , query Twitter for the account metadata and 5 recent tweets | 
   

### Stream Tweets
|                   |   |
|-------------------|---|
|<b>Input</b>       | config.ini |
|<b>Output</b>      | data/twitter_stream_data.log |
<b>How It Works</b>| Based on the rules and query fields defined, establish a real-time stream to listen to new Twitter posts fulfilling the rules |

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