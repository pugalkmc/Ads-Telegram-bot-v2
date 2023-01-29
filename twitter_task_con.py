from functions import *
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

CHECK, GET_LINK, GET_TOTAL, GET_PER, CONFIRM = range(5)


def twitter_task(update, context):
    chat_id = update.message.chat_id
    people = mydb['people']
    get = people.find_one({"_id": chat_id})
    if get['TRX_balance'] >= 1:
        bot.sendMessage(chat_id=chat_id,
                        text="Enter your tweet link to promote:",
                        reply_markup=ReplyKeyboardMarkup([["cancel"]], resize_keyboard=True),
                        reply_to_message_id=update.message.message_id)
        return GET_LINK
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="You don't have enough TRX to create Twitter task!")
        return ConversationHandler.END


def get_link(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if "https://twitter.com/" in text:
        context.user_data["link"] = text
        context.user_data['chat_id'] = chat_id
        bot.sendMessage(chat_id=chat_id,
                        text="Enter total budget to spent:",
                        reply_to_message_id=update.message.message_id)
        return GET_TOTAL
    elif "cancel" == text:
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="Please enter a valid tweet link!")
        return GET_LINK


def get_total(update, context):
    chat_id = update.message.chat_id
    budget = float(update.message.text)
    if str(type(budget)) == "<class 'str'>":
        bot.sendMessage(chat_id=chat_id,
                        text="Total budget must be in numbers!")
        return GET_TOTAL
    elif "cancel" == budget:
        main_buttons(update, context)
        return ConversationHandler.END
    people = mydb['people']
    get = people.find_one({"_id": chat_id})

    if budget < 1:
        bot.sendMessage(chat_id=chat_id,
                        text="Minimum total budget is 1 TRX")
        return GET_TOTAL
    elif get["TRX_balance"] >= budget:
        context.user_data['budget'] = budget
        bot.sendMessage(chat_id=chat_id,
                        text="Enter TRX reward for each persons:",
                        reply_to_message_id=update.message.message_id)
        return GET_PER


def trx_per(update, context):
    chat_id = update.message.chat_id
    per_user = float(update.message.text)
    if str(type(per_user)) == "<class 'str'>":
        bot.sendMessage(chat_id=chat_id,
                        text="TRX per user must be in numbers!")
        return GET_PER
    elif "cancel" == per_user:
        main_buttons(update, context)
        return ConversationHandler.END
    elif (context.user_data['budget']/2) <= per_user:
        context.user_data['per_user'] = per_user
        bot.sendMessage(chat_id=chat_id,
                        text="Please confirm once again to submit task:",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ReplyKeyboardMarkup([["Confirm", "cancel"]], resize_keyboard=True))
        return CONFIRM
    else:
        bot.sendMessage(chat_id=chat_id, text="Please enter a valid TRX to submit task")
        return GET_PER


def confirm(update, context):
    text = update.message.text
    chat_id = update.message.chat_id
    if text == "Confirm":
        people = mydb['people']
        ind_time = datetime.datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M')
        twitter = mydb["twitter_task"]
        twitter.insert_one({"chat_id": chat_id,
                            "username": update.message.chat.username,
                            "link": context.user_data['link'],
                            "trx_per": context.user_data['per_user'],
                            "trx_total": context.user_data['budget'],
                            "time": ind_time,
                            "done": 0,
                            "done_by": []})
        get = people.find_one({"_id": chat_id})
        trx_total = context.user_data['budget']

        if get["payout_avail"] >= trx_total:
            people.update_one({"_id": chat_id}, {"$inc": {"TRX_balance": -float(trx_total),
                                                          'payout_avail': -float(trx_total)}})
        else:
            people.update_one({"_id": chat_id}, {"$inc": {"TRX_balance": -float(trx_total),
                                                          'payout_avail': 0}})
        bot.sendMessage(chat_id=chat_id, text="Your task has added successfully!")
        main_buttons(update, context)
        return ConversationHandler.END
    elif "cancel" == text:
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        return CONFIRM


DO_TWITTER, TWITTER_SUBMIT = range(2)


def message(update, context):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Coming soon")


# def twitter_task(update, context):
#     chat_id = update.message.chat_id
#     twitter = mydb["twitter_task"]
#     context.user_data['link'] = twitter['link']
#     context.user_data['id'] = twitter['task_id']
#     bot.sendMessage(chat_id=chat_id, text=f"Like and retweet this post\n\n"
#                                           f"Then click button DONE for verification\n\n"
#                                           f"Link: {twitter['link']}")
#     return DO_TWITTER

#
# def twitter_submit(update, context):
#     chat_id = update.message.chat_id
#     text = update.message.text
#     if "DONE" == text:
#

