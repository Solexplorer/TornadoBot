# TornadoBot

This is the twitter bot that tracks how many deposits were made in the last 24 hours.

## Get Started

Install python modules:

`pip3 install -r requirements.txt`

In order to use the app, you will need an [`INFURA`](https://infura.io) key, an [`Etherscan API`](https://etherscan.io/login) key 
and the access to a [twitter developer account](https://www.extly.com/docs/autotweetng_joocial/tutorials/how-to-auto-post-from-joomla-to-twitter/apply-for-a-twitter-developer-account/#apply-for-a-developer-account)

Fill the fields in the file `.env.example` and rename the file to `.env`

To run it every 24 hours create a cron job and append the following line:

```shell
crontab -e
* */24 * * * /path/to/venv/python3 /path/to/app.py >>  ~/cron.log 2>&1
```

See the bot [here](https://twitter.com/BotTornado).
