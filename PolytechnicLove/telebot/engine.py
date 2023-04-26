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

NAME_ENTERING, HANDLING_NAME, CONSTRUCTION, GOOD_MORNING, CONTINUE, NOVEL, INFO_BUTTONS, GLOSSARY_BUTTONS, SAVE_FEEDBACK, FEEDBACK_BUTTON = range(10)

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
        return await novel(update, context, "continue")
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
    reply_keyboard = [[f"{player.get_name()}", script.user_replies[player.get_language()][0]]]
    await update.message.reply_text(script.bot_messages[player.get_language()][0],
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return HANDLING_NAME


async def handleName(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the name choosing"""
    await set_player(update.message.chat_id)
    if update.message.text == script.user_replies[lang][0]:
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


async def novel(update: Update, context: ContextTypes.DEFAULT_TYPE, choice="1") -> int:
    """The wheel of the main story"""
    continu3 = [[InlineKeyboardButton(script.user_replies[lang][1], callback_data="1")]]
    yesno = [
        [
            InlineKeyboardButton(script.user_replies[lang][2], callback_data="2"),
            InlineKeyboardButton(script.user_replies[lang][3], callback_data="3")
        ]
    ]
    menu = [[script.user_replies[lang][i] for i in range(4, 7)]]
    progress = player.get_progress() + 1
    global last_message
    if progress > 3 and (update.message is None or update.message.text != '/start'):
        try:
            await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
        except(BadRequest):
            None
    else:
        await set_player(update.message.chat_id)
        hoax_message = await bot.send_message(chat_id=player.get_id(), text='🕓',
                                              reply_markup=ReplyKeyboardMarkup(menu,
                                                                               resize_keyboard=True))
    args = {'is_text': True,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            'markup': InlineKeyboardMarkup(continu3)
            }

    if progress in [3, 30, 45]:
        args['is_text'] = False
        args['is_photo'] = True
        if progress == 3:
            args['link'] = links.link_begin + links.dream
        elif progress == 30:
            args['link'] = links.link_begin + links.room
        elif progress == 45:
            args['link'] = links.link_begin + links.city
    elif progress in [29]:
        args['is_text'] = False
        args['is_voice'] = True
        if progress == 29:
            args['link'] = links.link_begin + links.alarmclock
    elif progress in [53]:
        args['is_text'] = False
        args['is_sticker'] = True
        if progress == 53:
            args['link'] = links.link_begin + links.vika
    elif progress == 19:
        args['markup'] = InlineKeyboardMarkup(yesno)
    elif choice == "3" or (choice == "1" and progress == 23):
        progress += 3
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
    if query.data == "1" or query.data == "2":
        return await novel(update, context)
    elif query.data == "3":
        return await novel(update, context, "3")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await set_player(update.message.chat_id)
    await last_message[player.get_id()].edit_reply_markup(reply_markup=None)
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
    choose_character = [[InlineKeyboardButton(script.user_replies[lang][7], callback_data="7")]]
    from_char_info_table = [
        [InlineKeyboardButton(script.user_replies[lang][8], callback_data="8")],
        [InlineKeyboardButton(script.user_replies[lang][7], callback_data="7")]
    ]
    args = {'is_text': False,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            }
    if choice == "_":
        args['is_text'] = True
        args['text'] = script.bot_messages[lang][-1]
        if player.get_progress() > 56:
            choose_character.insert(0, [InlineKeyboardButton(script.characters[lang][0], callback_data="Vika")])
        args['markup'] = InlineKeyboardMarkup(choose_character)
    elif choice == "Vika":
        if player.get_progress() < 100:
            args['is_sticker'] = True
            args['text'] = script.bot_messages[lang][-2].format(*script.characters_info[lang]["Vika"]["56-?"])
            args['link'] = links.link_begin + links.vika
            args['markup'] = InlineKeyboardMarkup(from_char_info_table)
    last_message[player.get_id()] = await send_anything(args)
    return INFO_BUTTONS


async def info_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles info menu choice"""
    query = update.callback_query
    await query.answer()
    await set_player(query.message.chat_id)
    if query.data == "7":
        try:
            await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id - 1)
        except(BadRequest):
            None
        await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id)
        return await novel(update, context)
    elif query.data == "Vika":
        await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id)
        return await info(update, context, "Vika")
    elif query.data == "8":
        await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id - 1)
        await bot.deleteMessage(chat_id=player.get_id(), message_id=last_message[player.get_id()].message_id)
        return await info(update, context, "_")


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles about menu choice"""
    await set_player(update.message.chat_id)
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
    return GLOSSARY_BUTTONS


async def glossary_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await novel(update, context)


async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the feedback menu choice"""
    await set_player(update.message.chat_id)
    player.leave_feedback(update.message.text)
    print("898")
    args = {'is_text': True,
            'is_photo': False,
            'is_voice': False,
            'is_sticker': False,
            'text': script.bot_messages[lang][-11],
            'markup': InlineKeyboardMarkup([[InlineKeyboardButton(script.user_replies[lang][7], callback_data="_")]])
            }
    last_message[player.get_id()] = await send_anything(args)
    return FEEDBACK_BUTTON


async def feedback_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles info menu choice"""
    query = update.callback_query
    await query.answer()
    await set_player(query.message.chat_id)
    return await novel(update, context)

