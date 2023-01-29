from functions import *
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

CREATE, TITLE, TRX_TOTAL, TRX_PER, LINK, CONFIRM = range(6)


def task_new(update, context):
    chat_id = update.message.chat_id
    people = mydb["people"]
    get = people.find_one({"_id": chat_id})
    if get["TRX_balance"] >= 1:
        bot.sendMessage(chat_id=chat_id, text="This task willl help you to promote any link\n"
                                              "Users will send you the task screenshot proof\n"
                                              "You can check their proof youself and approve the task\n"
                                              "<------------------------->")
        markup = ReplyKeyboardMarkup([["cancel"]], one_time_keyboard=True, resize_keyboard=True)
        bot.sendMessage(chat_id=chat_id, text="Send task title to go next step:", reply_markup=markup,
                        reply_to_message_id=update.message.message_id)
        return CREATE
    else:
        bot.sendMessage(chat_id=chat_id, text="You must have atleat more than 1 TRX to create task\n"
                                              "To create task deposit TRX to the bot")
        return ConversationHandler.END


def get_title(update, context):
    chat_id = update.message.chat_id
    title = update.message.text
    context.user_data["title"] = title
    if title == "cancel":
        main_buttons(update, context)
        return ConversationHandler.END
    bot.sendMessage(chat_id=chat_id, text="Enter total task budget in TRX")
    return TITLE


def get_total(update, context):
    chat_id = update.message.chat_id
    trx_total = update.message.text
    balance = mydb["people"]
    get = balance.find_one({"_id": chat_id})
    try:
        if trx_total == "cancel":
            main_buttons(update, context)
            return ConversationHandler.END
        elif float(trx_total) >= 1:
            if get["TRX_balance"] >= float(trx_total):
                update.message.reply_text("Enter how mush to be rewarded per user:")
                context.user_data["trx_total"] = trx_total
                return TRX_TOTAL
            else:
                update.message.reply_text("Insufficient balance...\n"
                                          f"Your TRX balance {get['TRX_balance']}")
                return TITLE
        else:
            update.message.reply_text("TRX budget must be greater than 1")
            return TITLE
    except:
        update.message.reply_text("TRX amount must be in numbers!")
        return TITLE


def get_per(update, context):
    chat_id = update.message.chat_id
    trx_per = update.message.text
    try:
        if trx_per == "cancel":
            main_buttons(update, context)
            return ConversationHandler.END
        elif float(trx_per) <= float(context.user_data["trx_total"]):
            if float(trx_per) >= 0.3:
                update.message.reply_text("Send full task description(Instructions):")
                context.user_data["trx_per"] = trx_per
                return TRX_PER
            else:
                update.message.reply_text("Task amount can't be less than 0.3 TRX")
                return TRX_TOTAL
    except:
        update.message.reply_text("TRX amount must be in numbers!")
        return TRX_TOTAL


def description(update, context):
    chat_id = update.message.chat_id
    des = update.message.text
    if des == "cancel":
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        context.user_data["des"] = des
        update.message.reply_text("Send the link you want to promote:")
        return LINK


def get_link(update, context):
    chat_id = update.message.chat_id
    link = update.message.text
    if link == "cancel":
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        context.user_data["link"] = link
        markup = ReplyKeyboardMarkup([["Confirm", "cancel"]], one_time_keyboard=True, resize_keyboard=True)
        bot.sendMessage(chat_id=chat_id, text="Check task details once again and confirm:", reply_markup=markup)
        return CONFIRM


def confirm_create(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "Confirm":
        title = context.user_data["title"]
        trx_total = context.user_data["trx_total"]
        trx_per = context.user_data["trx_per"]
        link = context.user_data["link"]
        des = context.user_data["des"]
        sub_approve(title, float(trx_total), float(trx_per), link, des, int(chat_id))
        detect = mydb["people"]
        get = detect.find_one({"_id": chat_id})
        if get["payout_avail"] >= float(trx_total):
            detect.update_one({"_id": chat_id}, {"$inc": {"TRX_balance": -float(trx_total),
                                                          'payout_avail': -float(trx_total)}})
        else:
            detect.update_one({"_id": chat_id}, {"$inc": {"TRX_balance": -float(trx_total),
                                                          'payout_avail': 0}})
        bot.sendMessage(chat_id=chat_id, text="Task submitted to owner")
        main_buttons(update, context)
        return ConversationHandler.END
    elif text == "cancel":
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        return CONFIRM
