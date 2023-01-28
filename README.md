# Overheard bot
Telegram bot enabling voice journaling.

Forked from @jxnl's repo, jxnl/vercel-telegram-gpt.


## Setting up your Flask App
1. Clone this repository
2. Create a `.env` file and add your Telegram bot token  OpenAI API key
3. Optionally you can also add a OpenAI API key to enable the `/gpt` command
3. Create a virtual environment by running `python3 -m venv env`
4. Activate the virtual environment by running `source env/bin/activate`
5. Install the required packages by running `pip install -r requirements.txt`
6. Visit the [telebot docs](https://pytba.readthedocs.io/en/latest/quick_start.html) to get a rundown on how to make more complex responses.


## Deployment on Vercel
1. Connect your GitHub repository to Vercel or
2. Run `npm i -g vercel` to install vercel
3. Run `vercel auth` to authenticate
4. Run `vercel` the first time to set up the itegrationto deploy the app
5. Run `vercel dev` to test the application locally
6. Run `vercel secrets add [secret-name] [secret-value]` to set your tokens
7. Run `vercel deploy` to deploy the application as a preview

## Setting up Webhooks

1. Run the `app.py` script use the URL of your Vercel-deployed app as the webhook URL

## Implementing GPT-3
1. In the `app.py` file, import the OpenAI package and Telebot package
2. Implement the function for calling the GPT-3 API and generating a response
3. In the Telegram bot handling function, call the GPT-3 function and use the generated response as the bot's reply using telebot


## Conclusion
Congratulations, you have successfully created and deployed a Telegram bot using Flask, Webhooks, and Vercel. You have also added the functionality of GPT-3 to generate responses for your bot using Telebot.

Feel free to reach out if you have any questions or issues. Happy coding!
