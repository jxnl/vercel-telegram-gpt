from dotenv import load_dotenv

load_dotenv()

import os
import requests
import time
import gpt

import flask
import telebot
from telebot.async_telebot import AsyncTeleBot


app = flask.Flask(__name__)

bot = AsyncTeleBot(os.environ["TELEGRAM_TOKEN"])

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

@app.route("/assemblyai_callback_webhook", methods=["POST"])
def assemblyai_callback_webhook():
    """ This is the webhook that Assembly AI calls when a transcript is ready 
    """
    # TODO set up statefulness so we can use this instead of the polling method
    # We need the chat_id to be associated with it.

    # Get the JSON response
    json_response = flask.request.get_json()

    # Get the transcript ID
    if json_response["status"] == "completed":
        transcript_id = json_response["transcript_id"]

    else:
        print("The Assembly AI webhook was called but the status was not completed")
        print(json_response)
        return


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    bot.reply_to(
        message,
        """
        Welcome to the demo bot. 

        Send a message to get an echo reply

        /help Prints this help message
        /gpt <message> - Get a GPT-3 generated reply based on your prompt in gpt.py
        
        """,
    )

async def poll_for_transcript_completion(chat_id, transcript_id):
    """ Polls the Assembly AI API for completion of the transcript """

    # Get the API key from the environment variable
    api_key = os.environ["ASSEMBLY_AI_API_KEY"]

    # Set the headers
    headers = {"authorization": api_key}

    time_elapsed = 0
    while True:
        if time_elapsed > 60 * 5:
            await bot.send_message(chat_id, 'Transcription timed out, sorry')
            return None
        # Get the transcript
        response = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers
        )

        # Get the JSON response
        json_response = response.json()

        # If the transcript is complete
        if json_response["status"] == "completed":
            return json_response
        elif json_response["status"] == "error":
            bot.send_message(chat_id, 'There was an error with the transcription')
        else:
            time.sleep(0.25)
            time_elapsed += 0.25
    return None

@bot.message_handler(content_types=['voice'])
async def voice_processing(message):
    # Download the voice message
    file_info = await bot.get_file(message.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    await bot.send_message(message.chat.id, "Processing your voice message...")
    
    # Upload voice message to Assembly AI
    headers = {'authorization': os.environ["ASSEMBLY_AI_TOKEN"]}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                            headers=headers,
                            data=downloaded_file)
    print(response.json())
    if 'upload_url' in response.json():
        upload_url = response.json()['upload_url']
    else:
        print('Error uploading file to Assembly AI')
        print(response.json())
        await bot.send_message(message.chat.id, "Error uploading file to Assembly AI")
        return None

    # Now request the transcript
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = { "audio_url": upload_url,
            "webhook_url": f"{WEBHOOK_URL}/assemblyai_callback_webhook" }
    headers = {
        "authorization": os.environ["ASSEMBLY_AI_TOKEN"]
    }
    response = requests.post(endpoint, json=json, headers=headers)
    print(response.json())
    
    # Get the transcript ID
    completion = poll_for_transcript_completion(message.chat.id, response.json())
    if completion:
        print(completion)
        transcript_text = completion['text']
        await bot.reply_to(message, transcript_text)



@bot.message_handler(commands=["gpt"])
async def gpt_response(message):
    """Generate a response to a user-provided message make sure to change the prompt in gpt.py
    and set the OPENAI_TOKEN environment variable"""
    response = gpt.respond(message.text)
    bot.reply_to(message, response)


@bot.message_handler(func=lambda message: True, content_types=["text"])
async def echo_message(message):
    """Echo the user message"""
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
