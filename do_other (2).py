# import functions
from functions import *
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext
from telegram.update import Update

TWO, THREE = range(2)

CHOOSE = range(1)


def do_task(update: Update, context: CallbackContext):
    message_id = update.message.message_id
    text = update.message.text
    text_id = text.replace("/", '')
    chat_id = update.message.chat_id
    context.user_data["task_id"] = text_id
    context.user_data["chat_id"] = chat_id
    context.user_data["message_id"] = message_id
    find_task = mydb["tasks"]
    get = find_task.find_one({"cmd_id": text_id})
    if chat_id in get['done_by']:
        update.message.reply_text("You have already done this task!")
        return ConversationHandler.END
    elif f"permit_{text_id}{chat_id}" in get['pending']:
        update.message.reply_text("You already submitted this task!\n\n"
                                  "Pending approval without rejection will get auto approved"
                                  " after 24 hours of submission")
        return ConversationHandler.END
        # keyboard = [["Submit Task", "Skip Task"]]
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("Do task", callback_data="do"),
        InlineKeyboardButton("Close", callback_data="close")]])
    # reply_markup = ReplyKeyboardMarkup(keyboard,  one_time_keyboard=True , resize_keyboard=True)
    update.message.reply_text(f"Title: {get['title']}\n\n"
                              f"Description: {get['des']}\n\n"
                              f"Link: {get['link']}", reply_markup=reply_markup, timeout=10,
                              reply_to_message_id=message_id)


def task_select(update: Update, context: CallbackContext):
    if update.callback_query['data'] == "do":
        tasks = mydb['tasks']
        get = tasks.find_one({"cmd_id": context.user_data['task_id']})
        if context.user_data['chat_id'] in get['done_by']:
            bot.sendMessage(chat_id=context.user_data['chat_id'],
                            text="You have already done this task!")
            return ConversationHandler.END
        elif f"permit_{context.user_data['task_id']}{context.user_data['chat_id']}" in get['pending']:
            bot.sendMessage(chat_id=context.user_data['chat_id'],
                            text="You already submitted this task!\n\n"
                            "Pending approval without rejection will get auto approved"
                            " after 24 hours of submission")
            return ConversationHandler.END
        keyboard = [["Confirm Submit", "cancel"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        bot.sendMessage(chat_id=context.user_data['chat_id'],
                        text=f"Now send your task proof and click submit\n"
                             f"This proof will send to task owner for verification",
                        reply_markup=markup)
        context.user_data['callback_id'] = update.callback_query.message.message_id
        return TWO
    else:
        bot.editMessageText(chat_id=context.user_data['chat_id'], text="Task Skipped",
                            message_id=update.callback_query.message.message_id)
        main_buttons(update, context)
        return ConversationHandler.END


def get_photo(update: Update, context: CallbackContext):
    context.user_data["photo"] = update.message.photo[-1]
    context.user_data["caption"] = update.message.caption
    update.message.reply_text("Got it!")
    return THREE
    # update.message.reply_photo(photo=photo)


def confirm_task(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if update.message.text == "Confirm Submit":
        try:
            photo = context.user_data['photo']
        except:
            update.message.reply_text("Your document is empty!\n"
                                      "Please send me your proof of work")
            return TWO
        tasks = mydb['tasks']
        get = tasks.find_one({"cmd_id": context.user_data['task_id']})
        get_list = list(get['pending'])
        permit_id = f"permit_{context.user_data['task_id']}{chat_id}"
        get_list.append(permit_id)
        try:
            tasks.update_one({"cmd_id": context.user_data['task_id']}, {'$set': {'pending': get_list}})
        except:
            bot.sendMessage("This task has ended!\nMaximum users reached")
        update.message.reply_text("Got your response and sent to task owner for verification")
        main_buttons(update, context)
        if str(context.user_data['caption']) == "None":
            bot.send_photo(chat_id=get["chat_id"], photo=photo,
                           caption=f"Click to approve:\n /{permit_id}")
        else:
            bot.send_photo(chat_id=get["chat_id"], photo=photo,
                           caption=f"{context.user_data['caption']}\n\nClick to approve:\n /{permit_id}")
        return ConversationHandler.END
    else:
        main_buttons(update, context)
        return ConversationHandler.END
