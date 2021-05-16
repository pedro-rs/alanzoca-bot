# TODO : catch "command not found" exceptions
# TODO : faça o teste do "!translate pt ent" (com um "t" msm) o bot para de funfar :( F bot

import os, discord, asyncio
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(".env")  # take environment variables from .env.

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents, help_command=None)

buff = {}
# Loads all cogs
for ext in os.listdir(Path('./cogs')):
    if ext.endswith('.py'):
        bot.load_extension(f'cogs.{ext[:-3]}')
        buff[ext] = os.stat(f'./cogs/{ext}').st_mtime     # Logging the time it was loaded
        print(f"Loaded {ext}")


@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")
    GAME = discord.Game("!help para ver os comandos") 
    await bot.change_presence(activity=GAME)

    while True:
        await asyncio.sleep(2)
        for ext in os.listdir(Path('./cogs')):
            if ext.endswith('.py'):
                if os.stat(f'./cogs/{ext}').st_mtime != buff[ext]:
                    print(f"[Reloadaded {ext}] @ {datetime.now().strftime('%H:%M:%S')}")
                    print("==================================================")
                    buff[ext] = os.stat(f'./cogs/{ext}').st_mtime     # Logging the time it was loaded
                    bot.reload_extension(f'cogs.{ext[:-3]}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass # These are handled by the extensions individually
    elif isinstance(error, commands.CommandNotFound):
        ctx.send("Hmm, não conheço esse comando. Se quiser ver meus comandos, envie `!help`")
    else:
        await ctx.send(f"Oops, algo deu errado.\nErro: {error}", delete_after=10)
        print(f"[Erro: {error}] @ {datetime.now().strftime('%H:%M:%S')}")
        print("==================================================")

        

bot.run(os.getenv("DISC_TOKEN"))