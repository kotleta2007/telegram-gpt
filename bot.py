import logging
from telegram import Update
import telegram
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
from groq import Groq
import re
from chatgpt_md_converter import telegram_format

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
        # self.conv = False
        self.conv = True
        self.client = Groq(api_key=GROQ_API_KEY)

        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.talk))
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('switch', self.switch))
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
            # text = "We are in a conversation."
            text = self.generate(update.message.text)
        else:
            text = "We are not in a conversation."


        # text = re.sub(r'\.', r'\\.', text)
        # text = re.sub(r'\!', r'\\!', text)
        # text = re.sub(r'\-', r'\\-', text)

        print(text)

        # text = re.sub(r"\*\*", r"\*", text)
        # text = re.sub(r"\*\*", r"*", text)
        print(text)
        to_be_escaped = ['_',
                         '*',
                         '[',
                         ']',
                         '(',
                         ')',
                         '~',
                         '`',
                         '>',
                         '#',
                         '+',
                         '-',
                         '=',
                         '|',
                         '{',
                         '}',
                         '.',
                         '!']
        for ch in to_be_escaped:
            # text = re.sub(f"{ch}", f"\\{ch}", text)
            pass
            # text = re.sub(f"\\{ch}", f"\\\\{ch}", text)
            # text = re.sub(ch, f"\\\\{ch}", text)
        print(text)
        # text = re.sub(r"\\\*\\\*", r"*", text)
        print(text)
        print("****")
        print(telegram_format(text))

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=telegram_format(text),
            parse_mode=telegram.constants.ParseMode.HTML,
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
