from telebot import engine
from telebot.credentials import bot_token
from telegram.ext import (
    Application,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters)


def main() -> None:
    """Starting the bot."""
    # Creating the Application and pass it the bot's token.
    application = Application.builder().token(bot_token).build()

    # Adding conversation handler with the states NAME_ENTERING, GOOD_MORNING and CONSTRUCTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", engine.start)],
        states={
            engine.NAME_ENTERING: [MessageHandler(filters.Regex("^(Українська|Русский)$"), engine.enterName)],
            engine.HANDLING_NAME: [MessageHandler(~filters.COMMAND & filters.TEXT, engine.handleName)],
            engine.GOOD_MORNING: [MessageHandler(~filters.COMMAND & filters.TEXT, engine.greetings)],
            engine.NOVEL: [MessageHandler(filters.Regex("^(Давай!)$"), engine.novel)],
            engine.CONTINUE: [CallbackQueryHandler(engine.game_buttons)],
            engine.INFO: [MessageHandler(filters.Regex("^(Інфо|Инфо)$"), engine.info)],
            engine.INFO_BUTTONS: [CallbackQueryHandler(engine.info_buttons)]
        },
        fallbacks=[MessageHandler(filters.Regex("^(Інфо|Инфо)$"), engine.info),
                   MessageHandler(~filters.Regex("^(Інфо|Инфо)$"), engine.error)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
