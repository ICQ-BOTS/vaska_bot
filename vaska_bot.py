# -*- coding: utf-8 -*-
from handlers import *
from my_filter import Filter
from mailru_im_async_bot.bot import Bot
from mailru_im_async_bot.handler import StartCommandHandler, MessageHandler, CommandHandler, DefaultHandler, BotButtonCommandHandler, NewChatMembersHandler, LeftChatMembersHandler
from logging.config import fileConfig
from pid import PidFile
import wolframalpha
import asyncio
import logging
import sys
import os


configs_path = os.path.realpath(os.path.dirname(sys.argv[0])) + "/"

# Get config path from args
if len(sys.argv) > 1:
	configs_path = sys.argv[1]

if not os.path.isfile(os.path.join(configs_path, "logging.ini")):
	raise FileExistsError(f"File logging.ini not found in path {configs_path}")

logging.config.fileConfig(os.path.join(configs_path, "logging.ini"), disable_existing_loggers=False)
log = logging.getLogger(__name__)
loop = asyncio.get_event_loop()



NAME = "vaska"
TOKEN = '001.2918970001.1540231839:753423284'
APP_ID = "Y2Q635-YXJJYT8HL9"

client = wolframalpha.Client(APP_ID)
bot = Bot(token=TOKEN, name=NAME)

# Register your handlers here
# ---------------------------------------------------------------------

bot.dispatcher.add_handler(StartCommandHandler(
		callback=new_start_bot
	)
)
bot.dispatcher.add_handler(MessageHandler(
		callback=sticker,
		filters=Filter.sticker
	)
)
bot.dispatcher.add_handler(MessageHandler(
		callback=media,
		filters=Filter.media
	)
)
bot.dispatcher.add_handler(MessageHandler(
		callback=ask,
		filters=Filter.regexp('(?i)получить(.*?)отве(т)|найти(.*?)решени(е|я)|(реш(и|ить)|помоги)(.*?)(приме(р|ы)|зада|мате|физ|хим|дома)')
	)
)
bot.dispatcher.add_handler(MessageHandler(
        callback=help_mi, 
        filters=Filter.chaotic_args(['что', 'ты', ['умеешь', 'умешь', 'умеешь?', 'умешь?']])
    )
)
bot.dispatcher.add_handler(MessageHandler(
        callback=write_text, 
        filters=Filter.chaotic_args([['сделай', 'напиши'], ['конспект', 'сочинение']])
    )
)

bot.dispatcher.add_handler(CommandHandler(
		callback=add_phrases, 
		command='addPhrases'
    )
)

bot.dispatcher.add_handler(CommandHandler(
		callback=add_answer, 
		command='addAnswer'
    )
)

bot.dispatcher.add_handler(MessageHandler(
		callback=rand_answer,
		filters=Filter.regexp(r'(?i).+\?$(?<!что мне задали\?)(?<!что ты умеешь\?)(?<!что ты умешь\?)')
	)
)

bot.dispatcher.add_handler(DefaultHandler(
	    callback=def_phrases
	)
)

bot.dispatcher.add_handler(BotButtonCommandHandler(
	callback=button_1,
	filters=Filter.callback_data('call_back_id_1')
	)
)

bot.dispatcher.add_handler(BotButtonCommandHandler(
	callback=button_2,
	filters=Filter.callback_data('call_back_id_2')
	)
)
bot.dispatcher.add_handler(BotButtonCommandHandler(
	callback=button_3,
	filters=Filter.callback_data('call_back_id_3')
	)
)
bot.dispatcher.add_handler(BotButtonCommandHandler(
	callback=button_4,
	filters=Filter.callback_data('call_back_id_4')
	)
)
bot.dispatcher.add_handler(BotButtonCommandHandler(
	callback=def_phrases,
	filters=Filter.callback_data('call_back_id_5')
	)
)


with PidFile(NAME):
	try:
		loop.create_task(bot.start_polling())
		loop.run_forever()
	finally:
		loop.close()