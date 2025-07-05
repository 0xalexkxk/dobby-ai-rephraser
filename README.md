# Dobby AI Rephraser

<p align="center">
  <img src="dobby_logo.png" alt="Dobby Logo" width="120">
</p>

Ever wanted to quickly change the tone of your text? Maybe make an angry message sound friendlier, or turn a casual note into something more professional? That's exactly what Dobby does.

Just highlight any text anywhere on your computer, press F2, pick a style, and boom - your text is rewritten in seconds.

## What it does

This little tool helps you rewrite text in different styles:

- **Friendly** - Makes things sound warmer and more approachable
- **Professional** - Perfect for work emails and formal documents  
- **Polite** - When you need to be extra respectful
- **Casual** - For relaxed, everyday conversation
- **Supportive** - Encouraging and uplifting tone
- **Unhinged** - When you want to be... well, completely unfiltered

The best part? It works with any app. Writing in Discord, Word, your browser, whatever - just select text and hit F2.

## How to get it

**Easy way:** Download `DobbyAI-Rephraser.exe` from the [Releases page](https://github.com/0xalexkxk/-dobby-ai-rephraser/releases) and run it. That's it.

**Build it yourself:** If you want to create your own EXE or modify the code:
```bash
git clone https://github.com/0xalexkxk/-dobby-ai-rephraser.git
cd -dobby-ai-rephraser
pip install -r requirements.txt

# To run from source:
python dobby_qt.py

# To build your own EXE:
python build_exe.py
```

The `build_exe.py` script will create `DobbyAI-Rephraser.exe` for you.

## First time setup

You'll need an API key from Fireworks AI. Don't worry, it's free and takes about 2 minutes.

When you run the app for the first time, it'll ask for this key.

### Getting the API key

1. Go to [fireworks.ai](https://fireworks.ai) and sign up
2. Find the "API Keys" section in your dashboard
3. Create a new key and copy it (starts with `fw_`)
4. Paste it into the dialog that pops up

That's it. The key gets saved on your computer and you won't need to do this again.

Don't worry about security - your key stays local, nothing gets stored or tracked.

## How to use it

1. Highlight some text anywhere on your computer
2. Press F2
3. Pick a style from the 6 buttons
4. Hit "Generate Text"
5. Either copy the result or click "Paste" to replace your original text

The app sits in your system tray (bottom right corner), so it's always ready when you need it.

### The different styles

**Friendly** - Makes text warmer and more approachable  
*"Hey, hope you're doing well!" instead of "Hello."*

**Professional** - Perfect for work emails and formal stuff  
*"I would like to request..." instead of "I want..."*

**Polite** - Extra respectful and courteous  
*"Would it be possible to..." instead of "Can you..."*

**Casual** - Relaxed, everyday conversation  
*"That's pretty cool" instead of "That is beneficial"*

**Supportive** - Encouraging and uplifting  
*"You've got this!" instead of "Good luck"*

**Unhinged** - Zero filter, says exactly what it thinks  
*"This is fucking awesome" instead of "This is great"*

### Quick tips

- The app runs in your system tray - double-click the icon to bring it back up
- Closing the window doesn't quit the app, it just hides it
- To actually exit, right-click the tray icon and choose "Exit"
- ESC key also closes the window

## Building your own EXE

If you want to build the EXE yourself:

```bash
pip install pyinstaller
python build_exe.py
```

## Requirements

- Windows 10 or 11
- Internet connection (for the AI processing)
- If running from Python: Python 3.8+

## Cost

The AI processing uses Fireworks AI, which is pretty cheap. Most people spend less than a couple dollars per month, even with regular use. Each rephrase costs fractions of a penny.

## Contributing

Found a bug? Want to add a new writing style? Feel free to open an issue or submit a pull request. 

Check out [CONTRIBUTING.md](CONTRIBUTING.md) if you want to get involved.

## License

MIT License - basically, do whatever you want with this code.

## Credits

- Uses [Fireworks AI](https://fireworks.ai/) for the text processing
- Built with PyQt6 for the interface

## Troubleshooting

**App asks for API key every time**  
Delete `config.py` and restart. The setup dialog should appear and save your key properly.

**"API Error 401" or similar**  
Your API key is probably wrong or expired. Get a new one from fireworks.ai and make sure it starts with `fw_`.

**F2 doesn't work**  
Make sure you actually selected/highlighted some text first. The app needs to see that there's text in your clipboard.

**Window disappeared**  
Look for the Dobby icon in your system tray (bottom-right corner). Double-click it to bring the window back.

**Slow or stuck**  
Check your internet - the AI processing happens online. Sometimes it just takes a few seconds.

**Can't close the app**  
Right-click the tray icon and choose "Exit". Just closing the window only hides it.

---

If you run into other issues, feel free to [open an issue](https://github.com/0xalexkxk/-dobby-ai-rephraser/issues) on GitHub.