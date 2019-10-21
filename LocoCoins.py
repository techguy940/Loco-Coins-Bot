BotToken = "Enter your Bot Token here!"
#BotToken = "Enter your Bot Token here!"
BotPrefix = "$"

import random
import requests
import asyncio
from discord import Game
from discord.ext.commands import Bot
import discord
from discord.ext import commands
import random
import aiohttp
import json

if BotToken == "Enter your Bot Token here!":
    raise ValueError("Please enter your Bot Token in line 1")

bot = Bot(command_prefix = BotPrefix)

headers = {
    "authorization": "Blep NxiYEwFvgWh6D01whmjp6YFhiEKdn40"
}
auth2 = BotToken
apiUrl = "http://152.89.104.131:10101/"

response = requests.get(
    apiUrl+"GetOnline",
    headers = headers,
    json = {"auth2": auth2}
).json()
print(response)
if response.get("error"):
    raise ConnectionError("Unable to connect to the API.")
else:
    print(response["message"])

with open("UsersData.json", "w+") as f:
    json.dump({}, f)

with open("UsersData.json") as f:
    UsersData = json.load(f)

def SaveUsersData():
    with open("UsersData.json", "w+") as f:
        json.dump(UsersData, f)

@bot.event
async def on_ready():
    print(
        "Logged in"

    )
    await bot.change_presence(activity=discord.Game(name='with Just for fun | {}help'.format(BotPrefix)))

@bot.command(pass_context = True)
async def play(ctx, *, phoneNumber: str = None):
    if phoneNumber is None:
        return await ctx.send(
            "**Correct Use:**\n`{}play <phoneNumber>`".format(
                BotPrefix
            )
        )
    print(phoneNumber)
    if phoneNumber.startswith("+91"):
        phoneNumber = phoneNumber[3:]
    print(phoneNumber)
    if len(phoneNumber) != 10:
        return await ctx.send(
            "**Invalid Phone Number!**"
        )

    response = requests.post(
        apiUrl+"Loco/SendOTP",
        headers = headers,
        json = {
            "phoneNumber": phoneNumber
        }
    ).json()

    if response.get("error"):
        return await ctx.send(
            "**An error occurred.**"
        )

    elif not response.get("status"):
        return await ctx.send(
            "**An error occurred.**"
        )

    await ctx.send(
        "**OTP has been successfully sent to your phone number:**\n`+91{}*****`\nPlease enter your otp using `{}code <otp>`".format(
            phoneNumber[:5],
            BotPrefix
        )
    )

    def CodeCheck(Message):
        return Message.author == ctx.message.author and Message.content.lower().startswith("{}code".format(BotPrefix))


    codeMessage = await bot.wait_for('message',
        timeout = 60,
        check = CodeCheck
    )
    code = codeMessage.content.lower()[(len(BotPrefix)+4):]
    code = str(code.replace(" ", ""))

    if len(code) != 4:
        return await ctx.send(
            "**Invalid OTP Entered!**"
        )

    response = requests.post(
        apiUrl+"Loco/VerifyOTP",
        headers = headers,
        json = {
            "phoneNumber": phoneNumber,
            "code": code
        }
    ).json()
    print(response)
    if response.get("error"):
        if response["errorCode"] == 7:
            return await ctx.send(
                "**Session expired!\nPlease use `{}play` command again.**".format(
                    BotPrefix
                )
            )
        else:
            return await ctx.send(
                "**Incorrect OTP entered!**"
            )


    authToken = response["authToken"]

    UsersData[ctx.message.author.id] = authToken
    SaveUsersData()
    print("otp verified")
    response = requests.post(
        apiUrl+"Loco/PlayPractice",
        headers = headers,
        json = {
            "authToken": authToken
        }
    ).json()
    print(response)
    if response.get("error"):
        if response["errorCode"] == 10:
            return await ctx.send(
                "**{}**".format(
                    response["error"]
                )
            )

        else:
            return await ctx.send(
                "**An unknown error occurred!**"
            )

    practiceMessage = await ctx.send(
        "**Started Loco Practice!**"
    )

    TotalEarned = 0
    TotalBalance = "Unknown"

    while True:
        await asyncio.sleep(5)

        response = requests.get(
            apiUrl+"Loco/GetPracticeStatus",
            headers = headers,
            json = {
                "authToken": authToken
            }
        ).json()

        if response.get("error"):
            del UsersData[ctx.message.author.id]
            SaveUsersData()

            if response["errorCode"] == 11:
                if TotalEarned == 0:
                    return await practiceMessage.edit(
                        content="**You played all the Practice Games!\nPlease try again later.**"
                    )

                return await practiceMessage.edit(
                    content="**Loco Practice Over!**\n\n**• Total Coins Earned: {}\n• Total Coin Balance: {}**\n\nMade by **Just for fun#4278**".format(
                        TotalEarned,
                        TotalBalance
                    )
                )

            return await practiceMessage.edit(
                content="**An unknown error occurred!**"
            )

        TotalEarned = response["TotalEarned"]
        TotalBalance = response["TotalBalance"]

        await practiceMessage.edit(
            content="**Playing Loco Practice...**\n\n**• Total Coins Earned: {}\n• Total Coin Balance: {}**".format(
                TotalEarned,
                TotalBalance
            )
        )

@bot.command(pass_context = True,no_pm=True)
async def stop(ctx):
    if ctx.message.author.id not in UsersData:
        return await ctx.send(
            "**No game running on your account!**"
        )

    authToken = UsersData[ctx.message.author.id]
    del UsersData[ctx.message.author.id]
    SaveUsersData()

    response = requests.post(
        apiUrl+"Loco/StopPractice",
        headers = headers,
        json = {
            "authToken": authToken
        }
    ).json()

    if response.get("status"):
        return await ctx.send(
            "**"+response["message"]+"**"
        )

    elif response.get("error"):
        if response["errorCode"] == 11:
            return await ctx.send(
                "**No game running on your account!**"
            )

        return await ctx.send(
            "**An unknown error occurred!**"
        )

    else:
        return await ctx.send(
            "**An unknown error occurred!**"
        )

loop = asyncio.get_event_loop()
while True:
    try:
        loop.run_until_complete(bot.start(BotToken, reconnect=True))
    except Exception as e:
        time.sleep(1)
        print("Event loop error:", e)
