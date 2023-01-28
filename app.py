from dotenv import load_dotenv

load_dotenv()

import os
import requests
import time
import gpt

import flask
import telebot

app = flask.Flask(__name__)

bot = telebot.TeleBot(os.environ["TELEGRAM_TOKEN"], threaded=False)


WEBHOOK_URL = "https://overheardbot.vercel.app"


@app.route("/")
def hello():
    """ Just a simple check if the app is running """
    return {"status": "ok"}


# Process webhook calls
@app.route("/webhook", methods=["POST"])
def webhook():
    if flask.request.headers.get("content-type") == "application/json":
        json_string = flask.request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        flask.abort(403)

# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        """
        Welcome to the demo bot. 

        Send a message to get an echo reply

        /help Prints this help message
        /gpt <message> - Get a GPT-3 generated reply based on your prompt in gpt.py
        
        """,
    )

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    file_id = file_info.file_id
    # GET from this url https://johnmcdonnell--telegram-transcribe.modal.run  passing in file_id as an argument
    # This will return a JSON response with the transcript
    # We can then send that to the user
    bot.send_message(message.chat.id, 'Attempting to transcribe!')

    response = requests.get(f'https://johnmcdonnell--telegram-transcribe.modal.run?file_id={file_id}')
    if response.status_code == 200 and response.json()['text']:
        bot.reply_to(message, response.json()['text'])
    else:
        bot.reply_to(message, 'Sorry, transcription failed')




@bot.message_handler(commands=["gpt"])
def gpt_response(message):
    """Generate a response to a user-provided message make sure to change the prompt in gpt.py
    and set the OPENAI_TOKEN environment variable"""
    response = gpt.respond(message.text)
    bot.reply_to(message, response)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_message(message):
    """Echo the user message"""
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
