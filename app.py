import telebot as tb
import logging
import random as rnd
import re
import sys

from telebot.types import Message
from logging import StreamHandler, Formatter

from conf import Config

conf = Config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


def have_stop_phrase(message: str) -> bool:
    message_text = re.sub(conf.CLEAN_SENTENCE_PATTERN, '', message.lower())
    message_words = set(message_text.split(' '))

    has_censor_symbol = re.compile(conf.CENSOR_PATTERN)

    if any(word in message_text for word in conf.STOP_PHRASES):
        return True

    if has_censor_symbol.search(message_text):
        for word in message_words:
            if has_censor_symbol.search(word):
                clean_word = re.sub(conf.CENSOR_PATTERN, '', word)
                if any(scw in clean_word for scw in conf.STOP_CENSOR_PHRASES):
                    return True

    return False


def create_bot(api: str) -> tb.TeleBot:
    bot = tb.TeleBot(api)

    @bot.message_handler(commands=['soldier_mod'])
    def handler_login(message):
        conf.SOLDIER_MOD = not conf.SOLDIER_MOD
        bot.send_message(message.from_user.id, f"Игорь Стрелков переведен в статус: {conf.SOLDIER_MOD}")

    @bot.message_handler(commands=['soldier_mod_status'])
    def handler_login(message):
        bot.send_message(message.from_user.id, f"Игорь Стрелков в статусе: {bool(conf.SOLDIER_MOD)}")

    @bot.message_handler(
        func=lambda message: message.from_user.id in conf.TARGET_TG_ID,
        content_types=['text', 'sticker', 'photo', 'document']
    )
    @bot.edited_message_handler(func=lambda message: message.from_user.id in conf.TARGET_TG_ID)
    def echo_message(message: Message) -> None:
        if conf.SOLDIER_MOD:
            if message.content_type == 'text':
                message_text = re.sub(conf.CLEAN_SENTENCE_PATTERN, '', message.text.lower())
                if message_text not in conf.SOLDIER_MOD_PHRASES:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(conf.CHANNEL_ID, f'🪖 <i>"{message.text}"</i>', parse_mode='HTML')
                    bot.send_message(
                        message.chat.id,
                        rnd.choice(conf.BOT_SOLDIER_PROSES)
                    )
            elif message.content_type == 'photo':
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(
                    message.chat.id,
                    rnd.choice(conf.BOT_SOLDIER_PROSES)
                )
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, 'Улыбышев! Отставить!')
            return None

        if message.content_type == 'sticker' and message.sticker.set_name in conf.IGNORED_STICKERS:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(conf.CHANNEL_ID, '📄')
            bot.send_sticker(conf.CHANNEL_ID, message.sticker.file_id)
            logger.info('sticker has been removed')
        elif message.content_type == 'text':
            event_type = 'edit' if message.edit_date else 'new'

            logger.info('[%s] MSG: %s' % (event_type, message.text))
            if have_stop_phrase(message.text):
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(conf.CHANNEL_ID, f'<b>[{event_type}]</b>🤬 <i>"{message.text}"</i>', parse_mode='HTML')
                logger.info('stop word was detected')

    return bot


def main():
    bot = create_bot(conf.BOT_API_TOKEN)
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
