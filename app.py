import requests
import tweepy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from web3 import Web3

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

load_dotenv()

API_KEY = os.getenv("ETHERSCAN_API")
INFURA_KEY = os.getenv("INFURA_KEY")

abi = open('abi.json', 'r').read()

fromBlock = 0
totalEth = float(0)
totalDai = float(0)
tweetMessage = 'Here are the stats from the last 24 hours:'
api = ''

def build_message(tx_times,amount, token):
    global tweetMessage
    tweetMessage += '\n⚡ {} transactions with a value of {} {} were made totalling {} {}'\
        .format(tx_times, amount, token, tx_times * float(amount), token)

def send_tweet():
    auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
    auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    api.update_status(tweetMessage)


def get_from_block():
    global fromBlock
    unixTime = int(datetime.timestamp(datetime.now() + timedelta(days=-1)))
    url = 'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={}&closest=before&apikey={}' \
        .format(unixTime, API_KEY)
    fromBlock = int(requests.get(url).json()['result'])

w3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/" + INFURA_KEY))

def get_eth_deposits():
    global  totalEth
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
    get_dai_deposits()
    send_tweet()
    print(totalEth, totalDai)
    print(tweetMessage)


pass




