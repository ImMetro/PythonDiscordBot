# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 14:59:15 2020

@author: Peter
"""

import discord
import csv
from discord.ext import commands
import os
import pyshorteners
import random
import json
import string
import asyncio
import requests


def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix = get_prefix, help_command = None)

@client.event
async def on_ready():
    print("Bot is ready.")

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command(aliases=['music', 'sheets', 'notes', 'searchmn', 'musicnotes'])
async def _musicnotes(ctx, *, search):
    with open('musicnotesdatabasev1.csv') as csvfile:
        reader = csv.reader(csvfile)
        table = [row for row in reader]
        availableprints = [row for row in table if (row[2] != '' and row[2] != 'YeetYeet')]
        emailpass = [row[0] for row in availableprints]
        purchasedsheets = [row[1] for row in availableprints]
        f = open("sheetmusic.txt", "x")
        f = open("sheetmusic.txt", "w")
        f.write("Here are the accounts that contain your search\n")
        author = ctx.message.author
        a = 0
        for i in range(len(purchasedsheets)):
            if (search in purchasedsheets[i]):
                a += 1
                f = open("sheetmusic.txt", "a")
                f.write(emailpass[i] + "\n" + purchasedsheets[i] + "\n\n")
                f.close()
            else:
                a
        if (a != 0):
            await ctx.send(f'{author.mention} Your Search: **{search}**\nTurned up **{a}** results. The results have been forwarded to your dm')
            with open('sheetmusic.txt', 'rb') as fp:
                        channel = await author.create_dm()
                        await channel.send(f'Here is everything related to **{search}**.')
                        await channel.send(file=discord.File(fp, 'sheetmusic.txt'))
            os.remove("sheetmusic.txt")
        else:
            await ctx.send(f'{author.mention}, Unfortunately your search for: **{search}** yielded no results')
            f.close()
            os.remove("sheetmusic.txt")

@client.command()
async def shortentiny(ctx, *,link):
    shortener = pyshorteners.Shortener()
    x = shortener.tinyurl.short(link)
    await ctx.send(f"Original Link: {link}\nShortened Link: {x}")

@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

chars = "ABCDEFGHIJKLMNOPQRSTUVWQ1234567890"

@client.command()
async def genkeys(ctx, amount):
    f = open("keys.txt", "a")
    for i in range(int(amount)):
        key = ''
        for i in range(16):
            x = random.randint(35,61)
            key += string.printable[x]
        f.write('SHORTEN-'+key+'\n')
    f.close()
    await ctx.send(f'**{amount}** keys have been generated and added to the database\nAn event log of this key generation has been forwarded to the owner of this bot.')


@client.command()
async def changeprefix(ctx, newprefix):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = newprefix

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)



@client.command()
async def getlinks(ctx):
    await ctx.channel.purge(limit=1)
    url = "https://api.rebrandly.com/v1/links"
    querystring = {"orderBy":"createdAt","orderDir":"desc","limit":"25"}
    headers = {"apikey": "bcfbd79949354f1eac41617974693207"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    f = open("links.txt", "x")
    f = open("links.txt", "w")
    f.write("Here are your current links\n")
    f = open("links.txt", "a")
    f.write(response.text + "\n")
    f.close()
    with open('links.txt', 'rb') as fp:
        await ctx.send(f'Here are your **links**.')
        await ctx.send(file=discord.File(fp, 'links.txt'))
    os.remove("links.txt")

@client.command()
async def shorten(ctx, link, tag, key):
    await ctx.channel.purge(limit=1)
    with open("keys.txt") as txtfile:
        if key in txtfile.read():
            author = ctx.message.author #This is the tag, if they change their name we fucked, so we use the id
            author1 = str(author)
            USER_ID = str(ctx.message.author.id) #This is the id

            linkRequest = {
            "destination": link
            , "domain": { "fullName": "ngek.me" }
            , "slashtag": tag
            }

            requestHeaders = {
            "Content-type": "application/json",
            "apikey": "bcfbd79949354f1eac41617974693207",
            "workspace": "327641910e3f4a55b5e3b164fb7eda7b"
            }

            r = requests.post("https://api.rebrandly.com/v1/links",
            data = json.dumps(linkRequest),
            headers=requestHeaders)

            if (r.status_code == requests.codes.ok):
                link = r.json()
                channel = await author.create_dm()
                await channel.send(f"{author.mention}\nLong URL was %s, short URL is %s" % (link["destination"], link["shortUrl"]))
                embed=discord.Embed(title="Success", description="Your request has been processed, check your DMs!", color=0x1cd431)
                embed.set_thumbnail(url="https://i.imgur.com/1MTgUdy.jpg")
                await ctx.send(embed=embed)
                f = open("keys.txt", "r")
                filedata = f.read()
                f.close()
                newdata = filedata.replace(key, '')
                f = open("keys.txt", "w")
                f.write(newdata)
                f.close()
                f = open("customers.txt", "a")
                f.write(USER_ID+","+author1+"\n")
            else:
                embed=discord.Embed(title="Invalid Url/Key", description="If you think this is a mistake, please contact the support team.", color=0xff0000)
                embed.set_thumbnail(url="https://imgur.com/a/M1mT1Oz")
                await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Invalid Url/Key", description="If you think this is a mistake, please contact the support team.", color=0xff0000)
            embed.set_thumbnail(url="https://i.imgur.com/vKsW3MZ.jpg")
            await ctx.send(embed=embed)

@client.command()
async def usage(ctx):
    await ctx.channel.purge(limit=1)
    embed=discord.Embed(title="How to use this bot", description="Usage of this bot is simple. All you have to provide are three things. The URL you want shortened, the Slashtag of the shortened link and the key that you have purchased.", color=0xffffff)
    embed.add_field(name="URL Definition", value="The URL must be a link, a simple 'google.com' will not suffice. Links start with https://", inline=False)
    embed.add_field(name="What is a Slashtag?", value="Shortened URL's for example tinyurl.com/slashtag. The slashtag is what you want after the domain name, keep this to one work", inline=False)
    embed.add_field(name="Key? ", value="To use this bot, a key is required if you do not have a key, you cannot use this bot. However, we do offer a free 30 minute trial where a link of your choice will active for thirty minutes", inline=False)
    embed.add_field(name="Examples", value="!!shorten https://www.youtube.com YouTube (key) will yield **ngek.com/YouTube**", inline=False)
    embed.add_field(name="Example URL's", value="ngek.me/nulled and ngek.me/cracked", inline=False)
    embed.add_field(name="Custom Domains?", value="Custom Domains are available for $22 and you will have this domain for aslong as this service is active. ", inline=False)
    embed.set_footer(text="yea#9058")
    await ctx.send(embed=embed)

client.run('NzA0Mjc2NjM3MDg4NDgxMzU0.Xqayuw.AGLAqs0KDmHVYT8TbESZdutr1Ug')
