import logging
from telebot.credentials import bot_token
from telegram.error import BadRequest
from info.playerinfo import players, Player
from files import links, script

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Message,
    Update,
    Bot)
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

NAME_ENTERING, HANDLING_NAME, CONSTRUCTION, GOOD_MORNING, CONTINUE, NOVEL, INFO_BUTTONS, GLOSSARY_BUTTONS, SAVE_FEEDBACK, FEEDBACK_BUTTON = range(
    10)

bot = Bot(bot_token)
global player
global lang
last_message = {}


async def set_player(player_id):
    global player
    player = players[player_id]
    global lang
    lang = player.get_language()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """tarts the conversation and asks to choose the language or loads progress of the player"""
    players[update.message.chat_id] = Player(player_id=update.message.chat_id, name=update.message.from_user.first_name)
    players[update.message.chat_id].load()
    await set_player(update.message.chat_id)
    if player.get_progress() >= 2:
        return await novel(update, context, "-2")
    reply_keyboard = [["Українська", "Русский"]]
    await update.message.reply_text("Оберіть мову",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return NAME_ENTERING


async def enterName(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the language choice and asks for name"""
    await set_player(update.message.chat_id)
    if update.message.text == "Русский":
        player.set_language(script.ru)
    reply_keyboard = [[f"{player.get_name()}", script.user_replies[player.get_language()][-1]]]
    await update.message.reply_text(script.bot_messages[player.get_language()][0],
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return HANDLING_NAME


async def handleName(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the name choosing"""
    await set_player(update.message.chat_id)
    if update.message.text == script.user_replies[lang][-1]:
        await update.message.reply_text(script.bot_messages[lang][1])
        return GOOD_MORNING
    else:
        return await greetings(update, context)


async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Greets the player, launches the story"""
    await set_player(update.message.chat_id)
    player.set_name(update.message.text)
    player.set_progress(2)
    player.save_all()
    reply_keyboard = [["Давай!"]]
    await update.message.reply_text(text=script.bot_messages[lang][2].format(player.get_name()),
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                     one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return NOVEL


async def novel(update: Update, context: ContextTypes.DEFAULT_TYPE, choice="-2") -> int:
    """The wheel of the main story"""
    continu3 = [[InlineKeyboardButton(script.user_replies[lang][-2], callback_data="-2")]]
    progress = player.get_progress() + 1
    global last_message
    if progress > 3 and (update.message is None or update.message.text != '/start'):
        try:
            await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
        except(BadRequest):
            None
    else:
        await set_player(update.message.chat_id)
        menu = [[script.user_replies[lang][i] for i in range(-3, -6, -1)]]
        hoax_message = await bot.send_message(chat_id=player.get_id(), text='🕓',
                                              reply_markup=ReplyKeyboardMarkup(menu,
                                                                               resize_keyboard=True))
    args = {'is_text': True,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            'markup': InlineKeyboardMarkup(continu3)
            }
    if progress in [3, 30, 45, 81, 108, 115]:
        args['is_text'] = False
        args['is_photo'] = True
        if progress == 3:
            args['link'] = links.link_begin + links.dream
        elif progress == 30:
            args['link'] = links.link_begin + links.room
        elif progress == 45:
            args['link'] = links.link_begin + links.city
        elif progress == 81:
            args['link'] = links.link_begin + links.assembly_hall
        elif progress == 108:
            args['link'] = links.link_begin + links.street
        elif progress == 115:
            args['link'] = links.link_begin + links.workplace
    elif progress in [29]:
        args['is_text'] = False
        args['is_voice'] = True
        if progress == 29:
            args['link'] = links.link_begin + links.alarmclock
    elif progress in [53, 96, 121, 141, 168, 170, 172]:
        args['is_text'] = False
        args['is_sticker'] = True
        if progress == 53:
            args['link'] = links.link_begin + links.vika
        elif progress == 96:
            args['link'] = links.link_begin + links.bestofurendo
        elif progress == 121:
            args['link'] = links.link_begin + links.nastya
        elif progress == 141:
            args['link'] = links.link_begin + links.tanya
        elif progress == 168:
            args['link'] = links.link_begin + links.vikachibi
        elif progress == 170:
            args['link'] = links.link_begin + links.nastyachibi
        elif progress == 172:
            args['link'] = links.link_begin + links.tanyachibi
    elif progress == 19:
        yesno = [
            [
                InlineKeyboardButton(script.user_replies[lang][1], callback_data="1"),
                InlineKeyboardButton(script.user_replies[lang][2], callback_data="2")
            ]
        ]
        args['markup'] = InlineKeyboardMarkup(yesno)
    elif progress == 103:
        saynotsay = [
            [
                InlineKeyboardButton(script.user_replies[lang][3], callback_data="3"),
                InlineKeyboardButton(script.user_replies[lang][4], callback_data="4")
            ]
        ]
        args['markup'] = InlineKeyboardMarkup(saynotsay)
    elif progress == 126:
        suresorry = [
            [
                InlineKeyboardButton(script.user_replies[lang][5], callback_data="5"),
                InlineKeyboardButton(script.user_replies[lang][6], callback_data="6")
            ]
        ]
        args['markup'] = InlineKeyboardMarkup(suresorry)
    elif progress == 153:
        freepay = [
            [
                InlineKeyboardButton(script.user_replies[lang][7], callback_data="7"),
                InlineKeyboardButton(script.user_replies[lang][8], callback_data="8")
            ]
        ]
        args['markup'] = InlineKeyboardMarkup(freepay)
    elif progress == 174:
        root = [
                [InlineKeyboardButton(script.user_replies[lang][9], callback_data="9")],
                [InlineKeyboardButton(script.user_replies[lang][10], callback_data="10")],
                [InlineKeyboardButton(script.user_replies[lang][11], callback_data="9")],
                [InlineKeyboardButton(script.user_replies[lang][12], callback_data="10")]
        ]
        args['markup'] = InlineKeyboardMarkup(root)
    elif choice == "2" or (choice == "-2" and (progress == 23 or progress == 158)) or choice == "6":
        progress += 3
    elif choice == "4" or (choice == "-2" and progress == 130):
        progress += 2
    elif choice == "-2" and progress == 106:
        progress += 1
    elif choice == "8":
        progress += 4
    try:
        args['text'] = script.bot_messages[lang][progress].format(player.get_name())
    except(KeyError):
        await in_development(update, context)
    try:
        last_message[player.get_id()] = await send_anything(args)
    except(UnboundLocalError):
        return 10
    player.set_progress(progress)
    player.save_progress()
    return CONTINUE


async def game_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and handles the buttons pressed"""
    query = update.callback_query
    await query.answer()
    await set_player(query.message.chat_id)
    if query.data == "3":
        player.increaseEP("Vika")
    elif query.data == "5":
        player.increaseEP("Nastya")
    elif query.data == "7":
        player.increaseEP("Tanya")
    if query.data in ["-2", "1", "3", "5", "7"]:
        return await novel(update, context)
    return await novel(update, context, query.data)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await set_player(update.message.chat_id)
    try:
        await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
    except:
        None
    await bot.send_sticker(chat_id=player.get_id(),
                           sticker=links.link_begin + links.error)
    await bot.send_message(chat_id=player.get_id(),
                           text=script.error[lang])
    return await start(update, context)


async def in_development(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot.send_animation(chat_id=player.get_id(),
                             animation=links.in_development,
                             caption=script.in_development[lang],
                             reply_markup=ReplyKeyboardRemove())


async def send_anything(args) -> Message:
    if args['is_text']:
        return await bot.send_message(chat_id=player.get_id(),
                                      text=args['text'],
                                      reply_markup=args['markup'],
                                      parse_mode=ParseMode(ParseMode.HTML))
    elif args['is_photo']:
        return await bot.send_photo(chat_id=player.get_id(),
                                    photo=args['link'],
                                    caption=args['text'],
                                    reply_markup=args['markup'],
                                    parse_mode=ParseMode(ParseMode.HTML))
    elif args['is_voice']:
        return await bot.send_voice(chat_id=player.get_id(),
                                    voice=args['link'],
                                    reply_markup=args['markup'])
    elif args['is_sticker']:
        await bot.send_sticker(chat_id=player.get_id(),
                               sticker=args['link'])
        return await bot.send_message(chat_id=player.get_id(),
                                      text=args['text'],
                                      reply_markup=args['markup'],
                                      parse_mode=ParseMode(ParseMode.HTML))


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE, choice="_") -> int:
    """Info menu"""
    try:
        await set_player(update.message.chat_id)
    except(AttributeError):
        None
    try:
        await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
    except(BadRequest):
        None
    progress = player.get_progress()

    choose_character = [[InlineKeyboardButton(script.user_replies[lang][-6], callback_data="-6")]]
    from_char_info_table = [
        [InlineKeyboardButton(script.user_replies[lang][-7], callback_data="-7")],
        [InlineKeyboardButton(script.user_replies[lang][-6], callback_data="-6")]
    ]
    args = {'is_text': False,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            }
    if choice == "_":
        args['is_text'] = True
        args['text'] = script.bot_messages[lang][-1]
        if progress >= 56:
            choose_character.insert(0, [InlineKeyboardButton(script.characters[lang][0], callback_data="Vika")])
        if progress >= 120:
            choose_character.insert(1, [InlineKeyboardButton(script.characters[lang][1], callback_data="Nastya")])
        if progress >= 161:
            choose_character.insert(2, [InlineKeyboardButton(script.characters[lang][2], callback_data="Tanya")])
        args['markup'] = InlineKeyboardMarkup(choose_character)
    else:
        args['is_sticker'] = True
        args['markup'] = InlineKeyboardMarkup(from_char_info_table)
        if choice == "Vika":
            if 56 <= progress:
                args['text'] = script.bot_messages[lang][-2].format(*script.characters_info[lang]["Vika"]["56-?"])
                args['link'] = links.link_begin + links.vika
        elif choice == "Nastya":
            if 120 <= progress:
                args['text'] = script.bot_messages[lang][-3].format(*script.characters_info[lang]["Nastya"]["120-?"])
                args['link'] = links.link_begin + links.nastya
        elif choice == "Tanya":
            if 161 <= progress:
                args['text'] = script.bot_messages[lang][-4].format(*script.characters_info[lang]["Tanya"]["161-?"])
                args['link'] = links.link_begin + links.tanya
    last_message[player.get_id()] = await send_anything(args)
    return INFO_BUTTONS


async def info_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles info menu choice"""
    query = update.callback_query
    await query.answer()
    await set_player(query.message.chat_id)
    await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id)
    if query.data == "-6":
        try:
            await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id - 1)
        except(BadRequest):
            None
        return await novel(update, context)
    elif query.data == "-7":
        await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id - 1)
        return await info(update, context, "_")
    else:
        return await info(update, context, query.data)


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles about menu choice"""
    try:
        await set_player(update.message.chat_id)
    except(AttributeError):
        None
    try:
        await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
    except(BadRequest):
        None
    args = {'is_text': True,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            'text': script.bot_messages[lang][-10],
            'markup': None
            }

    last_message[player.get_id()] = await send_anything(args)
    return SAVE_FEEDBACK


async def glossary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await set_player(update.message.chat_id)
    except(AttributeError):
        None
    try:
        await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
    except(BadRequest):
        None
    progress = player.get_progress()
    back_to_game = [[InlineKeyboardButton(script.user_replies[lang][-6], callback_data="-6")]]
    args = {'is_text': True,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            'text': script.glossary[lang][1],
            'markup': InlineKeyboardMarkup(back_to_game)
            }
    if 72 <= progress < 77:
        args['text'] = script.glossary[lang]["72-76"]
    elif 77 <= progress < 147:
        args['text'] = script.glossary[lang]["77-146"]
    elif 147 <= progress < 166:
        args['text'] = script.glossary[lang]["147-165"]
    elif 166 <= progress < 200:
        args['text'] = script.glossary[lang]["166-?"]
    last_message[player.get_id()] = await send_anything(args)
    return GLOSSARY_BUTTONS


async def glossary_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await set_player(query.message.chat_id)
    await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id)
    return await novel(update, context)


async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the feedback menu choice"""
    await set_player(update.message.chat_id)
    player.leave_feedback(update.message.text)
    args = {'is_text': True,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            'text': script.bot_messages[lang][-11],
            'markup': InlineKeyboardMarkup([[InlineKeyboardButton(script.user_replies[lang][-6], callback_data="_")]])
            }
    last_message[player.get_id()] = await send_anything(args)
    return FEEDBACK_BUTTON


async def feedback_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles info menu choice"""
    query = update.callback_query
    await query.answer()
    await set_player(query.message.chat_id)
    return await novel(update, context)
