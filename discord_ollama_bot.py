import discord
from discord.ext import commands
import ollama
import os
from dotenv import load_dotenv
from config import Config
import random
import aiohttp
import tempfile
import asyncio
from functools import partial
import yt_dlp as youtube_dl

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Add voice state intent
bot = commands.Bot(command_prefix=Config.COMMAND_PREFIX, intents=intents)

# Store active games
active_games = {}

# Music settings
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

async def get_ollama_response(prompt, model=Config.CHAT_MODEL):
    """Get response from Ollama model"""
    try:
        response = ollama.generate(model=model, prompt=prompt)
        return response['response']
    except Exception as e:
        return f"Error: {str(e)}"

async def get_llava_response(image_path, prompt):
    """Get response from Llava model for image analysis"""
    try:
        # Run ollama.generate in a thread pool to prevent blocking
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                ollama.generate,
                model=Config.VISION_MODEL,
                prompt=prompt,
                images=[image_path]
            )
        )
        return response['response']
    except Exception as e:
        return f"Error processing image: {str(e)}"

async def download_image(url, max_size=10 * 1024 * 1024):  # 10MB limit
    """Download image from URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception("Failed to download image")
            if int(response.headers.get('Content-Length', 0)) > max_size:
                raise Exception("Image too large (max 10MB)")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(await response.read())
            temp_file.close()
            return temp_file.name

# Music-related commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize queue as a dictionary of guild_id: [songs]
        self.queues = {}
        self.volume = Config.DEFAULT_VOLUME
        self.now_playing = {}  # Track currently playing song

    async def play_next(self, ctx):
        """Play the next song in the queue"""
        if not ctx.guild.id in self.queues or not self.queues[ctx.guild.id]:
            self.now_playing[ctx.guild.id] = None
            return
            
        # Get the next song from queue
        url = self.queues[ctx.guild.id].pop(0)
        
        try:
            # Get song info
            data = await self.bot.loop.run_in_executor(
                None, 
                lambda: ytdl.extract_info(url, download=False)
            )
            
            if 'entries' in data:
                data = data['entries'][0]
                
            url = data['url']
            title = data['title']
            
            # Create audio source
            source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
            
            # Play the song
            ctx.voice_client.play(
                source, 
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx),
                    self.bot.loop
                ).result() if not e else print(f'Player error: {e}')
            )
            
            self.now_playing[ctx.guild.id] = title
            await ctx.send(f'🎵 Now playing: **{title}**')
            
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            await self.play_next(ctx)

    @commands.command(name='join')
    async def join(self, ctx):
        """Join the user's voice channel"""
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")
        
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        await ctx.send(f"Joined {channel.name}!")

    @commands.command(name='play')
    async def play(self, ctx, *, query):
        """Play a song or add it to queue"""
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        async with ctx.typing():
            try:
                processing_msg = await ctx.send("🔍 Searching for the song...")
                
                # Extract song info
                data = await self.bot.loop.run_in_executor(
                    None, 
                    lambda: ytdl.extract_info(query, download=False)
                )
                
                if 'entries' in data:
                    data = data['entries'][0]
                
                url = data['webpage_url']  # Store webpage_url instead of direct URL
                title = data['title']
                
                # Initialize queue for this guild if it doesn't exist
                if ctx.guild.id not in self.queues:
                    self.queues[ctx.guild.id] = []
                
                # If nothing is playing, play directly without adding to queue
                if not ctx.voice_client.is_playing():
                    try:
                        source = await discord.FFmpegOpusAudio.from_probe(
                            data['url'], 
                            **ffmpeg_options
                        )
                        ctx.voice_client.play(
                            source,
                            after=lambda e: asyncio.run_coroutine_threadsafe(
                                self.play_next(ctx),
                                self.bot.loop
                            ).result() if not e else print(f'Player error: {e}')
                        )
                        self.now_playing[ctx.guild.id] = title
                        await processing_msg.edit(content=f'🎵 Now playing: **{title}**')
                    except Exception as e:
                        await ctx.send(f"❌ An error occurred while playing: {str(e)}")
                else:
                    # Add to queue if something is already playing
                    self.queues[ctx.guild.id].append(url)
                    position = len(self.queues[ctx.guild.id])
                    await processing_msg.edit(content=f'📝 Added to queue (Position {position}): **{title}**')
                    
            except Exception as e:
                await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop playing"""
        if not ctx.voice_client:
            return await ctx.send("I'm not playing anything!")
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏹️ Stopped playing")
        else:
            await ctx.send("Nothing is playing right now!")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the currently playing song"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused")
        else:
            await ctx.send("Nothing is playing right now!")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the currently paused song"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed")
        else:
            await ctx.send("Nothing is paused right now!")

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel")
        else:
            await ctx.send("I'm not in a voice channel!")

    @commands.command(name='volume')
    async def volume(self, ctx, volume: int):
        """Change volume (0-200)"""
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel!")

        if not 0 <= volume <= 200:
            return await ctx.send("Volume must be between 0 and 200!")

        if ctx.voice_client.source:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"🔊 Volume set to {volume}%")
        else:
            await ctx.send("Nothing is playing right now!")

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """Show the current queue"""
        if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
            return await ctx.send("Queue is empty!")
            
        # Create queue embed
        embed = discord.Embed(title="Song Queue", color=discord.Color.blue())
        
        # Add currently playing song
        if ctx.guild.id in self.now_playing and self.now_playing[ctx.guild.id]:
            embed.add_field(
                name="Now Playing",
                value=f"🎵 {self.now_playing[ctx.guild.id]}",
                inline=False
            )
        
        # Add queued songs
        queue_list = []
        for i, url in enumerate(self.queues[ctx.guild.id], 1):
            try:
                info = ytdl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                queue_list.append(f"{i}. {title}")
            except:
                queue_list.append(f"{i}. Error getting title")
                
        if queue_list:
            embed.add_field(
                name="Up Next",
                value="\n".join(queue_list[:10]),  # Show first 10 songs
                inline=False
            )
            
            if len(queue_list) > 10:
                embed.set_footer(text=f"And {len(queue_list) - 10} more songs...")
        
        await ctx.send(embed=embed)

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skip the current song"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("Nothing is playing!")
            
        ctx.voice_client.stop()  # This will trigger play_next() automatically
        await ctx.send("⏭️ Skipped the current song")

    @commands.command(name='clear')
    async def clear(self, ctx):
        """Clear the queue"""
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
        await ctx.send("🗑️ Queue cleared!")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name=Config.PLAYING_STATUS))
    
    # Pull the Llava model at startup
    try:
        ollama.pull(Config.VISION_MODEL)
        print("Llava model pulled successfully")
    except Exception as e:
        print(f"Error pulling Llava model: {e}")

    # Add music cog
    await bot.add_cog(Music(bot))

@bot.command(name='ask')
async def ask(ctx, *, question):
    """Command to ask a question to the Ollama model"""
    async with ctx.typing():
        response = await get_ollama_response(question)
        await ctx.reply(response)

@bot.command(name='analyze')
async def analyze(ctx, *, prompt=None):
    """Analyze an image using Llava"""
    if not ctx.message.attachments:
        await ctx.reply("Please attach an image to analyze!")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.content_type.startswith('image/'):
        await ctx.reply("Please provide a valid image file!")
        return

    async with ctx.typing():
        try:
            # Download the image
            image_path = await download_image(attachment.url)
            
            # Default prompt if none provided
            if not prompt:
                prompt = "Describe this image in detail."

            # Send initial response to let user know processing has started
            await ctx.reply("Processing your image... This may take a minute.")

            # Get response from Llava
            response = await get_llava_response(image_path, prompt)
            
            # Clean up temporary file
            os.unlink(image_path)
            
            await ctx.reply(response)
        except Exception as e:
            await ctx.reply(f"Error: {str(e)}")

@bot.command(name='aihelp')
async def aihelp(ctx):
    """Custom help command"""
    help_text = """
    **Available Commands:**
    
    AI Commands:
    `!ask [question]` - Ask a question to the AI
    `!analyze [prompt]` - Analyze an attached image (optional prompt)
    
    Music Commands:
    `!join` - Join your voice channel
    `!play [song]` - Play a song (URL or search term)
    `!stop` - Stop playing music
    `!leave` - Leave the voice channel
    
    Game Commands:
    `!rps @user` - Challenge someone to Rock Paper Scissors
    
    Other Commands:
    `!aihelp` - Show this help message
    
    **Examples:**
    `!ask What is artificial intelligence?`
    `!analyze What objects are in this image?` (with attached image)
    `!play Despacito`
    `!rps @friend`
    """
    await ctx.send(help_text)

@bot.command(name='rps')
async def rps(ctx, opponent: discord.Member):
    """Challenge someone to Rock Paper Scissors"""
    if opponent.bot:
        await ctx.send("You can't challenge a bot!")
        return
    
    if opponent == ctx.author:
        await ctx.send("You can't challenge yourself!")
        return

    game_id = str(ctx.message.id)
    
    # Create buttons
    view = discord.ui.View()
    accept_button = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label="Accept Challenge",
        custom_id=f"accept_rps_{game_id}"
    )
    
    async def accept_callback(interaction):
        if interaction.user != opponent:
            await interaction.response.send_message("This challenge isn't for you!", ephemeral=True)
            return
            
        # Create choice buttons for both players
        choices = ['🪨 Rock', '📄 Paper', '✂️ Scissors']
        active_games[game_id] = {
            'challenger': ctx.author.id,
            'opponent': opponent.id,
            'choices': {}
        }
        
        for player in [ctx.author, opponent]:
            choice_view = discord.ui.View()
            for choice in choices:
                button = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label=choice,
                    custom_id=f"rps_choice_{game_id}_{choice}"
                )
                choice_view.add_item(button)
            
            await player.send("Make your choice:", view=choice_view)
        
        await interaction.response.edit_message(content="Game started! Check your DMs to make your choice.", view=None)
    
    accept_button.callback = accept_callback
    view.add_item(accept_button)
    
    await ctx.send(f"{opponent.mention}, {ctx.author.name} challenges you to Rock Paper Scissors!", view=view)

@bot.event
async def on_interaction(interaction):
    if not interaction.data['custom_id'].startswith('rps_choice_'):
        return
        
    _, _, game_id, choice = interaction.data['custom_id'].split('_', 3)
    
    if game_id not in active_games:
        await interaction.response.send_message("This game has expired!", ephemeral=True)
        return
        
    game = active_games[game_id]
    player_id = interaction.user.id
    
    if player_id not in [game['challenger'], game['opponent']]:
        await interaction.response.send_message("This isn't your game!", ephemeral=True)
        return
        
    if player_id in game['choices']:
        await interaction.response.send_message("You've already made your choice!", ephemeral=True)
        return
        
    game['choices'][player_id] = choice
    await interaction.response.send_message(f"You chose {choice}!", ephemeral=True)
    
    if len(game['choices']) == 2:
        # Both players have made their choices
        challenger_choice = game['choices'][game['challenger']]
        opponent_choice = game['choices'][game['opponent']]
        
        # Determine winner
        choices = {'Rock': 0, 'Paper': 1, 'Scissors': 2}
        challenger_value = choices[challenger_choice.split()[1]]
        opponent_value = choices[opponent_choice.split()[1]]
        
        diff = (challenger_value - opponent_value) % 3
        
        challenger = await bot.fetch_user(game['challenger'])
        opponent = await bot.fetch_user(game['opponent'])
        
        result_message = (
            f"**Results:**\n"
            f"{challenger.name}: {challenger_choice}\n"
            f"{opponent.name}: {opponent_choice}\n\n"
        )
        
        if diff == 0:
            result_message += "It's a tie!"
        elif diff == 1:
            result_message += f"{challenger.name} wins!"
        else:
            result_message += f"{opponent.name} wins!"
            
        await challenger.send(result_message)
        await opponent.send(result_message)
        
        del active_games[game_id]

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main() 