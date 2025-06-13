# Mouse Jiggler

A professional tool to keep your system active by moving the mouse with advanced features and customization options.

## Features

- Multiple mouse movement patterns (horizontal, circular, random)
- Pause/Resume functionality
- System tray support
- CPU usage monitoring
- Progress tracking
- Dark/Light theme
- Keyboard shortcuts
- Settings persistence
- Cross-platform support

## Quick Start (Windows Users)

1. Go to the [releases](releases) directory
2. Download `Mouse Jiggler.exe`
3. Double-click to run
4. No installation required

## Installation Options

### Option 1: Using the Executable (Recommended for Windows)
1. Download the `Mouse Jiggler.exe` from the [releases](releases) directory
2. Double-click to run
3. No installation required

### Option 2: Running from Source
1. Install Python 3.8 or higher
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Linux Users

1. Install Python 3.8 or higher
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Keyboard Shortcuts

- `Ctrl+S`: Start
- `Ctrl+P`: Pause/Resume
- `Ctrl+X`: Stop
- `Ctrl+Q`: Quit

## Settings

The application will save your settings automatically in a `settings.json` file in the same directory. This includes:
- Movement pattern preference
- Theme preference
- Window position and size

## System Requirements

- Windows 10/11 or Linux
- Python 3.8+ (for running from source)
- 100MB free disk space
- 512MB RAM

## Troubleshooting

If you encounter any issues:
1. Make sure all dependencies are installed correctly
2. Check if you have the required permissions
3. Try running as administrator (Windows)
4. Check the activity log for error messages

## Building from Source

To build the executable yourself:
1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
2. Run the build command:
   ```
   pyinstaller mouse_jiggler.spec
   ```
3. The executable will be created in the `dist` directory

## License

This project is open source and free to use.

## Author

Developed by Niyas 