<p align="center"><b>TELESHARE</b></p>
<p align="center">A efficient and configurable telegram file sharing bot</p>

**DEMO:** [BOT LINK](https://t.me/TelezhareBot?start=IjIwMjQtMDUtMzAgMjM6NTM6Mjci)

**SUPPORT CHANNEL:** [THE HQ](https://t.me/zawshq)

#### INDEX
* [Features](#features)
* [Todo](#todo)
* [All Available Commands](#all-available-commands)
* [Frequently Asked Questions](#frequently-asked-questions)
* [Setup Requirements](#setup-requirements)
* [Deployments](#deployments)

#### FEATURES
- [All available commands.](#all-available-commands)
- CodeXbotz links compatibility.
- Fully asynchronous.
- In-built rate limiter.
- Join chat request.
- Multi-channel force subscription.
- [Option Setup.](#bot-options)
- Protect content.

#### TODO
- [x] Database and Option refactor.
- [x] Ban command.
- [x] Join chat requests.

#### ALL AVAILABLE COMMANDS:
Use: `/help [command name]` for more informations.

1. `/make_files`: Handles a conversation that receives files to generate an accessable file link.
2. `/start`: Handle start command, it returns files if a link is included otherwise sends the user a request.
3. `/broadcast`: Broadcasts a message to multiple subscribed users
this command may take awhile depending on user count.
4. `/option`: Use to configure database options. See [bot options](#bot-options) for more informations.
5. `/delete_link`: Delete an accessible link from the database and delete the corresponding file from the backup channel.
6. Auto link generation: just forward or send a file directly to the bot.
7. `/range_files`: Fetch files directly from backup channel to create a sharable link of ranged file ids.
8. `/ban` and `/unban`: Bans a user from using the bot.

#### Frequently Asked Questions
<details>
<summary>FAQS</summary>

1. How do i disable automatic deletation:

```
/option AUTO_DELETE_SECONDS 0
```

2. Can I disable file backup? It depends on your use case. By default, the bot automatically grabs the files through the Telegram server. If you need to use the links in the future on another bot, backing up the files is mandatory.
3. How to turn on join chat request?

set `PRIVATE_REQUEST` from .env or environment variable to `True`


</details>

#### SETUP REQUIREMENTS
<details id="environment">
<summary>.env / environ</summary>

> You can set up the configuration using either a `.env` file or an `environ variable`. Please refer to the [.env_example](.env_example) file as a reference. Don't forget to add `[` and `]` or brackets if required, as shown in the example file.

[Telegram website](https://my.telegram.org/auth)
- API_ID
- API_HASH

[Bot father](t.me/BotFather)
- BOT_TOKEN

[Mongo database](https://www.mongodb.com)
- MONGO_DB_URL = mongodb+srv

Bot Config
- `BOT_WORKER (int)`: amount of bot workers, default to 8.
- `BOT_SESSION (int)`: bot session name, reads from bot directory.
- `BOT_MAX_MESSAGE_CACHE_SIZE (int)`: amount of message to cache, recommended to cache more than a thousand if your bot is big enough due to scheduling. default to 100.

Main config
- `BACKUP_CHANNEL (int)`: file backup channel.
- `ROOT_ADMINS_ID (list[int])`: bot admins.
- `PRIVATE_REQUEST (bool)`: enable private request on private channel/group. default to `False`.
- `PROTECT_CONTENT (bool)`: disalllow forwarding and saving of files sent by the bot. default to `True`.
- `FORCE_SUB_CHANNELS (list[int] | optional)`: force subscription channels, leave it blank or do not add it on `.env` if you do not need a subscription channel.
- `AUTO_GENERATE_LINK`: toggle auto link generator when file is recieve directly. default to `True`.
</details>

<details id="bot-options">
<summary>Bot options</summary>

- `FORCE_SUB_MESSAGE (str | int)`: message during force subscription.
- `BANNED_USER_MESSAGE (str | int)`: The message to display if user is banned from using the bot.
- `ADDITIONAL_MESSAGE (str | int)`: The message to display after a user recieved a file, set to 0 to disable.
- `START_MESSAGE (str | int)`: a start message.
- `AUTO_DELETE_MESSAGE (str | int)`: an auto delete messages, {} is the amount of minutes.

- `AUTO_DELETE_SECONDS (int)`: auto deletion in minutes, is set as {} of AUTO_DELETE_MESSAGE.
- `GLOBAL_MODE (bool)`: toggle everyone to generate a file link.
- `BACKUP_FILES (bool)`: toggle all files to back up.


configure through `/option` command or use `/help option` for more information.

Usage:

    /option key new_value
    /option key [reply to a message]
Example:

    /option AUTO_DELETE_SECONDS 600
    /option FORCE_SUB_MESSAGE [reply to a message.]
</details>

#### DEPLOYMENTS

Please edit the following "Environment Variable" for `quick deployment` or create an ".env" for `local deployment` and refer to [.env_example](.env_example) for reference or [configuration](#environment) for descriptions.

<details>
<summary>Local Deployment</summary>

1. Clone the repo
```
git clone https://github.com/zawsq/Teleshare.git
```
then change directory to Teleshare 
```
cd Teleshare
```

2. Create an .env file refer to [.env_example](.env_example) for referencee.


4. Create an python environment (poetry / virtualenv): `Optional`
```
pip install virtualenv
virtualenv myenv

source myenv/bin/activate

windows:
myenv\Scripts\activate
```
5. Install requirements
```
pip install -r requirements.txt
```

6. Start the bot.
```
python -m bot.main
```


</details>

<details>
<summary>Heroku Deployment</summary>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/zawsq/Teleshare/tree/heroku-deploy)

If this repo cannot be deployed in Heroku, please fork it and deploy it manually using the [heroku-deploy](https://github.com/zawsq/Teleshare/tree/heroku-deploy) branch.
</details>

<details>
<summary>Koyeb Deployment</summary>

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/services/deploy?type=git&repository=github.com/zawsq/Teleshare&branch=main&builder=dockerfile&env%5BAPI_ID%5D=api_id&env%5BAPI_HASH%5D=api_hash&env%5BBOT_TOKEN%5D=bot_token&env%5BMONGO_DB_URL%5D=mongodb_url&env%5BBACKUP_CHANNEL%5D=backup&env%5BROOT_ADMINS_ID%5D=admins&env%5BFORCE_SUB_CHANNELS%5D=force_sub)

Just setup the environment variables and your done.
</details>

<details>
<summary>Render Deployment</summary>

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

To deploy on render, fork the main repo and deploy using `Dockerfile`

Setup your Render environment variable refer to [.env_example](.env_example) for reference or [configuration](#environment) for descriptions.
</details>
