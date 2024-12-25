# Discord Bot with Ollama, Llava & Music 🤖 🎵

A powerful Discord bot that combines local AI models (Ollama & Llava) with music playback features. Run advanced AI models locally while enjoying music and games!!

## Features 🌟

### AI Integration 🧠
- **Local AI Chat (llama3.2:latest)**
  - Run AI locally using Ollama
  - Fast response times
  - No API costs
  - Command: `!ask [question]`

- **Image Analysis (llava:latest)**
  - Local image processing
  - Detailed visual descriptions
  - No cloud dependencies
  - Command: `!analyze [prompt]`

### Music System 🎵
- **YouTube Integration**
  - Play from URLs or search terms
  - Queue management
  - High-quality playback

- **Music Controls**
  - `!play` - Play/queue songs
  - `!pause`/`!resume` - Control playback
  - `!skip` - Skip current song
  - `!queue` - View playlist
  - `!volume [0-200]` - Adjust volume

### Games 🎮
- **Rock Paper Scissors**
  - Challenge friends
  - Interactive buttons
  - Auto-scoring

## Setup Guide 🚀

### Prerequisites
- Python 3.8+
- FFmpeg
- Ollama
- Discord Bot Token
- 8GB RAM (16GB recommended)

### Quick Start
1. **Clone & Install**
```bash
git clone https://github.com/KermitEX/Discord_bot_with_local_ollama_llava_music.git
cd Discord_bot_with_local_ollama_llava_music
pip install -r requirements.txt
```

2. **Install Ollama**
```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh
# Windows: Download from ollama.ai/download
```

3. **Configure**
```bash
# Create .env file
DISCORD_TOKEN=your_token_here

# Pull AI models
ollama pull llama3.2:latest
ollama pull llava:latest
```

4. **Run**
```bash
python discord_ollama_bot.py
```

## Commands 💬

### AI Commands
- `!ask [question]` - Chat with AI
- `!analyze [prompt]` - Analyze images
- `!aihelp` - Show help

### Music Commands
- `!play [song]` - Play/queue music
- `!queue` or `!q` - Show queue
- `!skip` - Skip song
- `!pause` - Pause music
- `!resume` - Resume music
- `!stop` - Stop playback
- `!clear` - Clear queue
- `!volume [0-200]` - Set volume
- `!join` - Join voice
- `!leave` - Leave voice

### Game Commands
- `!rps @user` - Rock Paper Scissors

## Project Structure 📁
```
Discord_bot_with_local_ollama_llava_music/
├── discord_ollama_bot.py    # Main bot file
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── .env                    # Environment vars
└── .gitignore             # Git ignore rules
```

## Support 💡

### Need Help?
- **Discord Server**: Join our [community](https://discord.gg/eRV528xw7q) for:
  - Live support
  - Feature updates
  - Bug reports
  - Community discussions
  - Bot announcements

### Other Support
- Create GitHub issues for bugs
- Check documentation
- Report security issues via Discord DM

## License 📄

### Apache License 2.0

Copyright 2024 Discord Bot with Ollama, Llava & Music

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
- Discord.py team
- Ollama developers
- FFmpeg project
- yt-dlp maintainers
