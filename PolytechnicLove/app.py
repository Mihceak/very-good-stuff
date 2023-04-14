import logging
from telebot.credentials import bot_token, bot_user_name
from info.playerinfo import Player
from files import links

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ConversationHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


NAME_ENTERING, CONSTRUCTION, GOOD_MORNING = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their name."""
    global player
    player = Player(update.message.chat_id, update.message.from_user.first_name)
    reply_keyboard = [[f"{player.get_name()}", "Ввести ім'я"]]

    await update.message.reply_text("Привіт, кунчику. Як до тебе звертатися: ",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return NAME_ENTERING


async def enterName(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the name choosing"""
    if update.message.text == "Ввести ім'я":
        await update.message.reply_text("Введи своє ім'я:")
        return GOOD_MORNING
    else:
        return await greetings(update, context)


async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """greet the player"""
    player.set_name(update.message.text)
    reply_keyboard = [["Охайо!"]]
    await update.message.reply_text(f"Охайо, {player.get_name()}", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CONSTRUCTION


async def construction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bot = Bot(bot_token)
    await bot.send_photo(update.message.chat_id, photo=links.catstruction, caption="The further content is under construction..", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    """Starting the bot."""
    # Creating the Application and pass it the bot's token.
    application = Application.builder().token(bot_token).build()

    # Adding conversation handler with the states NAME and ENTERING
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME_ENTERING: [MessageHandler(~filters.COMMAND & filters.TEXT, enterName)],
            GOOD_MORNING: [MessageHandler(filters.TEXT & ~filters.COMMAND, greetings)],
            CONSTRUCTION: [MessageHandler(filters.Regex("^(Охайо!)$"), construction)],
        },
        fallbacks=[MessageHandler(filters.TEXT, construction)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C`
    application.run_polling()


if __name__ == "__main__":
    main()
