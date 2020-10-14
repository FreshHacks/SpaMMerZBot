import config
import discord
import asyncio
import requests
import io
import sqlite3
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands

Bot = commands.Bot(command_prefix = config.prefix)
bad_words = ['мамаша', 'хуйло', 'пидор', 'здохни']

connection = sqlite3.connect('server.db') # Переменная подключения базой данных
cursor = connection.cursor() # Переменная для отправления комманд в базу данных

@Bot.event
async def on_ready():
	print(f"Logged in as {Bot.user}!")

	while True:
		await asyncio.sleep(8)
		await Bot.change_presence( status = discord.Status.idle, activity = discord.Game(name = "by N3Kostya_") )
		await asyncio.sleep(8)
		await Bot.change_presence( status = discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = f"за порядком в чате") )
		await Bot.change_presence( status = discord.Status.idle, activity = discord.Game(name = "спам серверов чмырей") )


@Bot.event
async def on_message(message):
	msg = message.content.lower()
	channel = message.channel
	if msg in bad_words:
		await message.delete()
		await channel.send(f"{message.author.mention} слыш дядя, а ты не охуел такие слова писать?\n\n```{message.content}```")

	await Bot.process_commands( message )


# ============ JOIN SYSTEM ============


@Bot.event
async def on_member_join(member):
	joinchannel = Bot.get_channel(765927147092181022)
	await joinchannel.send(f'{member.name} присоеденился к серверу.')


# ============ LOGS SYSTEM ============

@Bot.event
async def on_message_edit(before, after):
	logchannel = Bot.get_channel(765876096758579240)
	await logchannel.send(f"До: {before.content}\nПосле: {after.content}\nОт: {after.author.mention}\nКанал: {after.channel.mention}")
	await Bot.process_commands(after)



@Bot.command(aliases = [ 'я' ])
async def card(ctx, member: discord.Member = None):

	if member is None:
		img = Image.new('RGBA', (400, 130), '#232529')
		url = str(ctx.author.avatar_url) [:-10]

		response = requests.get(url, stream = True)
		response = Image.open(io.BytesIO(response.content))
		response = response.convert('RGBA')
		response = response.resize((100, 100), Image.ANTIALIAS)

		img.paste(response, (15, 15, 115, 115))
		idraw = ImageDraw.Draw(img)
		name = ctx.author.name
		tag = ctx.author.discriminator

		headline = ImageFont.truetype('arial.ttf', size = 20)
		undertext = ImageFont.truetype('arial.ttf', size = 12)
		idraw.text((145, 15), f"{name}#{tag}", font = headline)
		idraw.text((145, 50), f"ID: {ctx.author.id}", font = undertext)
		memberlvl = cursor.execute(f"SELECT lvl FROM users WHERE id = {ctx.author.id}").fetchone()
		membermessages = cursor.execute(f"SELECT messages FROM users WHERE id = {ctx.author.id}").fetchone()
		membermessages = str(membermessages)
		memberlvl = str(memberlvl)
		if memberlvl == 10:
			memberlvl = "Максимальный"
		idraw.text((145, 85), f"Сообщений: {membermessages}", font=undertext)

		img.save("usercard.png")
		await ctx.send(f"{membermessages}", file=discord.File(fp='usercard.png'))

	else:
		img = Image.new('RGBA', (400, 130), '#232529')
		url = str(member.avatar_url)[:-10]

		response = requests.get(url, stream=True)
		response = Image.open(io.BytesIO(response.content))
		response = response.convert('RGBA')
		response = response.resize((100, 100), Image.ANTIALIAS)

		img.paste(response, (15, 15, 115, 115))
		idraw = ImageDraw.Draw(img)
		name = member.name
		tag = member.discriminator

		headline = ImageFont.truetype('arial.ttf', size=20)
		undertext = ImageFont.truetype('arial.ttf', size=12)
		idraw.text((145, 15), f"{name}#{tag}", font=headline)
		idraw.text((145, 50), f"ID: {member.id}", font=undertext)
		memberlvl = cursor.execute(f"SELECT lvl FROM users WHERE id = {member.id}").fetchone()
		membermessages = cursor.execute(f"SELECT messages FROM users WHERE id = {member.id}").fetchone()
		membermessages = str(membermessages)
		memberlvl = str(memberlvl)
		if memberlvl == 10:
			memberlvl = "Максимальный"
		idraw.text((145, 85), f"Сообщений: {membermessages}", font=undertext)

		img.save("usercard.png")
		await ctx.send(f"{membermessages}", file=discord.File(fp='usercard.png'))


@Bot.command()
async def vote(ctx, time : int, *, content):
	time = int(time)
	time = time * 60

	voteemb = discord.Embed(
		title = "**Опрос**",
		description = f"{content}",
		colour = config.color
	)

	voteemb.set_footer(text=f"Время опроса: {time / 60} минут.")

	message = await ctx.send(embed = voteemb)

	await message.add_reaction('✅')
	await message.add_reaction('❌')

	await asyncio.sleep(time)
	await ctx.send(f"Время опроса закончено")





@Bot.command()
@commands.has_permissions(administrator = True)
async def spam( ctx, link, *, text ):
	await ctx.message.delete()
	embed = discord.Embed( title = "Новый спам!", colour = config.color )

	embed.add_field( name = "**Ссылка:**", value = f"`{link}`", inline = False )
	embed.add_field( name = "**Текст для спама:**", value = f"`{text}`", inline = False )
	embed.set_author( name=ctx.author.name, icon_url=ctx.author.avatar_url )
	await ctx.send("@everyone ", embed = embed)


@Bot.command()
@commands.has_permissions(administrator=True)
async def rules(ctx):
	await ctx.message.delete()
	embed = discord.Embed(title = "Правила", colour = config.color)
	embed.add_field( name = "**1.1**", value = f"Не оскорблять родителей" )
	embed.add_field( name = "**1.2**", value = f"Не пиарится" )
	embed.add_field( name = "**1.3**", value = f"Не юзать селф-ботов" )
	embed.add_field( name = "**1.4**", value = f"Не задавать тупых вопросов" )
	embed.add_field( name = "**1.5**", value = f"Администрация может изменять правила без уведомления пользователей" )
	embed.add_field( name = "**1.6**", value = f"Администратор/модератор может выдавать наказания вне зависимости от нарушения конкретных правил (не пытайтесь обходить правила)." )
	await ctx.send(embed = embed)


@Bot.command( aliases = ["about"] )
async def info(ctx):
	await ctx.message.delete()
	channelrules = Bot.get_channel(762776169387917344)
	channeltokens = Bot.get_channel(762770164222525480)
	channelnewspam = Bot.get_channel(762769708545081345)
	embed = discord.Embed(
		title = "О нас",
		colour = config.color,
		description = f"""
		**Мы хакцеры-спаммеры-программисты))**\n
		**Администрация**: N3Kostya_, Воронсай\n
		**По вопросам писать**: N3Kostya_\n
		**Правила тут**: {channelrules.mention}\n
		**Получить токены**: {channeltokens.mention}\n
		**Тут уведомления о спаме:** {channelnewspam.mention}\n
		**Надеюсь тебе понравится!**
		"""
	)

	await ctx.send(embed = embed)



Bot.run(config.token)