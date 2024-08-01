import nextcord
from nextcord.ext import commands, tasks
import requests
import os

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

WEATHER_API_KEY = ''
XMR_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd'


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.slash_command(description="Get weather information for a location")
async def weather(ctx: nextcord.Interaction, location: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") == "404":
        await ctx.send("Location not found. Please provide a valid location.")
        return

    try:
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        embed = nextcord.Embed(title=f"Weather in {location.capitalize()}", color=nextcord.Color.blue())
        embed.add_field(name="Description", value=weather_description.capitalize(), inline=False)
        embed.add_field(name="Temperature", value=f"{temperature}°C", inline=True)
        embed.add_field(name="Feels Like", value=f"{feels_like}°C", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind Speed", value=f"{wind_speed} m/s", inline=True)

        await ctx.send(embed=embed)

    except KeyError:
        await ctx.send("Failed to retrieve weather information. Please try again later.")

@bot.slash_command(description="Get current price of XMR (Monero)")
async def price(interaction: nextcord.Interaction):
    response = requests.get(XMR_API_URL)
    data = response.json()
    xmr_price = data['monero']['usd']
    await interaction.response.send_message(f"Current XMR Price: ${xmr_price}")

@bot.slash_command(description="Translate text")
async def translate(interaction: nextcord.Interaction, text: str, target_language: str):
    translate_api_url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_language}"
    response = requests.get(translate_api_url)
    translation = response.json()['responseData']['translatedText']
    await interaction.response.send_message(f"Translation: {translation}")

@bot.slash_command(description="Get information about a user")
async def userinfo(interaction: nextcord.Interaction, user: nextcord.Member = None):
    user = user or interaction.user
    embed = nextcord.Embed(title=f"User Info - {user.name}", description=f"ID: {user.id}")
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.slash_command(description="Get information about the server")
async def serverinfo(interaction: nextcord.Interaction):
    server = interaction.guild
    embed = nextcord.Embed(title=f"Server Info - {server.name}", description=f"ID: {server.id}")
    if server.icon:
        embed.set_thumbnail(url=server.icon.url)
    embed.add_field(name="Owner", value=server.owner, inline=True)
    embed.add_field(name="Created On", value=server.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Member Count", value=server.member_count, inline=True)
    await interaction.response.send_message(embed=embed)


@bot.slash_command(description="Kick a user from the server")
@commands.has_permissions(kick_members=True)
async def kick(interaction: nextcord.Interaction, user: nextcord.Member, reason: str = None):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"{user.name} has been kicked from the server. Reason: {reason}")

@bot.slash_command(description="Ban a user from the server")
@commands.has_permissions(ban_members=True)
async def ban(interaction: nextcord.Interaction, user: nextcord.Member, reason: str = None):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"{user.name} has been banned from the server. Reason: {reason}")

@bot.slash_command(description="Clear messages in the channel")
@commands.has_permissions(manage_messages=True)
async def clear(interaction: nextcord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Cleared {amount} messages.", ephemeral=True)

bot.run('')
