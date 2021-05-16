from discord.ext import commands
import discord, asyncio, random, os, csv, random
from pathlib import Path

INPUT_FILE = Path('./log.txt')

emojis_comp = [':heart_eyes:', ':smiling_face_with_3_hearts:', ':star_struck:', ':sunglasses:', ':zany_face:', ':cold_face:', ':blush:', ':heart_eyes_cat:']
emojis_eng = [':face_with_symbols_over_mouth:', ':nauseated_face:', ':face_vomiting:', ':mask:', ':sleeping:']
ranking = {}

def save_rank():
    # Register log
    with open(INPUT_FILE, "w") as file:
            writer = csv.writer(file)
            writer.writerow(['key', 'value'])
            for key, value in ranking.items():
                writer.writerow([key, value])

def load_rank():
    with open(INPUT_FILE,"r") as file:              # Open log in read mode
        reader = csv.DictReader(file)
        ranking.clear()                             # Reseting the dict
        for row in reader:                          # Re-populating dict
            ranking[row['key']] = row['value']

def reset_rank():
    open(INPUT_FILE, 'w').close()
    ranking.clear()


class Computeiro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)


    @commands.command()
    async def rank_index(self, ctx):
        load_rank()

        if str(ctx.author.id) in ranking:
            await ctx.reply("Você já está no ranking!", delete_after=5)

        else:
            number = random.randint(0, 100)
            comp_emoji = random.choice(emojis_comp)
            eng_emoji = random.choice(emojis_eng)
            enguber = "EngComper" if random.randint(1, 50) != 3 else "~~Motorista da Uber~~ EngComper"
            ranking[ctx.author.id] = number             # Saves the person (through their ID) in the ranking dict
            await ctx.send(f'{ctx.author.name} é {number}% computeiro {comp_emoji}, com aquele {100 - number}% de {enguber} {eng_emoji}')
            if number == 100:
                await ctx.channel.send(f'Alan Turing? És tu? :O {ctx.author.mention}')

            save_rank()

    @commands.command()
    async def rank(self, ctx):
        load_rank()

        if not(ranking):
            await ctx.send("O ranking está vazio :(")
        
        else:
            embed = discord.Embed(title="Ranking de computaria")
            i = 1
            for x in sorted(ranking, key=ranking.get, reverse=True):
                user = self.bot.get_user(int(x))
                embed.add_field(name = f"#{i}: {user.name}", value = f"{ranking[x]}% computeiro", inline=False)
                i += 1
            await ctx.send(embed=embed)
        

    @commands.command()
    @is_admin()
    async def rank_reset(self, ctx):
        reset_rank()
        await ctx.send(f"O rank for resetado por {ctx.author.mention}")

    @rank_reset.error
    async def reset_rank_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("Você não tem permissão para usar esse comando.", delete_after=5)

def setup(bot):
    bot.add_cog(Computeiro(bot))