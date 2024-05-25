import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
assert TELEGRAM_TOKEN is not None
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
assert GROQ_API_KEY is not None

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Bot:
    def __init__(self) -> None:
        self.app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        self.conv = False
        self.client = Groq(api_key=GROQ_API_KEY)

        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.talk)
        start_handler = CommandHandler('start', self.start)
        switch_handler = CommandHandler('switch', self.switch)

        self.app.add_handler(start_handler)
        self.app.add_handler(echo_handler)
        self.app.add_handler(switch_handler)
        self.app.run_polling()


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        assert update.effective_chat is not None
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm a bot, please talk to me!"
        )

    async def switch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        assert update.effective_chat is not None
        self.conv = not self.conv

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'CONV is now {self.conv}.'
        )

    async def talk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        assert update.effective_chat is not None
        assert update.message is not None and update.message.text is not None

        if self.conv:
            text = "We are in a conversation."
        else:
            text = "We are not in a conversation."

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        assert update.effective_chat is not None
        assert update.message is not None and update.message.text is not None

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=update.message.text
        )

    def generate(self, text, temperature=0.0,max_tokens=1024):
        res = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-70b-8192",
            temperature=temperature,
            max_tokens=max_tokens,
            # response_format= {"type": "json_object"}
        )
        return res.choices[0].message.content

if __name__ == '__main__':
    bot = Bot()
