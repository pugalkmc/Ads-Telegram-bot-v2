# This is a sample Python script.

import os
import logging
import other_tasks
import tele_bot_task
import twitter_task_con
import withdrawal_conversation
from big_text import *
from do_other import *
# import join_group_con
from telegram.ext import *
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

# from operations import withdraw, is_valid
# from tronpy import Tron

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def start(update, context):
    sender = update.message.reply_text
    chat_id = update.message.chat_id
    username = update.message.chat.username
    text = update.message.text
    if str(username) == "None":
        sender("No username found for your account")
        sender("Please set username for your telegram\n"
               "1)Go telegram account settings\n"
               "2)Click username\n"
               "3)Set unique and simplified username")
    else:
        checking_exist = mydb["people"]
        bot.sendMessage(chat_id=chat_id, text="This KMC TRX earning bot\n"
                                              "You can earn TRX by doing tasks\n"
                                              "Also You can create task for other to do\n\n")

        main_buttons(update, context)
        for i in checking_exist.find({}):
            if username == i["username"]:
                break
        else:
            link = f"https://telegram.me/earn_trx_ind_bot?start={chat_id}"
            checking_exist.insert_one({"_id": chat_id, "username": username, "referral": link,
                                       "ref_count": 0, "TRX_balance": 0.0, "ref_income": 0.0,
                                       'earned_total': 0.0, 'payout_avail': 0.0, "ref_by": "None"})
            bot.sendMessage(chat_id=1291659507, text="New user found @" + str(username))
            referal(text, username, chat_id)


def referal(text, username, chat_id):
    get_id = text.replace("/start", '')
    if len(get_id) > 0:
        ref = mydb["people"]
        try:
            get = ref.find_one({"_id": int(get_id)})
            get_invitee = get["_id"]
            ref.update_one({"_id": get_invitee}, {"$inc": {"ref_count": 1}})
            ref.update_one({"_id": chat_id}, {"$set": {'ref_by': get_invitee}})
            bot.sendMessage(chat_id=get_invitee, text=f"You got new referral: @{username}")
        except:
            pass


def msg_hand(update, context):
    chat_id = update.message.chat_id
    # username = update.message.chat.username
    sender = update.message.reply_text
    text = update.message.text
    if 'Do Task💸' == text:
        task_page(update, context, text="Choose task method!")
    elif "Proof task📥" == text:
        task_list(update, context)
    elif 'Balance⚖' == text:
        people = mydb['people']
        get = people.find_one({'_id': chat_id})
        bot.sendMessage(chat_id=chat_id, text=f"Balance: {get['TRX_balance']} TRX\n\n"
                                              f"Total Earned: {get['earned_total']} TRX\n\n"
                                              f"Available for payout:\n"
                                              f"{get['payout_avail']} TRX",
                        reply_to_message_id=update.message.message_id)
    elif 'Deposit➕' == text:
        bot.sendMessage(chat_id=chat_id, text="Send TRX to this address(TRC-20):\n"
                                              "<code>TSPZcEraokyNAuFR4Shgyn5D4ycsWjJhrL</code>\n\n"
                                              "Then send TXID of your transaction\n\n"
                                              "After transaction fill below google form:\n"
                                              "https://surveyheart.com/form/626a84d84a8aaf49225347e7\n\n"
                                              "NEWS: Auto deposit will be enabled SOON",
                        parse_mode="html", reply_to_message_id=update.message.message_id)

    elif 'Referral link📎' == text:
        get_link = mydb['people']
        get = get_link.find_one({"_id": chat_id})
        bot.sendMessage(chat_id=chat_id, text=f"Your referral count: {get['ref_count']}\n\n"
                                              f"You have earned {get['ref_income']} TRX by referrals\n\n"
                                              f"Referral link: \n{get['referral']}\n\n"
                                              f"You can withdraw your referral income or spend it on ads\n\n"
                                              f"You will earn 7% commission when your friends do task "
                                              f"or create task\n\n",
                        reply_to_message_id=update.message.message_id)
    if text == "More❕":
        reply_keyboard = [["Withdraw➖", "Support👤"], ["About💬", "Rules🔖"], ["Back↩"]]
        sender("Use below buttons for quick access",
               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
               reply_to_message_id=update.message.message_id)
    elif 'Rules🔖' == text:
        bot.sendMessage(chat_id=chat_id, text=rules, reply_to_message_id=update.message.message_id)
    elif "About💬" == text:
        bot.sendMessage(chat_id=chat_id, text=about, reply_to_message_id=update.message.message_id)
    elif "Support👤" == text:
        bot.sendMessage(chat_id=chat_id, text="Support group link:\n"
                                              "https://t.me/+dFsICH3quPRhYjVl\n\n"
                                              "Join our support group to get more benefits\n\n"
                                              "Note: ADMIN WILL NEVER DM YOU FIRST!\n\n"
                                              "Admin support: @PugalKMC", reply_to_message_id=update.message.message_id)
    elif "add_trx " in text:
        text = update.message.text
        text1 = text.replace("add_trx ", '')
        separate = text1.split("{}")
        get_id = int(separate[0])
        get_trx = int(separate[1])
        people = mydb['people']
        try:
            people.update_one({"_id": get_id}, {"$inc": {"TRX_balance": get_trx}})
            bot.sendMessage(chat_id=chat_id, text=f"{get_trx} trx added to {get_id} account")
        except:
            bot.sendMessage(chat_id=chat_id, text="Wrong format or other error")
    elif "reduce_trx " in text:
        text = update.message.text
        text1 = text.replace("reduce_trx ", '')
        separate = text1.split("{}")
        try:
            get_id = int(separate[0])
            get_trx = int(separate[1])
            people = mydb['people']
            user = people.find_one({"_id": get_id})
            if (user['payout_avail'] - get_trx) < 0:
                bot.sendMessage(chat_id=chat_id, text="Can't detect trx! out of range!!")
            else:
                if user['payout_avail'] >= get_trx:
                    people.update_one({"_id": get_id}, {"$inc": {"TRX_balance": -get_trx, 'payout_avail': -get_trx}})
                    bot.sendMessage(chat_id=chat_id, text=f"{get_trx} trx reduced to {get_id} account")
                else:
                    people.update_one({"_id": get_id}, {"$inc": {"TRX_balance": -get_trx}})
                    bot.sendMessage(chat_id=chat_id, text=f"{get_trx} trx reduced to {get_id} account")
        except:
            bot.sendMessage(chat_id=chat_id, text="Wrong format or other error")
    elif "send_msg " in text:
        after = text.replace("send_msg ", "")
        infos = after.split("{}")
        # try:
        #     full_node = HttpProvider('https://api.trongrid.io')
        #     solidity_node = HttpProvider('https://api.trongrid.io')
        #     event_server = HttpProvider('https://api.trongrid.io')
        #
        #     tron = Tron(full_node=full_node,
        #                 solidity_node=solidity_node,
        #                 event_server=event_server)
        #
        #     tron.private_key = '009faab68456edf92132cc74a580316d159bdc10a544bda7f82a52175968a323'
        #     tron.default_address = 'TSPZcEraokyNAuFR4Shgyn5D4ycsWjJhrL'
        #
        #     # added message
        #     send = tron.trx.send_transaction('TEo84EXz7ZmaQkLXPwmkLnEhQd1DqH2DNU', 1)
        #
        #     print(send)
        #     bot.sendMessage(chat_id=chat_id, text=send)
        # except:
        #     bot.sendMessage(chat_id=chat_id, text="Error in transaction")
        try:
            id = infos[0]
            msg = infos[1]
            bot.sendMessage(chat_id=id, text=msg)
            bot.sendMessage(chat_id=chat_id, text="Message sent!")
        except:
            bot.sendMessage(chat_id=chat_id, text="Improper format")
    elif "announcement_user " in text:
        people = mydb["people"]
        after = text.replace("announcement_user ", "")
        for i in people.find({}):
            bot.sendMessage(chat_id=i["_id"], text=f"New Announcement!:\n\n"
                                                   f"{after}")
        else:
            bot.sendMessage(chat_id=chat_id, text="Message sent to all users!")

    elif text == "Back↩" or text == "cancel":
        main_buttons(update, context)


def select_task_method(update, context):
    chat_id = update.message.chat_id
    markup = ReplyKeyboardMarkup([['Bot Chats💬', 'Other Method📂'], ["Twitter Post🔜", "cancel"]],
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    bot.sendMessage(chat_id=chat_id, text="Please select task method you want to create:\n\n"
                                          "1)Bot Chats💬: This option will help you easily gain members for your "
                                          "group\n"
                                          "This bot will auto verify members to provide reward.\n\n"
                                          "2)Other Method📁: this option will be manual verification by "
                                          "your self, So you need to give details for doing task "
                                          "in description.", reply_markup=markup,
                    reply_to_message_id=update.message.message_id)


def approve_list():
    cmd = mydb["pending"]
    cmds = ["nothing"]
    for i in cmd.find({}):
        cmds.append(i["create_id"])
    return cmds


def commands(update, context):
    text = update.message.text
    after = text.replace("/", '')
    tasks = mydb["tasks"]
    if "approve" in text:
        pending = mydb['pending']
        get = pending.find_one({"create_id": after})
        if str(get) != "None":
            tasks.insert_one(get)
            pending.delete_one({"create_id": after})
            update.message.reply_text("Task permitted successfully")
    elif "permit_task_" in text:
        reuse = text.replace("/permit_task_", '')
        get_task_id = int(reuse[0:6])
        get_chat_id = int(reuse[6:])
        people = mydb['people']
        tasks = mydb['tasks']
        task_get = tasks.find_one({'cmd_id': f'task_{get_task_id}'})
        if str(task_get) != "None":
            done_by_list = list(task_get['done_by'])
            approve_list = list(task_get['pending'])
            try:
                reward = (float(task_get['trx_per']) / 100) * 90
                people.update_one({'_id': get_chat_id}, {'$inc': {"TRX_balance": float(reward),
                                                                  "payout_avail": float(reward),
                                                                  "earned_total": float(reward)}})
                get_refer_by = people.find_one({"_id": get_chat_id})
                ref_income = (reward / 100) * 7
                people.update_one({"_id": get_refer_by['ref_by']}, {"$inc": {"ref_income": ref_income,
                                                                             "TRX_balance": ref_income,
                                                                             "payout_avail": ref_income,
                                                                             "earned_total": ref_income}})

                if (task_get['limit']) == (task_get['done'] + 1):
                    tasks.delete_one({'cmd_id': f'task_{get_task_id}'})
                    bot.sendMessage(chat_id=task_get['chat_id'],
                                    text=f"your task: /{task_get['cmd_id']} has completed\n\n"
                                         f"Task totally done by {task_get['limit']} users")
                approve_list.remove(after)
                done_by_list.append(int(get_chat_id))
                tasks.update_one({"cmd_id": f'task_{get_task_id}'}, {'$inc': {"done": 1}})
                tasks.update_one({"cmd_id": f'task_{get_task_id}'}, {"$set": {"done_by": done_by_list}})
                tasks.update_one({"cmd_id": f'task_{get_task_id}'}, {'$set': {'pending': approve_list}})
                update.message.reply_text("Task approved!")
            except:
                update.message.reply_text("Task already approved!")

    elif "task_" in text:
        get = tasks.find_one({'cmd_id': after})
        if str(get) != "None":
            do_task(update, context)


def cancel(update, context):
    main_buttons(update, context)
    return ConversationHandler.END


#
# webhook_url = "https://webhook.site/48184ba5-39e5-4f29-bc4c-bb8cb7790f22"
# # 5123712096:AAFoWsAeO_sJyrsl0upMa-LUCeHE-k8AWYE
API_KEY = "5394324389:AAH9kDST-U9o4L7wXzdAyVLS5Ti1_pT0gbI"

# PORT = int(os.environ.get("PORT", 3978))


# r = requests.post(webhook_url)

# 5394324389:AAGvCQN8ogbnwj1MStLHmvu7Kb9e3uQiF_4 trx bot


def main():
    updater = Updater(API_KEY)
    dp = updater.dispatcher
    job_queue = updater.job_queue
    # job_queue.run_repeating(send_message_job, interval=10.0, first=0.0)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.command, commands))
    dp.add_handler(MessageHandler(Filters.text('Back↩'), main_buttons))
    task = ConversationHandler(entry_points=[CallbackQueryHandler(task_select)],
                               states={TWO: [MessageHandler(Filters.photo, get_photo)],
                                       THREE: [MessageHandler(Filters.text, confirm_task)]
                                       }, fallbacks=[MessageHandler(Filters.text, confirm_task)])

    # chat_member_task = ConversationHandler(entry_points=[MessageHandler(Filters.text("Chat Member"), chat_member)],
    #                                        states={
    #                                            CHAT_MEMBER_CREATE: [MessageHandler(Filters.text, MEMBER_TASK_TIT)]
    #                                        })

    other_task = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Other Method📂'), other_tasks.task_new)],
        states={other_tasks.CREATE: [MessageHandler(Filters.text, other_tasks.get_title)],
                other_tasks.TITLE: [MessageHandler(Filters.text, other_tasks.get_total)],
                other_tasks.TRX_TOTAL: [MessageHandler(Filters.text, other_tasks.get_per)],
                other_tasks.TRX_PER: [
                    MessageHandler(Filters.text, other_tasks.description)],
                other_tasks.LINK: [MessageHandler(Filters.text, other_tasks.get_link)],
                other_tasks.CONFIRM: [
                    MessageHandler(Filters.text, other_tasks.confirm_create)]
                }, fallbacks=[MessageHandler(Filters.text("cancel"), cancel)]
    )

    withdrawal = ConversationHandler(
        entry_points=[MessageHandler(Filters.text("Withdraw➖"), withdrawal_conversation.withdraw_con)],
        states={withdrawal_conversation.ADDRESS: [MessageHandler(Filters.text,
                                                                 withdrawal_conversation.check_address)],
                withdrawal_conversation.AMOUNT: [MessageHandler(Filters.text,
                                                                withdrawal_conversation.with_amount)],
                withdrawal_conversation.CONFIRM_WITH: [MessageHandler(Filters.text,
                                                                      withdrawal_conversation.confirm_withrawal)]},
        fallbacks=[])
    # join_group_task = ConversationHandler(
    #     entry_points=[MessageHandler(Filters.text('Chat Members🆕'),join_group_con)]
    # )
    # twitter_task = ConversationHandler(
    #     entry_points=[MessageHandler(Filters.text("Twitter Post"), twitter_task_con.twitter_task)],
    #     states={
    #         twitter_task_con.GET_LINK: [MessageHandler(Filters.text, twitter_task_con.get_link)],
    #         twitter_task_con.GET_TOTAL: [MessageHandler(Filters.text, twitter_task_con.get_total)],
    #         twitter_task_con.GET_PER: [MessageHandler(Filters.text, twitter_task_con.trx_per)],
    #         twitter_task_con.CONFIRM: [MessageHandler(Filters.text, twitter_task_con.confirm)]
    #     }, fallbacks=[])

    """Telegram bot task add and remove"""
    tele_task_add = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Bot Chats💬'), tele_bot_task.tele_task)],
        states={
            tele_bot_task.GET_LINK: [MessageHandler(Filters.text, tele_bot_task.get_link)],
            tele_bot_task.GET_BOT: [MessageHandler(Filters.text, tele_bot_task.get_bot)],
            tele_bot_task.GET_DESCRIPTION: [MessageHandler(Filters.text, tele_bot_task.get_description)],
            tele_bot_task.GET_TOTAL: [MessageHandler(Filters.text, tele_bot_task.get_total)],
            tele_bot_task.CONFIRM: [MessageHandler(Filters.text, tele_bot_task.confirm)]
        }, fallbacks=[]
    )
    # Telegram task do conversation
    do_telegram = ConversationHandler(
        entry_points=[MessageHandler(Filters.text("Chat Bot🆕"), tele_bot_task.get_task)],
        states={
            tele_bot_task.INLINE_TELE: [CallbackQueryHandler(tele_bot_task.go_telegram,
                                                             pattern='^' + "started" + '$'),
                                        MessageHandler(Filters.text, tele_bot_task.skip_tele_do)],
            tele_bot_task.CHECK_WORK: [MessageHandler(Filters.text, tele_bot_task.check_work)]
        }, fallbacks=[]
    )

    dp.add_handler(do_telegram)
    dp.add_handler(tele_task_add)
    # dp.add_handler(twitter_task)
    dp.add_handler(withdrawal)
    dp.add_handler(other_task)
    dp.add_handler(task)
    # dp.add_handler(MessageHandler(Filters.text("Chat Bot🆕"), tele_bot_task.get_task))
    dp.add_handler(MessageHandler(Filters.text(["Twitter🔜", "Twitter Post🔜"]), twitter_task_con.message))
    dp.add_handler(MessageHandler(Filters.text('Create Task📜'), select_task_method))
    dp.add_handler(MessageHandler(Filters.text, msg_hand))
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=API_KEY)
    # updater.bot.setWebhook('https://mywebhook/5394324389:AAH9kDST-U9o4L7wXzdAyVLS5Ti1_pT0gbI')
    # updater.bot.setWebhook("https://trx-earn-bot.herokuapp.com/" + "5394324389:AAGvCQN8ogbnwj1MStLHmvu7Kb9e3uQiF_4")
    updater.start_polling()
    updater.idle()


# https://webhook.site/48184ba5-39e5-4f29-bc4c-bb8cb7790f22
main()
