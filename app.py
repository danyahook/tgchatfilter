import telebot as tb
import typing as t
import logging
import os
import pytesseract
import random as rnd
import re
import sys

from datetime import datetime
from io import BytesIO
from telebot.types import Message
from logging import StreamHandler, Formatter
from PIL import Image

from conf import Config

conf = Config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


def have_stop_phrase(message: str, reply_text: t.Union[str, None] = None) -> bool:
    if message is None or reply_text is None:
        return False
    message_text = re.sub(conf.CLEAN_SENTENCE_PATTERN, '', message.lower())

    # Плохо, но пока что так
    re_question_words = re.findall("што|что|кто\w+", message_text.lower())
    if reply_text and re_question_words:
        reply_text_clear = re.sub(conf.CLEAN_SENTENCE_PATTERN, '', reply_text.lower())
        for question_word in re_question_words:
            if re.sub(r'што|что|кто', '', question_word) in reply_text_clear:
                return True

    message_words = set(message_text.split(' '))

    has_censor_symbol = re.compile(conf.CENSOR_PATTERN)

    if any(word in message_text for word in conf.STOP_PHRASES):
        return True

    if has_censor_symbol.search(message_text):
        for word in message_words:
            if has_censor_symbol.search(word):
                clean_word = re.sub(conf.CENSOR_PATTERN, '', word)
                alt_set = set(clean_word) & set(conf.ALTERNATIVE_SYMBOL)
                for letter in alt_set:
                    clean_word = clean_word.replace(letter, conf.SOLDIER_MOD[letter])
                if any(scw in clean_word for scw in conf.STOP_CENSOR_PHRASES):
                    return True

    return False


def create_bot(api: str) -> tb.TeleBot:
    bot = tb.TeleBot(api)

    @bot.message_handler(content_types=['photo'], func=lambda message: message.caption == '/send_img')
    def send_image(message):
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_caption = message.caption.removeprefix('/send_img')
        bot.send_photo(chat_id=conf.SISYAN_ID, photo=downloaded_file, caption=image_caption)

    @bot.message_handler(content_types=['text'], commands=['send_text'])
    def send_text(message):
        bot.send_message(chat_id=conf.SISYAN_ID, text=message.text.removeprefix('/send_text'))

    @bot.message_handler(commands=['soldier_mod'])
    def handler_soldier_mod(message):
        conf.SOLDIER_MOD = not conf.SOLDIER_MOD
        bot.send_message(message.from_user.id, f"Игорь Стрелков переведен в статус: {conf.SOLDIER_MOD}")

    @bot.message_handler(commands=['soldier_mod_status'])
    def handler_soldier_mod_status(message):
        bot.send_message(message.from_user.id, f"Игорь Стрелков в статусе: {bool(conf.SOLDIER_MOD)}")

    @bot.message_handler(commands=['get_link'])
    def get_invite_link(message):
        link = bot.export_chat_invite_link(chat_id=conf.SISYAN_ID)
        bot.send_message(message.from_user.id, link)

    @bot.message_handler(
        func=lambda message: True,
        content_types=['text', 'sticker', 'photo', 'document']
    )
    @bot.edited_message_handler(func=lambda message: True)
    def echo_message(message: Message) -> None:
        logger.info(f'[MSG LOG] ({message.from_user.first_name}): {message.text}')
        if message.from_user.id in conf.TARGET_TG_ID:
            event_type = 'edit' if message.edit_date else 'new'

            if conf.SOLDIER_MOD:
                if message.content_type == 'text':
                    message_text = re.sub(conf.CLEAN_SENTENCE_PATTERN, '', message.text.lower())
                    if message_text not in conf.SOLDIER_MOD_PHRASES:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(conf.CHANNEL_ID, f'🪖 <i>"{message.text}"</i>', parse_mode='HTML')
                        if datetime.now() - conf.LAST_SOLDER_MESSAGE > conf.SOLDIER_MOD_SPAM_TIME:
                            bot.send_message(
                                message.chat.id,
                                rnd.choice(conf.BOT_SOLDIER_PROSES)
                            )
                            conf.LAST_SOLDER_MESSAGE = datetime.now()
                elif message.content_type == 'photo':
                    bot.delete_message(message.chat.id, message.message_id)
                    if datetime.now() - conf.LAST_SOLDER_MESSAGE > conf.SOLDIER_MOD_SPAM_TIME:
                        bot.send_message(
                            message.chat.id,
                            rnd.choice(conf.BOT_SOLDIER_PROSES)
                        )
                        conf.LAST_SOLDER_MESSAGE = datetime.now()
                else:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, 'Улыбышев! Отставить!')
                return None

            if message.content_type == 'sticker' and message.sticker.set_name in conf.IGNORED_STICKERS:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(conf.CHANNEL_ID, '📄')
                bot.send_sticker(conf.CHANNEL_ID, message.sticker.file_id)
                logger.info('sticker has been removed')
            elif message.content_type == 'photo':
                file_id = message.photo[-1].file_id
                file_info = bot.get_file(file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                image_stream = BytesIO(downloaded_file)
                img = Image.open(image_stream)
                img_text = pytesseract.image_to_string(img, config='--psm 4', lang='rus')
                logger.info('[%s] MSG: %s' % (event_type, message.caption))
                if have_stop_phrase(img_text):
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_photo(conf.CHANNEL_ID, img, caption=f'<b>[{event_type}]</b>🤬📸', parse_mode='HTML')
                    logger.info('stop word was detected on photo')
                    return
                elif have_stop_phrase(message.caption):
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(conf.CHANNEL_ID, f'<b>[{event_type}]</b>🤬 <i>"{message.caption}"</i>',
                                     parse_mode='HTML')
                    logger.info('stop word was detected')

            elif message.content_type == 'text':
                logger.info('[%s] MSG: %s' % (event_type, message.text))
                reply_text = message.reply_to_message.text if message.reply_to_message else None
                if have_stop_phrase(message.text, reply_text):
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(conf.CHANNEL_ID, f'<b>[{event_type}]</b>🤬 <i>"{message.text}"</i>',
                                     parse_mode='HTML')
                    logger.info('stop word was detected')

    return bot


def main():
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    bot = create_bot(conf.BOT_API_TOKEN)
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
