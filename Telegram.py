import logging
from config import TELEGRAM
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Telegram_Bot:
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
    def start(update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')


    def help(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def send_message(self, text):
        """Send message to the user"""
        self.updater.bot.sendMessage(chat_id=TELEGRAM.get("chat_id"), text=text)


    def __init__(self):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(TELEGRAM.get("bot"), use_context=True)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        # dp.add_handler(CommandHandler("start", start))
        # dp.add_handler(CommandHandler("help", help))
        # dp.add_handle(CommandHandler())

        # on noncommand i.e message - echo the message on Telegram
        # dp.add_handler(MessageHandler(Filters.text, echo))

        # Start the Bot
        # self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()


if __name__ == '__main__':
    bot = Telegram_Bot()