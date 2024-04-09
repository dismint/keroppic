import main
import discord

intents = discord.Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('pop'):
        info = message.content.split()[1:]
        if len(info) == 0:
            await message.channel.send("no commands keroppi sad :c");
            return

        if info[0] == "see":
            if len(info) > 1 and info[1] == "clean":
                main.template(p_verbose=False)
            else:
                main.template()
            await message.channel.send(file=discord.File('template.png'))

        if info[0] == "mod":
            if len(info) < 3:
                await message.channel.send("no commands keroppi sad :c");
                return
            if len(info) < 4:
                info = info[:2] + ["status", info[2]]
            res = main.mod(info[1], {info[2]: info[3]})
            if res:
                await message.channel.send(f"modified {info[2]}:{info[3]}!")
                main.template()
                await message.channel.send(file=discord.File('template.png'))
            else:
                await message.channel.send("file didnt exist TwT")

        if info[0] == "filter":
            if len(info) < 2:
                main.filter("")
                return
            f_text = " ".join(info[1:])
            main.filter(f_text)
            main.template()
            await message.channel.send(file=discord.File('template.png'))

        if info[0] == "status":
            if len(info) < 2:
                main.status("")
                return
            s_text = " ".join(info[1:])
            main.status(s_text)
            main.template()
            await message.channel.send(file=discord.File('template.png'))
token1 = "MTIyNzI4NDQzNzQ0NDU5MTY0Nw."
token2 = "G28OWq.sqNLoabV7PPCL9"
token3 = "EWVrT3rG2GayKD8Jg9IL-fXw"

tk1 = "MTIyNzMzODk1OTc0MzQ4ODA2M"
tk2 = "Q.GPGFAP.4BIXFDUmXmRHj3"
tk3 = "jiFTSsRmnToBtmMGz-epOPxw"

# client.run(token1 + token2 + token3)
client.run(tk1 + tk2 + tk3)
