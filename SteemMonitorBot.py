#   GNU GENERAL PUBLIC LICENSE
#                       Version 3, 29 June 2007
#
# Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.


import sys
import time, datetime
import requests
import json
from steem.blockchain import Blockchain

# ---- User Settings -------

author = 'sc-steemit' # Your Author Name

# Mentions are anything that you desire to be mentioned about.
# Include your author name here to be notified when someone mentions you as well.
mentions = ['sc-steemit','gridcoinstats','crypto.fans']

# Triggers are what to look for. Possible options are:
# mention = Mentions of strings in 'mentions'
# comment = Comments on posts by 'author'
# vote = Votes on posts by 'author'
# curation = Curation rewards to 'author'
# reward = Author rewards to 'author'
# interest = Interest sent to 'author'
# transfer = Transfer sent to 'author'

triggers = ['mention','comment','vote','curation','reward','interest','transfer']

# Telegram ID - Get your ID from @MyTelegramID_bot (https://telegram.me/mytelegramid_bot)
telegram_id    = "0"

# ---- User Settings End ---
# ----
# ---- No Editing Below This is Nessesary

# ---- Script Settings ----

telegram_token = "349116670:AAGsWt38CT839nx4oyT_5EYhAoQSDQXOn4Y" # @CryptofansSteemBot

# ---- Script Setting End ----
steem_chain = Blockchain()

# Telegram API Transmitter
def telegram(method, params=None):
    url = "https://api.telegram.org/bot"+telegram_token+"/"
    params = params
    r = requests.get(url+method, params = params).json()
    return r

# Telegram Notify Creator
def alert(msg):
    payload = {"chat_id":telegram_id, "text":msg}
    m = telegram("sendMessage", payload)

for operation in steem_chain.stream_from():
    op = operation["op"]
    try:
        for trigger in triggers:
            if op[0] == "comment":
                # Check for mention in both Main Posts + Comments
                if trigger == "mention":
                    for mention in mentions:
                        if mention in op[1]['body'] and op[1]['author'] != author:
                            alert("Mentioned on steem by " + op[1]['author'] + " https://steemit.com/@" + op[1]['author'] + "/" + op[1]['permlink'])
                            print("Alerted on mention")

                # Only check for replies in comments
                if trigger == "comment":
                    if op[1]['parent_author'] != "":
                        if op[1]['parent_author'] == author and op[1]['author'] != author:
                            alert("Comment received on steem by " + op[1]['author'] + " https://steemit.com/@" + op[1]['author'] + "/" + op[1]['permlink'])
                            print("Alerted on comment received")

            elif op[0] == "vote" and trigger == "vote":
                if op[1]['author'] == author:
                    vote_weight = int(op[1]['weight']/100)
                    alert("Vote receieved on steem by " + op[1]['voter'] + " (" + str(vote_weight) +"%) https://steemit.com/@" + op[1]['author'] + "/" + op[1]['permlink'])
                    print("Alerted on vote received")
            elif op[0] == "curation_reward" and trigger == "curation":
                if op[1]['curator'] == author:
                    alert("Curator reward (" + op[1]['reward'] + ") https://steemit.com/@" + op[1]['comment_author'] + "/" + op[1]['comment_permlink'])
                    print("Alerted on Curator Reward")

            elif op[0] == "transfer" and trigger == "transfer":
                if op[1]['to'] == author:
                    alert("Transfer of " + op[1]['amount'] + " Received from " + op[1]['from'] + " with the following memo\n-----\n" + op[1]['memo'].encode('utf-8','replace'))
                    print("Alerted on Transfer")

            elif op[0] == "author_reward" and trigger == "reward":
                if op[1]['author'] == author:
                    alert("Author reward (" + op[1]['sbd_payout'] + ", " + op[1]['steem_payout'] + ", " + op[1]['vesting_payout'] + ") https://steemit.com/@" + op[1]['author'] + "/" + op[1]['permlink'])
                    print("Alerted on Author Reward")

            elif op[0] == "interest" and trigger == "interest":
                if op[1]['owner'] == author:
                    print("Interest receieved " + op[1]['interest']) # Needs to be checked so we do not have 0.00 SBD interest before we send notification to useers

except Exception as e:
        print('Exception occured:')
        print(str(e))
