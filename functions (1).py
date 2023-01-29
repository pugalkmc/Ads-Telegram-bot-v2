# tronpy~=0.2.6

# import pymongo
import pymongo
import random
from pytz import timezone
import datetime
from telegram.bot import Bot
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from tronpy import Tron
from tronpy.keys import PrivateKey

client = pymongo.MongoClient(
    "mongodb+srv://pugalkmc:pugalkmc@cluster0.ey2yh.mongodb.net/mydb?retryWrites=true&w=majority")

mydb = client.get_default_database()
bot = Bot(token="5394324389:AAH9kDST-U9o4L7wXzdAyVLS5Ti1_pT0gbI")

client_tron = Tron()


def is_valid(address):
    is_address = client_tron.is_address(str(address))
    return is_address


ONE_TRON = 1000000

# your wallet information
WALLET_ADDRESS = "TJLUz79xwf6C6HU63c3Ti93BtfaqGmrwcH"
PRIVATE_KEY = "801e612fa5420001bcaae1aa7c37b434871f0d269a41fa14f69f2364e4c5f6ae"


# send some 'amount' of Tron to the 'wallet' address
def send_tron(amount, wallet):
    try:
        priv_key = PrivateKey(bytes.fromhex(PRIVATE_KEY))

        # create transaction and broadcast it
        txn = (
            client_tron.trx.transfer(WALLET_ADDRESS, str(wallet), int(amount * ONE_TRON))
                .memo("Transaction Description")
                .build()
                .inspect()
                .sign(priv_key)
                .broadcast()
        )
        # wait until the transaction is sent through and then return the details
        return txn.wait()

    # return the exception
    except Exception as ex:
        return ex


# bot.setWebhook("https://trx-earn-bot.herokuapp.com/" + "5394324389:AAGvCQN8ogbnwj1MStLHmvu7Kb9e3uQiF_4")


def task_list(update, context):
    chat_id = update.message.chat_id
    tasks_list = mydb["tasks"]
    list1 = []
    total = 0
    total_trx = 0
    for i in tasks_list.find({}).sort("trx_per", -1):
        if (chat_id not in i['done_by']) and (f"permit_{i['cmd_id']}{chat_id}" not in i['pending']):
            total += 1
            total_trx += i['trx_per']
            text = f"Task No: {total}\n" \
                   f"Title: {i['title']}\n" \
                   f"Do task : /{i['cmd_id']}\n" \
                   f"Payment: {i['trx_per']} TRX\n" \
                   f"Users : {i['done']}/{i['limit']}\n"
            list1.append(text)
    update.message.reply_text("Total task found:{0}\n\n"
                              "Can earn total: {1} TRX\n\n"
                              "{2}".format(total, float(total_trx), '\n'.join(x for x in list1)))


def task_page(update, context, text):
    markup = ReplyKeyboardMarkup([["Proof task📥", "Chat Bot🆕"],
                                  ['Group(soon)', 'Channel(soon)'],
                                  ["Twitter(soon)", 'Back↩']], resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=text,
                    reply_markup=markup)


def sub_approve(title, trx_total, trx_per, link, des, chat_id):
    create_id = f"approve_{random.randint(100000, 999999)}"
    tasks = mydb['pending']
    cmd_id = f"task_{random.randint(100000, 999999)}"
    ind_time = datetime.datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M')
    tasks.insert_one({"chat_id": chat_id, "create_id": create_id, "title": title, "trx_total": trx_total,
                      "trx_per": trx_per, "link": link, "des": des, "limit": int(trx_total // trx_per),
                      "time": ind_time, "done": 0, "cmd_id": cmd_id, 'done_by': [], 'pending': []})
    bot.sendMessage(chat_id=1291659507, text=f"Task approve id:/{create_id}\n"
                                             f"Total budget: {trx_total}\n"
                                             f"TRX/user: {trx_per}\n"
                                             f"Users limit: {trx_total // trx_per}\n"
                                             f"title: {title}\n\n"
                                             f"Description:\n"
                                             f"{des}\n\n"
                                             f"link: {link}")


# try:
#     from tronapi import Tron
#     from tronapi import HttpProvider
# except:
#     bot.sendMessage(chat_id =1291659507, text='error in import tronapi')

def main_buttons(update, context):
    reply_keyboard = [['Do Task💸', '', 'Create Task📜'], ['Balance⚖', 'Deposit➕'], ['Referral link📎', 'More❕']]

    bot.sendMessage(chat_id=update.message.chat_id, text="Main Menu",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                     resize_keyboard=True,
                                                     one_time_keyboard=True))
