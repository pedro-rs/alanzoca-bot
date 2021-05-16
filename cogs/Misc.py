from discord.ext import commands
from googletrans import Translator
import asyncio, discord

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)

    def is_reply():
        async def predicate(ctx):
            return not ctx.message.reference.resolved is None
        return commands.check(predicate)


    @commands.command()
    @is_admin()
    async def clear(self, ctx, quantity: int):
        await ctx.channel.purge(limit=quantity + 1)

        embed = discord.Embed(title="Mensagens apagadas", description= "**{}** mensagens foram apagadas.".format(quantity))
        embed.add_field(name="Ação executada por", value = "{}".format(ctx.author.mention), inline=True)
        await ctx.channel.send(embed=embed, delete_after=5)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.reply('Uso incorreto do comando.\n → `!clear [quantidade]`', delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply("Você não tem permissão para usar esse comando.", delete_after=5)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(colour=0x3388FF)
        embed.add_field(name=":small_blue_diamond: `!ne`", value = "Cria uma nova enquete", inline=False)
        embed.add_field(name=":small_blue_diamond: `!clear {quantidade}`", value = "Apaga `quantidade` de mensagens", inline=False)
        embed.add_field(name=":small_blue_diamond: `!rank_index`", value = "Te coloca no ranking", inline=False)
        embed.add_field(name=":small_blue_diamond: `!rank`", value = "Exibe o ranking", inline=False)
        #embed_comandos.add_field(name=":small_blue_diamond: `!tr {lingua destino} {lingua origem}`", value = "Traduz uma mensagem", inline=False)
        image = self.bot.user.avatar_url_as(format='png', size=128)
        embed.set_author(name="Comandos", icon_url=image)
        await ctx.send(embed=embed)

    """ Googletrans library seems to be really unstable. Will come back to this later.
    @commands.command()
    @is_reply()
    async def tr(self, ctx, source: str, dest: str):
        print("1")
        translator = Translator()
        reference = ctx.message.reference.resolved
        print(reference.content)
        print("2")
        translated_message = translator.translate(reference.content, dest=dest, src=source)
        print("3") # => Code is not reaching this point for some reason (??)
        await reference.reply(f">>> {translated_message.text}")


    @tr.error
    async def tr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.reply('Uso incorreto do comando.\n → `!tr [origem] [destino]`', delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply("Responda uma mensagem com o comando!", delete_after=5)
    """

def setup(bot):
    bot.add_cog(Misc(bot))
