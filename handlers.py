from tarantool_utils import *
from random import randint, choice
from PIL import Image, ImageDraw, ImageFont
import numexpr as ne
import asyncio
import json
import time
import sys
import os
import re


async def new_start_bot(bot, event):
	await bot.send_text(
			chat_id=event.from_chat,
			text="""Привет! 🙃
Я — Васька, твой школьный друг и помощник. Могу решать математику, делать за тебя письменные конспекты и просто болтать :) 

Если хочешь узнать обо всех доступных командах, спроси меня: Васька, что ты умеешь?"""
		)	


async def help_mi(bot, event):
	await bot.send_text(
			chat_id=event.from_chat,
			text="""📒 Помоги с математикой — присылай пример или уравнение, а я скажу правильный ответ 

📕 Напиши конспект — присылай текст, который нужно написать от руки, а я пришлю фото с написанным текстом. 
"""
		)	


async def def_phrases(bot, event):
	user = User(user_id=event.data['from']['userId']).get()
	if user.old_mes['text']:
		# Если человек отправляет следующим сообщением текст
		await write_text(bot, event)
	else:
		if user.example:
			is_text = re.search(r'[^\W\d]', event.text)
			# Проверка есть ли буквы в тексте
			event.text = event.text.replace(':', '/')
			if is_text:
				await wolf_ram(bot, event)					
			else:
				try:
					await bot.send_text(
						chat_id=event.from_chat,
						text=round(float(ne.evaluate(event.text)), 5)
					)
					await bot.send_text(
						chat_id=event.from_chat,
						text="Есть еще не решенные примеры?",
						inline_keyboard_markup="{}".format(json.dumps([
							[{"text": "Да", "callbackData": "call_back_id_1"}],
							[{"text": "Нет", "callbackData": "call_back_id_5"}]
						]))
					)					
				except Exception as e:
					await wolf_ram(bot, event)		
					
			user.space[1] = False
			user.save()	
		else:
			chat_type = event.data['message']['chat']['type'] if event.data.get('message') else event.data['chat']['type']
			chat_id = event.data['message']['chat']['chatId'] if event.data.get('message') else event.data['chat']['chatId']
			if chat_type == 'private':
				await bot.send_text(
					chat_id=chat_id,
					text=choice(space_phrases.select())[1]
				)


async def sleep_send(bot, event):
	await bot.send_actions(chat_id=event.from_chat, actions='typing')
	await asyncio.sleep(2)


async def wolf_ram(bot, event):
	answer = await bot.send_text(
		chat_id=event.from_chat,
		text="Немножко подожди, сейчас все посчитаю"
	)
	await sleep_send(bot, event)
	try:
		answers = await wolframalpha_send(bot, client.query(event.text), event)
		if answers:
			await bot.edit_text(
				msg_id=answer['msgId'],
				chat_id=event.from_chat,
				text=answers
			)
			await bot.send_text(
				chat_id=event.from_chat,
				text="Есть еще не решенные примеры?",
				inline_keyboard_markup="{}".format(json.dumps([
					[{"text": "Да", "callbackData": "call_back_id_1"}],
					[{"text": "Нет", "callbackData": "call_back_id_5"}]
				]))
			)				
		else:
			await bot.edit_text(
				msg_id=answer['msgId'],
				chat_id=event.from_chat,
				text=f"Не смог решить пример:\n{event.text}\nОтправил разработчику, чтоб научил считать и такое тоже."
			)
	except Exception as e:
		await bot.edit_text(
				msg_id=answer['msgId'],
				chat_id=event.from_chat,
				text=f"Не смог решить пример:\n{event.text}\nОтправил разработчику, чтоб научил считать и такое тоже."
			)
		for admin in ['752284535']:
			await bot.send_text(
				chat_id=admin,
				text="Не смог решить пример:\n" + event.text
			)			
	

async def wolframalpha_send(bot, res, event, assumption=None):
	if res.success == 'true':
		text = ''
		if assumption is None and 'assumptions' in list(res.keys()):
			res = client.query(event.text, assumption=list(res.assumptions)[0]['assumption']['value'][1]['@input'])
			return await wolframalpha_send(bot, res, event, assumption=True)
		for pod in res.pods:
			if pod.title in ['Decimal approximation', 'Result', 
			'Solutions', 'Solution', 'Exact result', 'Repeating decimal']:
				for sub in pod.subpods:
					sub.plaintext = sub.plaintext[:-3] if sub.plaintext[-3:] == '...' else sub.plaintext
					text += str(round(float(sub.plaintext), 5)) + "\n" if sub.plaintext.replace('.', '', 1).isdigit() else sub.plaintext + "\n"

		if text == '':
			for admin in ['752284535']:
				await bot.send_text(
					chat_id=admin,
					text="Не смог решить пример:\n" + event.text
				)				
			return False
		return text	
	else:
		return False	


async def rand_answer(bot, event):
	if event.data['chat']['type'] == 'private':
		await sleep_send(bot, event)
		await bot.send_text(
				chat_id=event.from_chat,
				text=choice(space_answer.select())[1]
			)


async def ask(bot, event):
	await sleep_send(bot, event)
	await bot.send_text(
		chat_id=event.from_chat,
		text="Нужна помощь? Сейчас я могу помочь только с математикой, но я постоянно учусь:)",
		inline_keyboard_markup="{}".format(json.dumps([
			[{"text": "Да", "callbackData": "call_back_id_1"}],
			[{"text": "Нет", "callbackData": "call_back_id_2"}]
		])))


async def sticker(bot, event):
	if event.data['from']['userId'] in ['752284535']:
		#Проверка на админов!
		space_sticker.insert((None, event.text.split('/')[-1]))
		await bot.send_text(
				chat_id=event.from_chat,
				text='Добавил стикер!'
			)		
	elif event.data['chat']['type'] == 'private':
		await sleep_send(bot, event)
		await bot.send_text(
				chat_id=event.from_chat,
				text='https://files.icq.net/get/' + choice(space_sticker.select())[1]
			)


async def media(bot, event):
	if event.data['chat']['type'] == 'private':
		await sleep_send(bot, event)
		await bot.send_text(
			chat_id=event.from_chat,
			text="Ой, ой. А можно все тоже самое, но текстом?"
			)	


async def button_1(bot, event):
	await bot.answer_callback_query(query_id=event.data['queryId'])
	await bot.send_actions(chat_id=event.data['message']['chat']['chatId'], actions='typing')
	await asyncio.sleep(2)
	user = User(user_id=event.data['from']['userId']).get()
	user.space[1] = True
	user.save()
	await bot.send_text(
		chat_id=event.data['message']['chat']['chatId'],
		text="Присылай пример - я решу 😉"
		)  


async def button_2(bot, event):
	await bot.answer_callback_query(query_id=event.data['queryId'])
	await bot.send_actions(chat_id=event.data['message']['chat']['chatId'], actions='typing')
	await asyncio.sleep(2)
	await bot.send_text(
		chat_id=event.data['message']['chat']['chatId'],
		text="Чем ещё могу помочь?"
		)  


async def button_3(bot, event):
	await bot.answer_callback_query(query_id=event.data['queryId'])
	await bot.send_actions(chat_id=event.data['message']['chat']['chatId'], actions='typing')
	await asyncio.sleep(2)
	user = User(user_id=event.data['from']['userId']).get()
	if user.old_mes['text']:
		user.old_mes['text'] = user.old_mes['text'].replace('–', '-')	
		args = user.old_mes['text'].split(' ')
		# ищем слово конспект, и проверяем то что оно стоит в конце
		index_text = args.index(args[1]) + 1 if args.index(args[1]) else 0	
		name = new_foto(args[index_text:], fon=True)
		text = 'Готово. С тебя шоколадка/Лови конспект/Получите, распишитесь/Вуаля/И не отличишь, да?'
		with open(name, 'rb') as file:
			await bot.send_file(
				chat_id=event.data['message']['chat']['chatId'],
				file=file, 
				caption=choice(text.split('/'))
				)
		user.old_mes['text'] = None
		os.remove(name)		
	else:
		await bot.send_text(
			chat_id=event.data['message']['chat']['chatId'],
			text='Пришли текст, который нужно написать от руки - я пришлю тебе скан'
		)	
		user.old_mes['text'] = 'Напиши конспект'
	user.save()


async def button_4(bot, event):
	await bot.answer_callback_query(query_id=event.data['queryId'])
	await bot.send_actions(chat_id=event.data['message']['chat']['chatId'], actions='typing')
	await asyncio.sleep(2)
	user = User(user_id=event.data['from']['userId']).get()
	if user.old_mes['text']:
		user.old_mes['text'] = user.old_mes['text'].replace('–', '-')	
		args = user.old_mes['text'].split(' ')
		# ищем слово конспект, и проверяем то что оно стоит в конце
		index_text = args.index(args[1]) + 1 if args.index(args[1]) else 0		
		name = new_foto(args[index_text:], fon=False)
		text = 'Готово. С тебя шоколадка/Лови конспект/Получите, распишитесь/Вуаля/И не отличишь, да?'
		with open(name, 'rb') as file:
			await bot.send_file(
				chat_id=event.data['message']['chat']['chatId'],
				file=file, 
				caption=choice(text.split('/'))
				)
		user.old_mes['text'] = None
		os.remove(name)	
	else:
		await bot.send_text(
			chat_id=event.data['message']['chat']['chatId'],
			text='Пришли текст, который нужно написать от руки - я пришлю тебе скан'
		)	
		user.old_mes['text'] = 'Напиши конспект'
	user.save()


async def add_phrases(bot, event):
	if event.data['from']['userId'] in ['752284535']:
		await sleep_send(bot, event)
		for c in event.text[12:].split('\n'):
			space_phrases.insert((None, c))		
		await bot.send_text(
			chat_id=event.from_chat,
			text="Добавил новую фразу - " + '\n'.join(event.text[12:].split('\n'))
		) 


async def add_answer(bot, event):
	if event.data['from']['userId'] in ['752284535']:
		await sleep_send(bot, event)
		for c in event.text[11:].split('\n'):
			space_answer.insert((None, c))
		await bot.send_text(
			chat_id=event.from_chat, 
			text="Добавил новый ответы - " + '\n'.join(event.text[11:].split('\n'))
		)


def scale_image(input_image_path, width=None, height=None):
	original_image = Image.open(input_image_path)
	w, h = original_image.size

	if width and height:
		max_size = (width, height)
	elif width:
		max_size = (width, h)
	elif height:
		max_size = (w, height)
	else:
		raise RuntimeError('Width or height required!')
 
	original_image.thumbnail(max_size, Image.ANTIALIAS)
	return original_image


def separation_text(args, count):
	len_str = 0
	text_list = ['']
	for index, c in enumerate(args):
		if len(text_list[-1].split('\n')) >= 2:
			split = text_list[-1].split('\n')
			text_list[-1] = split[0]
			len_str = len(split[1]) + 8
			text_list.append("—" + split[1])
		else:
			len_str += len(c) + 1
		if len_str < count:
			text_list[-1] +=  f" {c}"
		else:
			len_str = len(c) + 1
			text_list.append(c)

	return [c.strip() for c in text_list]


def new_foto(args, fon=True):
	configs_path = os.path.realpath(os.path.dirname(sys.argv[0])) + "/"
	if fon:
		base = scale_image(configs_path + 'fon/' + str(randint(1, 4)) + '.jpg', height=450).convert('RGBA')
	fnt = ImageFont.truetype(configs_path + 'Brush font one.otf', size=16)
	text = separation_text(args, 50)
	text[0] = "—" + text[0]
	if len(text) >= 23:
		if fon:
			tetrad = Image.open(configs_path + 'notebook/2.png').convert('RGBA')
			draw = ImageDraw.Draw(tetrad)
			draw.multiline_text((60, 11), '\n'.join(text[:17]), font=fnt, fill=(5, 4, 170, 165), spacing=8)
			draw.multiline_text((335, 12),  '\n'.join(text[17:34]), font=fnt, fill=(5, 4, 170, 165), spacing=8)	
		else:
			tetrad = Image.open(configs_path + 'notebook/4.png').convert('RGBA')
			draw = ImageDraw.Draw(tetrad)
			draw.multiline_text((53, 3), '\n'.join(text[:17]), font=fnt, fill=(5, 4, 170, 165), spacing=8)
			draw.multiline_text((335, 12),  '\n'.join(text[17:34]), font=fnt, fill=(5, 4, 170, 165), spacing=8)	

		rand = randint(1, 3)
		if rand == 1:
			sh21 = scale_image(configs_path + 'foto/21.png', height=265)
			tetrad.paste(sh21, (600, 100),  sh21)
		elif rand == 2:
			sh22 = scale_image(configs_path + 'foto/22.png', height=265)
			tetrad.paste(sh22, (620, 100),  sh22)

		x_base_paste = 70
		y_base_paste = 25
	else:
		fnt = ImageFont.truetype(configs_path + 'Brush font one.otf', size = 29)
		if fon:
			tetrad = Image.open(configs_path + 'notebook/1.png').convert('RGBA')
			draw = ImageDraw.Draw(tetrad)
			draw.multiline_text((33, 61), '\n'.join(text), font=fnt, fill=(5, 4, 170, 165), spacing=8)
		else:
			tetrad = Image.open(configs_path + 'notebook/3.png').convert('RGBA')
			draw = ImageDraw.Draw(tetrad)
			draw.multiline_text((33, 3), '\n'.join(text), font=fnt, fill=(5, 4, 170, 165), spacing=8)
		rand = randint(1, 3)
		if rand == 1:
			sh21 = scale_image(configs_path + 'foto/21.png', height=465)
			tetrad.paste(sh21, (550, 150),  sh21)
		elif rand == 2:
			sh22 = scale_image( configs_path + 'foto/22.png', height=565)
			tetrad.paste(sh22, (570, 100),  sh22)	
		x_base_paste = 0
		y_base_paste = 0
		if fon:
			base = base.resize((500,520))
			tetrad.thumbnail((402,664), Image.ANTIALIAS)

	sh1 = scale_image(configs_path + 'foto/sh1.png', height=200)
	sh2 = scale_image(configs_path + 'foto/sh2.png', height=150)

	i = 0
	while i <= randint(0, 2):
		tetrad.paste(sh1, (randint(0, tetrad.size[0]), randint(0, tetrad.size[1])),  sh1)
		i += 1

	i = 0
	while i <= randint(0, 5):
		sh3 = scale_image(configs_path + 'foto/' + str(randint(1, 5)) + '.png', height=10).convert('RGBA')
		tetrad.paste(sh3, (randint(0, tetrad.size[0] - 50), randint(0, tetrad.size[1] - 20)),  sh3)
		i += 1

	random_name = configs_path + 'img/' + str(randint(0, 9999999)) + '_sfoto.png'
	if fon:
		base.paste(tetrad, (x_base_paste, y_base_paste),  tetrad)
		base.save(random_name)
	else:
		tetrad.save(random_name)
	return random_name


async def write_text(bot, event):
	await sleep_send(bot, event)
	user = User(user_id=event.data['from']['userId']).get()
	start_time = time.time()
	if user.old_mes['text'] is None:
		user.old_mes['text'] = event.data['text'].replace('ё', 'е')
	else:
		user.old_mes['text'] += " " + event.data['text'].replace('ё', 'е')
	text = user.old_mes['text']
	args = text.lower().split()

	# ищем 2 слово, и проверяем то что оно стоит в конце
	index_text = args.index(args[1]) + 1 if args.index(args[1]) else 0
	if index_text == len(args):
		await bot.send_text(
			chat_id=event.from_chat,
			text='Пришли текст, который нужно написать от руки - я пришлю тебе скан'
		)
	elif index_text <= len(args):
		await bot.send_text(
			chat_id=event.from_chat,
			text="Нужен фон стола?",
			inline_keyboard_markup="{}".format(json.dumps([
				[{"text": "Да", "callbackData": "call_back_id_3"}],
				[{"text": "Нет", "callbackData": "call_back_id_4"}]
			]))
		)
	user.save()
	