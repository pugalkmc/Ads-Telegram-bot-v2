from functions import *
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

ADDRESS, AMOUNT, CONFIRM_WITH = range(3)


def withdraw_con(update, context):
    chat_id = update.message.chat_id
    context.user_data['username'] = update.message.chat.username
    people = mydb['people']
    context.user_data['chat_id'] = int(chat_id)
    user = people.find_one({'_id': chat_id})
    if user['payout_avail'] >= 10:
        button = [['Withdraw⤴', 'cancel']]
        context.user_data['payout_avail'] = float(user['payout_avail'])
        bot.sendMessage(chat_id=chat_id, text=f"Balance: {user['TRX_balance']} TRX\n\n"
                                              f"Total Earned: {user['earned_total']} TRX\n\n"
                                              f"Available for payout:\n"
                                              f"{user['payout_avail']} TRX",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True))
        bot.sendMessage(chat_id=chat_id, text="Enter withdrawal TRX(TRC-20) address! or click cancel to go back")
        return ADDRESS
    else:
        bot.sendMessage(chat_id=chat_id, text="Minimum withdrawal limit is 10 TRX\n"
                                              "Do more task to withdraw")
        return ConversationHandler.END


def check_address(update, context):
    text = update.message.text
    verify = is_valid(text)
    if verify is True:
        context.user_data['address'] = text
        bot.sendMessage(chat_id=context.user_data['chat_id'], text="Enter withdrawal amount:",
                        reply_to_message_id=update.message.message_id)
        return AMOUNT
    elif text == 'cancel':
        main_buttons(update, context)
        return ConversationHandler.END
    else:
        bot.sendMessage(chat_id=context.user_data['chat_id'], text="Enter a valid Tron(TRX) address")
        return ADDRESS


def with_amount(update, context):
    try:
        value = float(update.message.text)
    except ValueError:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="TRX value must be a number!")
        return AMOUNT
    if value < 10:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Minimum withdrawal is 10 TRX!")
        return AMOUNT
    elif value <= context.user_data['payout_avail']:
        context.user_data['value'] = float(value)
        button = [["Confirm", "cancel"]]
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=f"Please confirm once again to withdraw\n\n"
                             f"Withdrawal of: {value}",
                        reply_markup=ReplyKeyboardMarkup(button,
                                                         resize_keyboard=True))
        return CONFIRM_WITH


def confirm_withrawal(update, context):
    text = update.message.text
    chat_id = update.message.chat_id
    people = mydb['people']
    if text == 'Confirm':
        value = context.user_data['value']
        people.update_one({"_id": chat_id}, {"$inc": {"TRX_balance": -value,
                                                      "payout_avail": -value
                                                      }})
        bot.sendMessage(chat_id=chat_id,
                        text="Withdrawal request submitted!\n\n"
                             "Please wait until the transaction is being completed")
        get = send_tron(context.user_data['value'], context.user_data['address'])
        main_buttons(update, context)
        if "balance is not sufficient" in str(get):
            bot.sendMessage(chat_id=chat_id,
                            text="Error in transaction\n\n"
                                 "Report sent to admin\n"
                                 "You will get manual transaction!")
            bot.sendMessage(chat_id=chat_id,
                            text=f"Not sufficient balance to withdraw report:\n\n"
                                 f"chat id: {chat_id}"
                                 f"username: {update.message.chat.username}"
                                 f"Amount: {context.user_data['value']}"
                                 f"address: {context.user_data['address']}")
            return ConversationHandler.END
        else:
            bot.sendMessage(chat_id=1291659507,
                            text=f"Withdrawal Successful:\n\n"
                                 f"Amount: <code>{context.user_data['value']}</code>\n\n"
                                 f"Transaction scan: https://tronscan.io/#/transaction/{get['id']}",
                            parse_mode="html")
            return ConversationHandler.END
        # withdraw(update, context, context.user_data['address'], context.user_data['value'])
    else:
        main_buttons(update, context)
        return ConversationHandler.END
