# from main import bot
#
# ONE_TRON = 1000000
# from tronpy import Tron
# from tronpy.keys import PrivateKey
#
# PRIVATE_KEY = "009faab68456edf92132cc74a580316d159bdc10a544bda7f82a52175968a323"
# MY_ADDRESS = "TSPZcEraokyNAuFR4Shgyn5D4ycsWjJhrL"
# # connect to the Tron blockchain
# client = Tron()
#
#
# def is_valid(address):
#     is_address = client.is_address(str(address))
#     return is_address
#
#
# def withdraw(update, context, address, value):
#     priv_key = PrivateKey(bytes.fromhex(PRIVATE_KEY))
#
#     # create transaction and broadcast it
#     # people = mydb['people']
#     # people.find_one({'_id':update.message.chat_id},{"$d"})
#     txn = (
#         client.trx.transfer(MY_ADDRESS, str(address), int(value * ONE_TRON))
#             .memo("Transaction Description")
#             .build()
#             .inspect()
#             .sign(priv_key)
#             .broadcast()
#     )
#     # wait until the transaction is sent through and then return the details
#     result = txn.wait()
#     bot.sendMessage(chat_id=update.message.chat_id, text=f"Transaction successful!\n\n"
#                                                          f"Transaction hash(TXID) : <code>{result['id']}</code>\n\n"
#                                                          f"Tron scan: https://tronscan.org/#/transaction/{result['id']}")
