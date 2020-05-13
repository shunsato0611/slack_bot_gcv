from slackbot.bot import respond_to

print("Hello")
@respond_to('Hello')
def reply_hello(message):
    message.reply('Hello')