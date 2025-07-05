# Contributing

Want to help make Dobby better? Cool! Here's how to get started.

## Getting set up

1. Fork this repo on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/-dobby-ai-rephraser.git
   cd -dobby-ai-rephraser
   ```
3. Install what you need:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the config template and add your API key:
   ```bash
   cp config_template.py config.py
   # Edit config.py and paste your Fireworks AI API key
   ```
5. Test it works:
   ```bash
   python dobby_qt.py
   ```

## What you need

- Python 3.8 or newer
- A Fireworks AI API key (for testing)
- Some kind of code editor

## Project layout

```
dobby_qt.py          # Main app
config_template.py   # Config file template
build_exe.py         # Builds the EXE
requirements.txt     # Dependencies
dobby_logo.png       # Logo
button_icon.png      # Button icon
```

To build an EXE: `python build_exe.py`

## Ways to help

### Found a bug?

Just open an issue and tell me:
- What you were doing
- What happened vs what you expected
- Your OS and Python version (if running from source)
- Screenshots help too

### Got an idea?

Open an issue with your suggestion. Even small improvements are welcome.

### Want to code?

Here are some easy things to start with:
- Fix typos in docs
- Add new writing styles
- Improve the UI
- Fix small bugs

### Making changes

1. Create a branch: `git checkout -b your-feature-name`
2. Make your changes
3. Test it: `python dobby_qt.py`
4. Commit: `git commit -m "Brief description"`
5. Push and create a pull request

That's it.

### Code style

Try to keep it readable. Use descriptive variable names, add comments where things get complex. 

For commit messages, just be clear about what you changed:
- `Add new writing style`
- `Fix tray icon bug`
- `Update docs`

### Ideas for contributions

**New writing styles**: Edit `config_template.py` and add a new style to the `WRITING_STYLES` dictionary. Test it with different types of text.

**UI improvements**: Better icons, colors, error messages, whatever makes it nicer to use.

**New features**: Different hotkeys, settings export, usage stats, support for other languages.

**Bug fixes**: Always welcome.

## Testing

Before submitting changes, make sure the basic stuff works:
- F2 hotkey
- All writing styles 
- System tray
- API key setup

Try some edge cases too - long text, special characters, no internet connection.

## Getting help

If you're stuck, just open an issue. I'm happy to help.

## Code of conduct

Be nice. Help others. That's about it.

---

Thanks for helping make Dobby better!