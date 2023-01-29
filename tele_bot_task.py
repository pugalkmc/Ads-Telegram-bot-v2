import functions
from functions import *
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.ext import ConversationHandler

GET_LINK, GET_BOT, GET_DESCRIPTION, GET_TOTAL, CONFIRM = range(5)


def tele_task(update, context, text="Choose task method"):
    chat_id = update.message.chat_id
    people = mydb['people']
    get = people.find_one({"_id": chat_id})
    if get['TRX_balance'] >= 1:
        bot.sendMessage(chat_id=chat_id,
                        text="Now send the bot refer link you want to promote:",
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
    if "https://telegram.me/" in text or "https://t.me/" in text:
        context.user_data["link"] = text
        context.user_data['chat_id'] = chat_id
        bot.sendMessage(chat_id=chat_id,
                        text="Now forward any message from the bot:",
                        reply_to_message_id=update.message.message_id)
        return GET_BOT
    elif "cancel" == text:
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="Please enter a valid bot link!")
        return GET_LINK


def get_bot(update, context):
    full_details = update.message
    chat_id = update.message.chat_id
    if update.message.text == "cancel":
        main_buttons(update, context)
        return ConversationHandler.END
    elif full_details['forward_from'] is None:
        bot.sendMessage(chat_id=chat_id, text="Please forward the message from the bot to go next step")
        return GET_BOT
    elif full_details['forward_from']['is_bot'] is True:
        update.message.reply_text(f"Got it-> @{full_details['forward_from']['username']}")
        context.user_data['bot_username'] = full_details['forward_from']['username']
        # ")
        context.user_data['first_name'] = full_details['forward_from']['first_name']
        bot.sendMessage(chat_id=update.message.chat_id, text="Now enter description about this task!",
                        reply_to_message_id=update.message.message_id)
        return GET_DESCRIPTION
    else:
        bot.sendMessage(chat_id=chat_id, text="It's not forward message from bot!")
        return GET_BOT


def get_description(update, context):
    text = update.message.text
    if text == 'cancel':
        main_buttons(update, context)
        return ConversationHandler.END
    elif len(text) > 10:
        bot.sendMessage(chat_id=update.message.chat_id, text="Now enter the total budget you want spend for this ad!",
                        reply_to_message_id=update.message.message_id)
        context.user_data['description'] = text
        return GET_TOTAL
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Please enter description at least 10 letters")
        return GET_DESCRIPTION


def get_total(update, context):
    chat_id = update.message.chat_id
    try:
        budget = float(update.message.text)
    except:
        bot.sendMessage(chat_id=chat_id,
                        text="Total budget must be in numbers!")
        return GET_TOTAL
    if "cancel" == budget:
        main_buttons(update, context)
        return ConversationHandler.END

    elif float(budget) < 1:
        bot.sendMessage(chat_id=chat_id,
                        text="Minimum total budget is 1 TRX")
        return GET_TOTAL
    else:
        context.user_data['budget'] = float(budget)
        bot.sendMessage(chat_id=chat_id, text="Please confirm once again to submit this task!",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ReplyKeyboardMarkup([["Confirm", "cancel"]], resize_keyboard=True))
        return CONFIRM


def confirm(update, context):
    text = update.message.text
    chat_id = update.message.chat_id
    if text == "Confirm":
        people = mydb['people']
        ind_time = datetime.datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M')
        twitter = mydb["bot_task"]
        task_id = random.randint(100000, 9999999)
        twitter.insert_one({"chat_id": chat_id,
                            "task_id":task_id,
                            "username": update.message.chat.username,
                            "link": context.user_data['link'],
                            "bot_username": context.user_data['bot_username'],
                            "bot_first_name": context.user_data['first_name'],
                            "description": context.user_data["description"],
                            "trx_per": 0.15,
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


# """Telegram task do conversation"""

INLINE_TELE, CHECK_WORK = range(2)


def get_task(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    context.user_data['chat_id'] = chat_id
    tele_bot = mydb["bot_task"]
    for i in tele_bot.find({}):
        if chat_id not in i['done_by']:
            context.user_data["task_id"] = int(i['task_id'])
            context.user_data["bot_username"] = i["bot_username"]
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton("Message Bot", url=i['link']),
                InlineKeyboardButton('✅ Started', callback_data="started")]])
            bot.sendMessage(chat_id=chat_id,
                            text=f"⚠WARNING: the following is a third party advertisement. "
                                 f"We are not responsible for this.\n"
                            f"<- - - - - - - - - - - - - ->\n\n"
                            f"Title: {i['bot_first_name']}\n\n"
                            f"Description: {i['description']}\n\n"
                            f"Bot link: {i['link']}\n\n"
                            f"<- - - - - - - - - - - - - ->\n\n"
                            f"1️⃣Press the 'Message Bot' button below.\n"
                            f"2️⃣After clicking '✅ Started' button then forward a new "
                                 f"message to me from the bot to earn TRX.\n",
                            reply_markup=reply_markup, timeout=10,
                            reply_to_message_id=message_id)
            return INLINE_TELE
    else:
        bot.sendMessage(chat_id=chat_id, text="No task currently available!")
        task_page(update, context, text="Choose another task!")
        return ConversationHandler.END


def go_telegram(update, context):
    if update.callback_query['data'] == "started":
        bot.sendMessage(chat_id=context.user_data["chat_id"],
                        text="Now forward any of the message from the bot to verify!",
                        reply_markup=ReplyKeyboardMarkup([["cancel task"]], resize_keyboard=True))
        return CHECK_WORK
        # bot.sendMessage(chat_id=context.user_data['chat_id'],


def skip_tele_do(update, context):
    text = update.message.text
    if text == "Chat Bot🆕":
        get_task(update, context)
    elif text == "Proof task📥":
        task_list(update, context)
    return ConversationHandler.END


def check_work(update, context):
    full_info = update.message
    chat_id = update.message.chat_id
    if update.message.text == "cancel task":
        functions.task_page(update, context, text="Choose task method!")
        return ConversationHandler.END
    if update.message.text == "cancel":
        main_buttons(update, context)
        return ConversationHandler.END
    elif full_info['forward_from'] is None:
        bot.sendMessage(chat_id=chat_id, text="Please forward the message from the bot to go next step")
        return CHECK_WORK
    elif full_info['forward_from']['is_bot'] is True:
        if context.user_data['bot_username'] == full_info['forward_from']['username']:
            people = mydb['people']
            tasks = mydb['bot_task']
            task_id = context.user_data['task_id']
            task_get = tasks.find_one({'task_id': task_id})
            if str(task_get) != "None":
                done_by_list = list(task_get['done_by'])
                try:
                    reward = (float(task_get['trx_per']) / 100) * 90
                    people.update_one({'_id': chat_id}, {'$inc': {"TRX_balance": float(reward),
                                                                      "payout_avail": float(reward),
                                                                      "earned_total": float(reward)}})
                    get_refer_by = people.find_one({"_id": chat_id})
                    ref_income = (reward / 100) * 7
                    people.update_one({"_id": get_refer_by['ref_by']}, {"$inc": {"ref_income": ref_income,
                                                                                 "TRX_balance": ref_income,
                                                                                 "payout_avail": ref_income,
                                                                                 "earned_total": ref_income}})
                    if (task_get["trx_total"]//task_get["trx_per"]) == (task_get['done']):
                        tasks.delete_one({'task_id': task_id})
                        bot.sendMessage(chat_id=task_get['chat_id'],
                                        text=f"your task: /{task_get['cmd_id']} has completed\n\n"
                                             f"Task totally done by {task_get['limit']} users")
                    done_by_list.append(int(chat_id))
                    tasks.update_one({"task_id": task_id}, {'$inc': {"done": 1}})
                    tasks.update_one({"task_id": task_id}, {"$set": {"done_by": done_by_list}})
                    # bot.sendMessage(chat_id=update.message.chat_id,
                    #                 text=)
                    functions.task_page(update, context, text="Task verified!")
                    return ConversationHandler.END

                except:
                    bot.sendMessage(chat_id=chat_id, task="Error occurred report sent to admin!")
                    return ConversationHandler.END
            else:
                bot.sendMessage(chat_id=chat_id, text="Sorry this task has ended just now!")
                return ConversationHandler.END
        else:
            bot.sendMessage(chat_id=chat_id, text=f"It's not forward from @{context.user_data['bot_username']}")
    else:
        bot.sendMessage(chat_id=chat_id, text="It's not forward message from bot!")
        return ConversationHandler.END

