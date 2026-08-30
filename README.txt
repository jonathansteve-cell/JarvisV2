================================================================================
                    JARVIS V2 - ALL-IN-ONE DESKTOP AI ASSISTANT
================================================================================

Version: 2.0.0
Author: jonathansteve-cell
License: MIT
Platform: Windows | macOS | Linux

================================================================================
                              OVERVIEW
================================================================================

Jarvis V2 is a comprehensive desktop AI assistant that combines voice control,
automated research, gaming assistance, and productivity tools into a single
application.

Features:
  - Voice recognition and text-to-speech
  - AI-powered conversations (Groq, OpenAI, Anthropic)
  - System control (volume, apps, screenshots)
  - Web search and automation
  - Email, WhatsApp, and phone integration
  - Spotify music control
  - Smart home integration
  - Research mode
  - Roblox grind mode
  - Serious mode (productivity workspaces)

================================================================================
                            QUICK START
================================================================================

1. INSTALLATION

   Windows:
     - Run JarvisV2-Setup.exe
     - Or extract JarvisV2-Portable-2.0.0.zip

   From Source:
     - Run start.bat (Windows)
     - Run ./run_local.sh (Linux/macOS)

2. FIRST LAUNCH

   - Run the application
   - Complete the setup wizard
   - Create your account
   - Configure API keys (optional)
   - Start using Jarvis!

3. BASIC COMMANDS

   "Hey Jarvis, what time is it?"
   "Hey Jarvis, system status"
   "Hey Jarvis, tell me a joke"

================================================================================
                              COMMANDS
================================================================================

SYSTEM COMMANDS:
  system status          - Show system information
  cpu status             - Show CPU usage
  memory status          - Show memory usage
  battery level          - Show battery level

TIME COMMANDS:
  what time is it        - Get current time
  what is today's date   - Get current date

FUN COMMANDS:
  tell me a joke         - Hear a joke
  what can you do        - List capabilities

RESEARCH COMMANDS:
  research about [topic] - Start researching
  add note: [text]       - Add a research note
  generate report        - Create research report

ROBLOX COMMANDS:
  start roblox grind     - Begin grinding
  set roblox goal: [goal]- Set a goal
  roblox grind status    - Check status
  end grind session      - Stop grinding

WORKSPACE COMMANDS:
  open coding workspace  - Open coding environment
  open study mode        - Open study environment
  enable focus mode      - Block distractions

================================================================================
                            API SETUP
================================================================================

Configure external APIs for enhanced functionality:

1. Groq AI (Recommended)
   - Get key at: https://console.groq.com
   - Add to .env: GROQ_API_KEY=your_key

2. OpenAI (Alternative)
   - Get key at: https://platform.openai.com
   - Add to .env: OPENAI_API_KEY=your_key

3. Email (Gmail)
   - Enable 2FA on Google account
   - Generate App Password
   - Add to .env: JARVIS_EMAIL_ADDRESS=you@gmail.com

4. Twilio (WhatsApp/Phone)
   - Get credentials at: https://console.twilio.com
   - Add to .env: TWILIO_ACCOUNT_SID=your_sid

5. Spotify
   - Get credentials at: https://developer.spotify.com
   - Add to .env: SPOTIFY_CLIENT_ID=your_id

================================================================================
                          CONFIGURATION
================================================================================

Configuration files:
  config/config.json     - Main configuration
  config/api_config.json - API settings
  .env                   - Environment variables (API keys)

User data:
  data/users.json        - User accounts
  data/current_user.json - Current session
  data/user_preferences.json - User settings

================================================================================
                            FEATURES
================================================================================

RESEARCH MODE:
  - Automated topic research
  - Wikipedia integration
  - Web search
  - Organized folder structure
  - Report generation

ROBLOX GRIND MODE:
  - 8 popular grind games
  - Session tracking
  - Robux estimation
  - Goal management
  - Statistics history

SERIOUS MODE:
  - 10 predefined workspaces
  - Automatic app launching
  - Website opening
  - Focus mode
  - Study tips

================================================================================
                          TROUBLESHOOTING
================================================================================

Problem: Application won't start
Solution: Make sure Python 3.10+ is installed and added to PATH.

Problem: Voice not working
Solution: Check microphone permissions and install PyAudio:
  pip install pyaudio

Problem: API errors
Solution: Verify your API keys in the Settings panel.

Problem: Build failed
Solution: Install all dependencies:
  pip install -r requirements.txt

================================================================================
                            SUPPORT
================================================================================

GitHub: https://github.com/jonathansteve-cell/JarvisV2
Issues: https://github.com/jonathansteve-cell/JarvisV2/issues

================================================================================
                              LICENSE
================================================================================

MIT License

Copyright (c) 2026 jonathansteve-cell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

================================================================================
