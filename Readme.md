# Luna - Discord AI Music Bot 🤖 🎵

A versatile Discord bot combining AI capabilities with music features. Luna can chat intelligently, analyze images, play music, and manage song queues.

## Features 🌟

### AI Features 🧠
- **Chat with Luna (!ask)**
  - Powered by llama3.2:latest (2.0 GB)
  - Natural, personality-driven responses
  - Casual and friendly conversation style

- **Image Analysis (!analyze)**
  - Powered by llava:latest (4.7 GB)
  - Detailed image descriptions
  - Visual content understanding

### Music Features 🎵
- **Music Playback**
  - Play from YouTube URLs or search terms
  - Queue management system
  - High-quality audio streaming

- **Playback Controls**
  - `!play` - Play a song
  - `!pause`/`!resume` - Control playback
  - `!skip` - Skip current song
  - `!queue` - View song queue
  - `!volume [0-200]` - Adjust volume

### Gaming Features 🎮
- Rock Paper Scissors (`!rps @user`)
  - Challenge other users
  - Interactive buttons
  - Automatic scoring

## Setup Guide 🚀

### Prerequisites
- Python 3.8+
- FFmpeg
- Ollama
- Discord Bot Token
- 8GB RAM (16GB recommended)

### Installation Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd discord-ai-music-bot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Ollama**
- Linux/Mac: `curl https://ollama.ai/install.sh | sh`
- Windows: Download from [ollama.ai/download](https://ollama.ai/download)

4. **Configure Bot**
- Create `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

5. **Pull AI Models**
```bash
ollama pull llama3.2:latest
ollama pull llava:latest
```

6. **Start Bot**
```bash
python discord_ollama_bot.py
```

## Commands 💬

### AI Commands
- `!ask [question]` - Chat with Luna
- `!analyze [prompt]` - Analyze an image
- `!aihelp` - Show help message

### Music Commands
- `!play [song]` - Play or queue a song
- `!queue` or `!q` - View current queue
- `!skip` - Skip current song
- `!pause` - Pause playback
- `!resume` - Resume playback
- `!stop` - Stop playback
- `!clear` - Clear queue
- `!volume [0-200]` - Set volume
- `!join` - Join voice channel
- `!leave` - Leave voice channel

### Game Commands
- `!rps @user` - Play Rock Paper Scissors

## Project Structure 📁
```
discord-ai-music-bot/
├── discord_ollama_bot.py    # Main bot file
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── .gitignore             # Git ignore rules
```

## Troubleshooting 🔧

### Common Issues
1. **Bot Won't Connect**
   - Check Discord token
   - Verify internet connection
   - Confirm bot permissions

2. **Music Won't Play**
   - Verify FFmpeg installation
   - Check voice permissions
   - Ensure valid YouTube URL

3. **AI Not Responding**
   - Ensure Ollama is running
   - Verify model installation
   - Check system resources

## Required Permissions 🔑
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Connect to Voice
- Speak in Voice
- Use Voice Activity

## Support 💡

### Need Help?
- **Discord Server**: Join our [community](https://discord.gg/eRV528xw7q) for:
  - Live support
  - Feature updates
  - Bug reports
  - Community discussions
  - Bot announcements

### Other Support Channels
- Create an issue on GitHub for bug reports
- Check documentation for guides
- Report security issues via Discord DM to admins

## License 📄

### Apache License 2.0

Copyright 2024 Luna Discord AI Music Bot

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Acknowledgments 🙏
- Discord.py developers
- Ollama team
- FFmpeg project
- yt-dlp maintainers