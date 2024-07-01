<p align="center"><b>TELESHARE</b></p>
<p align="center">A efficient and configurable telegram file sharing bot</p>

#### DEMO: [BOT LINK](https://t.me/TelezhareBot?start=IjIwMjQtMDUtMzAgMjM6NTM6Mjci)
#### FEATURES
- CodeXbotz links compatibility.
- Fully asynchronous.
- Highly configurable.
- In-built rate limiter.
- Multi-channel force subscription.
- Protect content.
- Quick Deployment.
- Toggleable auto file backup.
- Toggleable auto message delete.
- Type-hinted for improved code readability.
- User-friendly interface.

#### TODO
- [x] Broadcast / Announcement.
- [x] Configuration commands.
- [x] HTTP client.
- [x] Invite requests.
- [x] Public mode.
- [x] Quick deployments.
- [x] Support common file types: `(doc,photo,vid,audio)`.
- [x] Toggle Backup.
- [x] Help command.
- [x] Toggle global mode.
- [x] In-built rate limiter.
- [x] Fully remove database models.
- [x] Try again button.
- [x] Auto link generator.
- [x] add codeXbots file-sharing link compatibility.
- [ ] Tokenized access.

#### CURRENT AVAILABLE COMMANDS:
Use: `/help [command name]` for more informations.

1. `/make_files`: Handles a conversation that receives files to generate an accessable file link.
2. `/start`: Handle start command, it returns files if a link is included otherwise sends the user a request.
3. `/broadcast`: Broadcasts a message to multiple subscribed users
this command may take awhile depending on user count.
4. `/option`: Use to configure database options. See [START-UP REQUIREMENTS](#start-up-requirements) bot options for more informations.

#### Frequently Asked Questions
<details>
<summary>FAQS</summary>
1. How do i disable automatic deletation:

```
/option AUTO_DELETE_SECONDS 0
```
</details>

#### START-UP REQUIREMENTS
<details>
<summary>.env / environ</summary>

> You can use either .env or environ as a way to setup the configuration. Please see [.env_example](.env_example)  as reference.

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
- `FORCE_SUB_CHANNELS (list[int])`: force subscription channels.
- `AUTO_GENERATE_LINK`: toggle auto link generator when file is recieve directly. default to `True`.
</details>

<details>
<summary>Bot options</summary>

Set:
- `FORCE_SUB_MESSAGE (str|int)`: message during force subscription.
- `START_MESSAGE (str|int)`: a start message 
- `AUTO_DELETE_MESSAGE (str|int)`: an auto delete messages, {} is the amount of minutes.

- `AUTO_DELETE_SECONDS (int)`: auto deletion in minutes, is set as {} of AUTO_DELETE_MESSAGE.
- `GLOBAL_MODE (bool)`: toggle everyone to generate a file link.
- `BACKUP_FILES (bool)`: toggle all files to back up.


configure through `/option` command or use `/help option` for more information.

Usage:

    /option key new_value
    /option key [reply to a message]
Example:

    /option AUTO_DELETE_SECONDS 600
    /option FORCE_SUB_MESSAGE: reply to a message.
</details>

#### DEPLOYMENTS
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
<summary>Quick Deployment</summary>
  
Please edit the following "Environment Variable" and refer to [.env_example](.env_example) for reference.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/zawsq/Teleshare/tree/heroku-deploy)

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/apps/deploy?type=git&repository=github.com/zawsq/Teleshare&branch=main&builder=buildpack&run_command=cd+bot+%26%26+python+main.py&env[API_ID]=api_id&env[API_HASH]=api_hash&env[BOT_TOKEN]=bot_token&env[MONGO_DB_URL]=mongodb_url&env[BACKUP_CHANNEL]=backup&env[ROOT_ADMINS_ID]=admins&env[FORCE_SUB_CHANNELS]=force_sub)

</details>


<br>

____
**SUPPORT CHANNEL: [THE HQ](https://t.me/zawshq)**
