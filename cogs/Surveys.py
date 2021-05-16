from discord.ext import commands
import discord # Needed for embeds

creating_surveys = {}
active_surveys = {}

# Generates all possible reactions to a survey
possible_reactions = []
for i in range(9):
    possible_reactions.append(f"{i + 1}\N{variation selector-16}\N{combining enclosing keycap}")

# This class hosts surveys that are already created (Active)
class Survey:
    def __init__(self, author):
        self.title = None
        self.quantity = None
        self.author = author
        self.options = []
        self.votes = {}
        self.voters = {}
        self.embed = None

    # Generates the embed (ie. the survey itself)
    def generate_embed(self):
        embed = discord.Embed(title=f"{self.title}", colour=0x3388FF)
        profile_img = self.author.avatar_url_as(format='png', size=128)
        embed.set_author(name=self.author.name, icon_url=profile_img)

        for j in range(self.quantity):
            embed.add_field(name=f"{j + 1}\N{variation selector-16}\N{combining enclosing keycap} : {self.options[j]}", value = f"00 | **0%**", inline=False)

        embed.set_footer(text="Para votar, clique em uma reação (abaixo) correspondendo à sua opção de voto.")

        return embed
    

# This class hosts surveys thata are mid-creation
class CreatingSurvey(Survey):
    def __init__(self, author, channel, server):
        super().__init__(author)
        self.channel = channel
        self.server = server
        self.inputing_options = False       # True when user is in the process of inputing options
    

def generate_percentage(num):
    display = ""
    part = int(num//5)
    for i in range(part):
        display += "█"

    return display    


def update_embed(survey_id):
    survey = active_surveys[survey_id]
    votes = survey.votes
    title = survey.title
    author = survey.author.name
    profile_img = survey.author.avatar_url_as(format='png', size=128)
    quantity = survey.quantity
    options = survey.options

    total_votes = 0
    for i in votes:
        total_votes += votes[i] 
    
    new_embed = discord.Embed(title=f"{title}", colour=0x3388FF)
    new_embed.set_author(name=author, icon_url=profile_img)

    if total_votes == 0:
        for j in range(quantity):
            new_embed.add_field(name=f"{j + 1}\N{variation selector-16}\N{combining enclosing keycap} : {options[j]}", value = f"{votes[str(j + 1)]:02d} | **0%**", inline=False)

    else:
        for j in range(quantity):
            partial_percentage = (votes[str(j + 1)] / total_votes) * 100
            new_embed.add_field(name=f"{j + 1}\N{variation selector-16}\N{combining enclosing keycap} : {options[j]}", value = f"{votes[str(j + 1)]:02d} | {generate_percentage(partial_percentage)} **{int(partial_percentage)}%**", inline=False)

    new_embed.set_footer(text="Para votar, clique em uma reação (abaixo) correspondendo à sua opção de voto.")

    return new_embed


# Transforms user's reaction to a survey into an integer in order to compute the vote
def int_reaction(reaction):
    reaction = str(reaction)
    if reaction in possible_reactions:
        vote = int(reaction[:1])

    return vote  

# Main class for the cog
class Surveys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def ne(self, ctx):
        if ctx.author not in creating_surveys and not isinstance(ctx.channel, discord.channel.DMChannel):
            creating_surveys[ctx.author] = CreatingSurvey(channel=ctx.channel, server=ctx.guild, author=ctx.author)
            await ctx.author.send("**Vamos criar uma nova enquete!** Basta responder minhas perguntas aqui nesse chat!")
            await ctx.author.send("Qual o **título** da sua enquete?")

    @commands.command()
    async def cancel(self, ctx):
        if ctx.author in creating_surveys:
            del creating_surveys[ctx.author]
            await ctx.reply("**Sua enquete atual foi cancelada.** Se desejar, agora você pode começar outra.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return


        if isinstance(message.channel, discord.channel.DMChannel) and message.author in creating_surveys:
            author = message.author
            survey = creating_surveys[author]

            # Choosing the survey's title
            if survey.title == None:
                survey.title = str(message.content.strip())

                await message.channel.send(f">>> **Título da enquete:** {survey.title}")
                await message.channel.send("**Quantas opções** sua enquete terá?")

                return


            # Choosing how many options the surveys has and the options' values
            if survey.title != None and survey.quantity == None:
                survey.quantity = int(message.content.strip())
                
                await message.channel.send(f">>> **Quantidade de opções da enquete:** {survey.quantity}")

                def check(msg):
                    if msg.author in creating_surveys:
                        return creating_surveys[msg.author].inputing_options

                for i in range (1, survey.quantity + 1):
                    await message.channel.send(f"Qual a **{i}° opção** da sua enquete?")
                    survey.inputing_options = True
                    option = await self.bot.wait_for('message', check=check)
                    survey.options.append(option.content)

                await message.channel.send("**PREVIEW DA ENQUETE:**")
                embed = survey.generate_embed()
                await message.channel.send(embed=embed)
                await message.channel.send(f"A enquete será enviada em: \n**Servidor** → {survey.server} \n**Canal** → {survey.channel} \n**Para confirmar, envie `ok`.**")


            # Confirming the survey and sending it to the server -> channel
            if survey.quantity == len(survey.options) and message.content == "ok":
                embed = survey.generate_embed()
                await survey.channel.send(">>> **ENQUETE**")
                sent_embed = await survey.channel.send(embed=embed)
                survey_id = str(sent_embed.id)

                for i in range(survey.quantity):
                    await sent_embed.add_reaction(f"{i + 1}\N{variation selector-16}\N{combining enclosing keycap}")
                
                # Passing the survey from "creating" to "active"
                active_surveys[survey_id] = Survey(author)
                active_surveys[survey_id].embed = sent_embed
                active_surveys[survey_id].quantity = survey.quantity
                active_surveys[survey_id].options = survey.options

                for i in range(1, survey.quantity + 1):
                    active_surveys[survey_id].votes[str(i)] = 0

                del survey


    # Registering added votes
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):         
        if user == self.bot.user:
            return

        message = reaction.message

        if str(message.id) in active_surveys:
            vote = int_reaction(reaction)
            survey = active_surveys[str(message.id)]


            if (vote in range(1, survey.quantity + 1)) and (user not in survey.voters):
                survey.votes[str(vote)] += 1
                survey.voters[user] = vote

                embed = survey.embed
                new_embed = update_embed(str(message.id))

                await embed.edit(embed=new_embed)

            else:
                return


    # Registering removed votes
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user == self.bot.user:
            return

        message = reaction.message

        if str(message.id) in active_surveys:
            vote = int_reaction(reaction)
            survey = active_surveys[str(message.id)]
            
        if vote in range(1, survey.quantity + 1) and (user in survey.voters) and (survey.voters[user] == vote):
            survey.votes[str(vote)] -= 1
            survey.voters.pop(user)

            embed = survey.embed
            new_embed = update_embed(str(message.id))

            await embed.edit(embed=new_embed)

        else:
            return
            

def setup(bot):
    bot.add_cog(Surveys(bot))