import sys
import logging
import signal
import subprocess
import html
import json
import traceback

from config import TELEGRAM
from telegram import (
    ParseMode, 
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackContext,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

SHUTDOWN = range(1)

class Telegram_Bot:
    
    def run(self):
        self.is_running = True
        self.updater.start_polling()
        self.updater.idle()
    
    def shutdown_confirmation(self, update, context):
        # update.message.reply_text('Are you sure you want to shut down the telegram bot?')
        options = [
            InlineKeyboardButton(text='Yes', callback_data='Yes'),
            InlineKeyboardButton(text='No', callback_data='No')
        ]

        reply_markup = InlineKeyboardMarkup([options])
        update.message.reply_text(
            text='Are you sure you want to shut down the telegram bot?',
            reply_markup=reply_markup
        )
    
    def button(self, update, context):
        query = update.callback_query
        query.answer()
        if query.data == 'Yes':
            query.edit_message_text(text='== Shutting Down Telegram Bot ==')
            self.updater.stop()
        else:
            query.edit_message_text(text='== The stonks continues ==')

    def start(self, update, context):
        '''Starts chart sniper'''
        update.message.reply_text('== Starting Chart Sniper ==')
        # os.system('python3 live.py')
        self.chart_sniper = subprocess.Popen(['python3','live.py'])

    def stop(self, update, context):
        '''Stops Chart Sniper'''
        update.message.reply_text('== Terminating Chart Sniper ==')
        self.chart_sniper.send_signal(signal.SIGINT)

    def send_message(self, text):
        """Send message to the user"""
        self.updater.bot.sendMessage(chat_id=TELEGRAM.get("chat_id"), text=text)

    def error_handler(self, update: object, context: CallbackContext) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        message = (
            f'An exception was raised while handling an update\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )

        # Finally, send the message
        context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=message, parse_mode=ParseMode.HTML)

    def __init__(self):
        """Start the bot."""
        self.is_running = False
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(token=TELEGRAM.get("bot"), use_context=True)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("stop", self.stop))
        dp.add_handler(CommandHandler("shutdown", self.shutdown_confirmation))
        dp.add_handler(CallbackQueryHandler(self.button))
        dp.add_error_handler(self.error_handler)

        # on noncommand i.e message - echo the message on Telegram
        # dp.add_handler(MessageHandler(Filters.text, echo))

        # Start the Bot
        # self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

        # conv_handler = ConversationHandler(
        #     entry_points=[CommandHandler('shutdown', self.shutdown_confirmation)],
        #     states={
        #         SHUTDOWN: 

        #     }
        # )


# print("bot is running?: ", bot.is_running)
# if __name__ == 'telegram_bot':
#     bot.run()

if __name__ == '__main__':
    try:
        bot = Telegram_Bot()
        bot.run()
        print("bot is running in main?: ", bot.is_running)
    except KeyboardInterrupt:
        sys.exit()

# if not bot.is_running:
#     bot.run()
#     print("bot is running  main?: ", bot.is_running)
