import logging
import signal
import subprocess
import html
import traceback

from config import TELEGRAM
from telegram import (
    ParseMode, 
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    parsemode,
)
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackContext,
    CallbackQueryHandler,
    Filters,
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

(SHUTDOWN_YES, SHUTDOWN_NO, STOP_YES, STOP_NO) = ("SHUTDOWN_YES", "SHUTDOWN_NO", "STOP_YES", "STOP_NO") 

class Telegram_Bot:
    
    def __init__(self):
        """Start the bot."""
        self.is_running = False
        self.updater = Updater(token=TELEGRAM.get("bot"), use_context=True)
        filter = Filters.user(username="@wilfredbtan")
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=filter))
        dp.add_handler(CommandHandler("stop", self.stop_confirmation, filters=filter))
        dp.add_handler(CommandHandler("shutdown", self.shutdown_confirmation, filters=filter))
        dp.add_handler(CallbackQueryHandler(self.callbackHandler))
        dp.add_error_handler(self.error_handler)

    def run(self):
        self.send_message("The most stonks trading bot has been activated")
        self.updater.start_polling()
        self.updater.idle()
    
    def stop_confirmation(self, update, context):
        if not self.is_running:
            update.message.reply_text('== Unable to stop. Chart Sniper is not running==')
            return

        self.chart_sniper.send_signal(signal.SIGUSR1)

        options = [
            InlineKeyboardButton(text='Yes', callback_data=STOP_YES),
            InlineKeyboardButton(text='No', callback_data=STOP_NO)
        ]

        reply_markup = InlineKeyboardMarkup([options])
        update.message.reply_text(
            text='Stop Chart Sniper?',
            reply_markup=reply_markup
        )
    
    def shutdown_confirmation(self, update, context):
        options = [
            InlineKeyboardButton(text='Yes', callback_data=SHUTDOWN_YES),
            InlineKeyboardButton(text='No', callback_data=SHUTDOWN_NO)
        ]

        reply_markup = InlineKeyboardMarkup([options])
        update.message.reply_text(
            text='Are you sure you want to shut down the telegram bot?',
            reply_markup=reply_markup
        )
    
    def callbackHandler(self, update, context):
        query = update.callback_query
        query.answer()
        if query.data == STOP_YES:
            query.edit_message_text(text='== Stopping Chart Sniper ==')
            # self.chart_sniper.send_signal(signal.SIGINT)
            self.stop(update, context)

        if query.data == STOP_NO:
            query.edit_message_text(text='== The stonks continues ==')

        if query.data == SHUTDOWN_YES:
            query.edit_message_text(text='== Shutting Down Telegram Bot ==')
            if self.is_running:
                # self.chart_sniper.send_signal(signal.SIGINT)
                self.stop(update, context)
            self.updater.stop()

        if query.data == SHUTDOWN_NO:
            query.edit_message_text(text='== The stonks continues ==')

    def start(self, update, context):
        '''Starts chart sniper'''
        if self.is_running:
            update.message.reply_text('== Unable to start. Chart Sniper is already Running ==')
            return

        self.is_running = True
        # update.message.reply_text('== Starting Chart Sniper ==')
        txt = '<b>== Starting Chart Sniper ==</b>'
        context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=txt, parse_mode=ParseMode.HTML)
        self.chart_sniper = subprocess.Popen(['python3','src/live.py'])

    def stop(self, update, context):
        '''Stops Chart Sniper'''
        # update.message.reply_text('== Terminating Chart Sniper ==')
        txt = '<b>== Terminating Chart Sniper ==</b>\nRemember to close all positions and cancel all orders.'
        context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=txt, parse_mode=ParseMode.HTML)
        self.chart_sniper.send_signal(signal.SIGINT)
        self.is_running = False

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

        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                # bot.send_message(message.chat.id, message[x:x+4096])
                context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=message[x:x+4096], parse_mode=ParseMode.HTML)
        else:
            # bot.send_message(message.chat.id, message)
            context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=message, parse_mode=ParseMode.HTML)

        # context.bot.send_message(chat_id=TELEGRAM.get("chat_id"), text=message, parse_mode=ParseMode.HTML)

    def send_message(self, text):
        """Send message to the user"""
        self.updater.bot.sendMessage(chat_id=TELEGRAM.get("chat_id"), text=text)

if __name__ == '__main__':
    try:
        bot = Telegram_Bot()
        bot.run()
    except KeyboardInterrupt:
        raise
