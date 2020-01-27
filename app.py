#!/home/fred/TornadoBot/venv/bin/python3
import requests
import tweepy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from web3 import Web3
from pathlib import Path

ethContracts = {
    'eth01': '0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc',
    'eth1': '0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936',
    'eth10': '0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF',
    'eth100': '0xA160cdAB225685dA1d56aa342Ad8841c3b53f291'
}

daiContracts = {
    'dai100': '0xD4B88Df4D29F5CedD6857912842cff3b20C8Cfa3',
    'dai1000': '0xFD8610d20aA15b7B2E3Be39B396a1bC3516c7144',
    'dai10000': '0xF60dD140cFf0706bAE9Cd734Ac3ae76AD9eBC32A'
}

fdir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(Path(os.path.join(fdir, '.env')))

API_KEY = os.getenv("ETHERSCAN_API")
INFURA_KEY = os.getenv("INFURA_KEY")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

abi = open(os.path.join(fdir, 'abi.json'), 'r').read()

w3 = Web3(Web3.WebsocketProvider(f'wss://mainnet.infura.io/ws/v3/{INFURA_KEY}'))

fromBlock = 0
totalEth = float(0)
totalDai = float(0)
tweetMessage = 'Here are the stats from the last 24 hours:'
split_messages = []


def build_message(tx_times, amount, token):
    global tweetMessage
    tweetMessage += f'\n⚡ {tx_times} transactions with a value of {amount} {token} were made totalling {round(tx_times * float(amount), 2)} {token}'


def split_message():
    global split_messages
    string_append = ''
    data = tweetMessage.splitlines(keepends=True)
    for i in data:
        if len(string_append + i) < 280:
            string_append += i
        else:
            split_messages.append(string_append)
            string_append = i
    split_messages.append(string_append)


def send_tweet():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    if len(tweetMessage) > 280:
        send_message(api)
    else:
        api.update_status(tweetMessage)


def send_message(api):
    split_message()
    id1 = api.update_status(split_messages[0]).id
    try:
        id2 = api.update_status(split_messages[1], in_reply_to_status_id=id1).id
        api.update_status(split_messages[2], in_reply_to_status_id=id2)
    except IndexError:
        pass


def get_from_block():
    global fromBlock
    unix_time = int(datetime.timestamp(datetime.now() + timedelta(days=-1)))
    url = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={unix_time}&closest=before&apikey={API_KEY}'
    fromBlock = int(requests.get(url).json()['result'])


def get_eth_deposits():
    global totalEth
    for key, value in ethContracts.items():
        deposits = w3.eth.contract(address=value, abi=abi).events.Deposit.createFilter(
            fromBlock=int(fromBlock)).get_all_entries()
        if key == 'eth01' and deposits:
            totalEth += len(deposits) * 0.1
            build_message(len(deposits), '0.1', 'ETH')
        elif key == 'eth1' and deposits:
            totalEth += len(deposits)
            build_message(len(deposits), '1', 'ETH')
        elif key == 'eth10' and deposits:
            totalEth += len(deposits) * 10
            build_message(len(deposits), '10', 'ETH')
        elif key == 'eth100' and deposits:
            totalEth += len(deposits) * 100
            build_message(len(deposits), '100', 'ETH')


def get_dai_deposits():
    global totalDai
    for key, value in daiContracts.items():
        deposits = w3.eth.contract(address=value, abi=abi).events.Deposit.createFilter(
            fromBlock=int(fromBlock)).get_all_entries()
        if key == 'dai100' and deposits:
            totalDai += len(deposits) * 100
            build_message(len(deposits), '100', 'DAI')
        elif key == 'dai1000' and deposits:
            totalDai += len(deposits) * 1000
            build_message(len(deposits), '1000', 'DAI')
        elif key == 'dai10000' and deposits:
            totalDai += len(deposits) * 10000
            build_message(len(deposits), '10000', 'DAI')


if __name__ == "__main__":
    get_from_block()
    get_eth_deposits()
    tweetMessage += f'\n⚡⚡⚡ With a total amount of {round(totalEth, 2)} ETH'
    get_dai_deposits()
    tweetMessage += f'\n⚡⚡⚡ With a total amount of {totalDai} DAI'
    send_tweet()
