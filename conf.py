from datetime import datetime, timedelta


class Config:
    CHANNEL_ID = -1001754918482
    SISYAN_ID = -1001786724046
    # SISYAN_ID = -1001678203307
    SOLDIER_MOD = 0
    LAST_SOLDER_MESSAGE = datetime.now() - timedelta(minutes=1)
    SOLDIER_MOD_SPAM_TIME = timedelta(minutes=1)
    CENSOR_PATTERN = '[@#$%&*^]'
    CLEAN_SENTENCE_PATTERN = '[-,[]|!?:;.]'

    BOT_API_TOKEN = '5390283097:AAGgMJOSY99txo4TyblueDni8qmq02JMec4'
    # TARGET_TG_ID = (316237594, )
    TARGET_TG_ID = (444049905, )

    IGNORED_STICKERS = (
        'sp66fdc68dc48f640d86440992ce15db67_by_stckrRobot',
        'SoyaCorp_ChatBubbles',
        'floppa_chirpani',
    )

    STOP_PHRASES = ['bljat', 'ватник', '*internal screaming*', '*vine_boom.wav*', 'cушилка', 'bruh', 'не отношусь',
                    'душнила', 'блетб', 'блеат', 'cук(', 'сук(' 'наwhyя', 'наwhyя', 'стицкер', '0)0']

    STOP_CENSOR_PHRASES = ['314д', '314с', '314з','fck', 'fuck', 'аним',
                           'безю', 'бл', 'бь', 'г', 'дроч', 'еб', 'жоп', 'ипа', 'муд', 'нй', 'пизд', 'секс',
                           'сук', 'хам', 'хер', 'хи', 'хре', 'ху', 'xу', 'хy', 'xy', 'хя', 'член', 'ёб']

    SOLDIER_MOD_PHRASES = ['так точно', 'никак нет']

    BOT_SOLDIER_PROSES = [
        'УЛЫБЫШЕВ, ОТСТАВИТЬ ИСПРАЖНЯТЬСЯ ПЕРЕД СТАРШИМИ ПО ЗВАНИЮ КРЕЙСЕР ТЕБЕ В БУХТУ!\n"Так точно!" или "Никак нет!" и ни слова больше!',
        'Улыбышев! Отставить разговоры в строю!\n"Так точно!" или "Никак нет!" и ни слова больше!',
        'Еще слово и мобилизован! Улыбышев отставить!\nТак точно!" или "Никак нет!" и ни слова больше!',
        'Отставить разговоры Улыбышев! Здесь тебе не курорт калаш мне в зад, это армия, тротил мне в жопу!\n"Так точно!" или "Никак нет!" и ни слова больше!',
        'Улыбышев, сто нарядов вне очереди! Отставить разговоры!\n"Так точно!" или "Никак нет!" и ни слова больше!',
        'Посмотри на себя, зеленый, женоподобный, безмускульный щенок гав-гав, к мамочке небось хочешь, домой, СИСЮ ХОЧЕШЬ? Отставить разговоры в строю!\n"Так точно!" или "Никак нет!" и ни слова больше!'
    ]

    SYMBOL = ('х', 'у', 'б')
    ALTERNATIVE_SYMBOL = ('x', 'y', '6')
    SYMBOL_MAP = dict(zip(ALTERNATIVE_SYMBOL, SYMBOL))