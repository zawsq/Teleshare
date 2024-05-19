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
- [ ] Help command.
- [ ] Toggle global mode.
- [ ] In-built rate limiter.
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
- MONGO_DB_URL = mongodb://http

Main config
- BACKUP_CHANNEL
- ROOT_ADMINS_ID
- FORCE_SUB_CHANNELS
- PRIVATE_REQUEST
</details>

#### QUICK DEPLOYMENT
Please edit the following "Environment Variable" and refer to [.env_example](.env_example) for reference.

<details>
<summary>KOYEB</summary>

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/apps/deploy?type=git&repository=github.com/zawsq/Teleshare&branch=main&builder=buildpack&run_command=cd+bot+%26%26+python+main.py&env[API_ID]=api_id&env[API_HASH]=api_hash&env[BOT_TOKEN]=bot_token&env[MONGO_DB_URL]=mongodb_url&env[BACKUP_CHANNEL]=backup&env[ROOT_ADMINS_ID]=admins&env[FORCE_SUB_CHANNELS]=force_sub)
</details>

<details>
<summary>HEROKU</summary>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/zawsq/Teleshare/tree/heroku-deploy)
</details>

<br>

____
**SUPPORT CHANNEL: [THE HQ](https://t.me/zawshq)**
