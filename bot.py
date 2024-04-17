# | 🙑  dismint
# | YW5uaWUgPDM=

import main
import discord
import shlex

intents = discord.Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    main.load_prereqs()
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or message.channel.name != "keroppi":
        return

    if message.attachments:
        for i, attachment in enumerate(message.attachments):
            num = main.get_next_available()
            await attachment.save(f"img/process/{num}.png")
            await message.channel.send(f"image saved as `{num}`!")
        main.process_images()
        return

    info = message.content.split()

    if info[0] == "see":
        card_count = 0
        if len(info) > 1 and info[1] == "clean":
            card_count = main.template(p_verbose=False)
        else:
            card_count = main.template()
        await message.channel.send(file=discord.File('template.png'))
        await message.channel.send(f"keroppi sees {card_count} images! :3") 

    elif info[0] == "mod":
        if len(info) < 4:
            await message.channel.send("keroppi doesnt know what that means :c maybe try `help`?");
            return
        parsed = shlex.split(message.content)[1:]

        change = {parsed[0]: parsed[1]}
        res = main.mod(parsed[2:], change)
        if res:
            for msg in res:
                await message.channel.send(msg)
        else:
            await message.channel.send(f"modified everything correctly! :3")
        card_count = main.template()
        await message.channel.send(file=discord.File('template.png'))
        await message.channel.send(f"keroppi sees {card_count} images! :3")

    elif info[0] == "look":
        if len(info) != 2:
            await message.channel.send("keroppi doesnt know what that means :c maybe try `help`?");
            return
        res = main.look(info[1])
        await message.channel.send(res)

    elif info[0] == "del":
        if len(info) != 2:
            await message.channel.send("keroppi doesnt know what that means :c maybe try `help`?");
            return
        res = main.del_img(info[1])
        await message.channel.send(res)

    elif info[0] == "filter":
        info = shlex.split(message.content)
        if not len(info) % 2:
            await message.channel.send("keroppi doesnt know what that means :c maybe try `help`?");
            return
        if len(info) == 1:
            main.filter({})
            await message.channel.send("reset all filters");
            return
        flts = {}
        for i in range(1, len(info), 2):
            flts[info[i]] = info[i + 1]
        main.filter(flts)
        card_count = main.template()
        await message.channel.send(file=discord.File('template.png'))
        await message.channel.send(f"keroppi sees {card_count} images! :3")

    elif "help" in info:
        await message.channel.send("keroppi can do these things: \n```"
                                   "see [clean]\n-----------\nsee the current template, 'clean' will remove numbering\n\n"
                                   "mod key text imgs*\n------------------\nedit key for all imgs\n\n"
                                   "filter [key filt]*\n------------------\nfilter by some keys, no argument will reset\n\n"
                                   "look img\n--------\nlook at the info of an img\n\n"
                                   "del img\n-------\ndelete an img\n\n"
                                   "help\n----\nshow this message"
                                   "```keroppi is a good frog :3")

    else:
        await message.channel.send("keroppi doesnt know what that means :c maybe try `help`?")

j_toks = [
    "MTIyNzI4NDQzNzQ0NDU5MTY0Nw.",
    "G28OWq.sqNLoabV7PPCL9",
    "EWVrT3rG2GayKD8Jg9IL-fXw",
]

a_toks = [
    "MTIyNzMzODk1OTc0MzQ4ODA2M",
    "Q.GPGFAP.4BIXFDUmXmRHj3",
    "jiFTSsRmnToBtmMGz-epOPxw",
]

# client.run("".join(j_toks))
client.run("".join(a_toks))
