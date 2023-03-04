# Description
Telegram Bot to track real-time stats of Genshin Impact.

# Requirements
- python
- sqlite3

# BotFather set up
Create a bot with [@BotFather](https://t.me/BotFather) and set the following commands:
```
help - List of commands.
menu - Interact with me using UI.
redeem - Redeem the gift code.
set - Set resin/teapot/updates values.
get - Get resin/teapot/updates values.
```

# Run
- Install python dependencies.

    `pip install -r requirements.txt`
    > If you want to contribute, install also development dependencies.
    >
    >    `pip install -r dev_requirements.txt`

- Create a self-signed certificate in order to communicate with telegram server
  using SSL.

    `openssl req -newkey rsa:2048 -sha256 -nodes -keyout paimon.key
    -x509 -days 3650 -out paimon.pem`

- Create a copy of config.template.json and change the dummy values in .config.json.

    `cp config.template.json .config.json`
    > - **token** - Telegram bot token, obtained from
    > [@BotFather](https://t.me/BotFather)
    >
    > - **webhook**: true to run the bot using webhooks. false to use polling.
    >
    > - **ip**: Your server ip, where the bot is hosted
    >
    > - **port**: Port to receive telegram updates: port must be 443, 80, 88 or 8443.
    >
    > - **cert**: Path to your server certificate (can be self-signed)
    >
    > - **timezone**: Your timezone as
    > [TZ database name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List)
    >
    > - **telegram\_uid** - Must be changed with your actual telegram uid.
    > You can obtain your telegram uid from bots like
    > [@getmyid\_bot](https://t.me/getmyid_bot).
    >
    > ```json
    >     "accounts": {
    >         "123123123": {
    >             "ltoken": "..."
    >         }
    >     }
    > ```
    > The following cookies can be obtained using the tutorial from
    > [genshin.py](https://thesadru.github.io/genshin.py/authentication/)
    > - **ltoken**: [hoyolab.com](https://www.hoyolab.com/genshin) unique token for authentication
    > - **ltuid**: [hoyolab.com](https://www.hoyolab.com/genshin) uid
    > - **ctoken**: cookie_token from [genshin.hoyoverse.com](https://genshin.hoyoverse.com/en/gift)
    > - **uid**: account_id from [genshin.hoyoverse.com](https://genshin.hoyoverse.com/en/gift)


- Execute the bot.

    `./paimon.py`
    > **Note:** If you run the bot in port 80, it may be needed to run the bot as
    > superuser (**sudo**).


# Contributing
Happy to see you willing to make the project better. In order to make a contribution,
please respect the following format:
- Imports sorted with usort: `usort format <file>`
- Code formatted with black (line lenght 79): `black -l 79 <file>`

> If you are using flake8, ignore E203 in .flake8
> ```
> [flake8]
> extend-ignore = E203
> ```

### VSCode project settings
VSCode should have the following settings in settings.json:
```
{
    "python.analysis.fixAll": [],
    "python.formatting.blackArgs": [
        "-l 79"
    ],
    "python.formatting.provider": "black",
    "isort.path": [
        "usort format"
    ],
}
```
> ```
> "python.linting.flake8Args": [
>     "--ignore=E203",
> ],
> ```

> If you are using flake8, ignore E203 warning.

# License
    Copyright (c) 2021-2023 scmanjarrez. All rights reserved.
    This work is licensed under the terms of the MIT license.

For a copy, see
[LICENSE](LICENSE).
