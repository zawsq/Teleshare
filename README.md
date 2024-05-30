<p align="center"><b>TELESHARE</b></p>
<p align="center">A efficient and configurable telegram file sharing bot</p>

> [!IMPORTANT]  
> This bot is currently in [MVP](https://en.m.wikipedia.org/wiki/Minimum_viable_product) Stage. Expect frequent changes and updates. Not yet ready for production use. Use for testing and feedback purposes only.

> [!NOTE]  
> _Feel free to open an issue for more upcoming features!_

#### FEATURES
- Automatic file backup.
- Automatic message deletion.
- Easy to set up.
- Fast and efficient.
- Fully asynchronous.
- Highly configurable.
- Multi-channel force subscription.
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
- [ ] Toggle Backup.
- [x] Help command.
- [x] Toggle global mode.
- [x] In-built rate limiter.
- [x] Fully remove database models.
- [ ] Tokenized access.
- [x] Try again button.
- [x] add codeXbots file-sharing link compatibility.

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
- BOT_WORKER (int): amount of bot workers, default to 4.
- BOT_SESSION (int): bot session name, reads from bot directory.
- BOT_MAX_MESSAGE_CACHE_SIZE (int): amount of message to cache, recommended to cache more than a thousand if your bot is big enough due to scheduling. defaults to 4.

Main config
- BACKUP_CHANNEL (int): file backup channel.
- ROOT_ADMINS_ID (list[int]): bot admins.
- PRIVATE_REQUEST (bool): enable private request on private channel/group.
- FORCE_SUB_CHANNELS (list[int]): force subscription channels.
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

3. Use "deploy.sh" if you don't wanna
bother setting up python path. be sure to give deploy.sh a permission to run.
```
bash deploy.sh
```

4. Manually deployment
install requirements
```
pip install requirements.txt
```
set python path
```
export PYTHONPATH="${PYTHONPATH}:$PWD"
```
change directory to bot
```
cd bot
```
start the bot
```
python main.py
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
