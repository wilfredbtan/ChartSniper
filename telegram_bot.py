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

class Telegram_Bot:
    
    def __init__(self):
        """Start the bot."""
        self.is_running = False
        self.updater = Updater(token=TELEGRAM.get("bot"), use_context=True)
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("stop", self.stop))
        dp.add_handler(CommandHandler("shutdown", self.shutdown_confirmation))
        dp.add_handler(CallbackQueryHandler(self.button))
        dp.add_error_handler(self.error_handler)

    def run(self):
        self.is_running = True
        self.updater.start_polling()
        self.updater.idle()
        self.send_message("The most stonks trading bot has been activated")
    
    def shutdown_confirmation(self, update, context):
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
        self.chart_sniper = subprocess.Popen(['python3','live.py'])

    def stop(self, update, context):
        '''Stops Chart Sniper'''
        update.message.reply_text('== Terminating Chart Sniper ==')
        self.chart_sniper.send_signal(signal.SIGINT)

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

        context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=message, parse_mode=ParseMode.HTML)

    def send_message(self, text):
        """Send message to the user"""
        self.updater.bot.sendMessage(chat_id=TELEGRAM.get("chat_id"), text=text)

if __name__ == '__main__':
    try:
        bot = Telegram_Bot()
        bot.run()
    except KeyboardInterrupt:
        raise
