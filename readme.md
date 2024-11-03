# Train Color Matching Game

## Introduction

This project showcases my skills in developing a Python application using Pygame. It is part of my portfolio and represents my first attempt at creating an executable (.exe) file from a Python script. Prior to this, I had no experience in converting Python code into an executable format. The idea for this game stems from a childhood memory of a similar game that I found incredibly fun, and I wanted to recreate that experience.

## About the Game

The Train Color Matching Game is a simple yet engaging game where players match the colors of trains. The game features:

- **Menu, Playing, and Game Over States**: The game transitions between different states, providing a complete gaming experience.
- **Sound Effects and Background Music**: The game includes various sound effects and background music to enhance the player experience.
- **Light and Dark Themes**: Players can switch between light and dark themes for a better visual experience.
- **Interactive Buttons**: Modern buttons with hover effects and particle animations.
- **Dynamic Background Elements**: Trees, clouds, and stars that add to the visual appeal of the game.

## Technologies Used

- **Python**: The core programming language used for the game logic.
- **Pygame**: A set of Python modules designed for writing video games, used for rendering graphics and handling game events.
- **Sound Management**: Implemented using Pygame's mixer module to handle sound effects and background music.
- **Particle System**: Used for creating visual effects like button hover animations.

## Features

- **Train Matching**: Players match the colors of trains to score points.
- **Sound Effects**: Correct and wrong matches trigger different sound effects.
- **Theme Toggle**: Switch between light and dark themes.
- **Dynamic Background**: Includes moving clouds and glowing stars in dark mode.
- **High Score Tracking**: Keeps track of the highest score achieved.

## Creating the Executable

To convert the Python script into an executable file, I used the following steps:

1. **Install PyInstaller**: A tool for converting Python applications into standalone executables.
    ```bash
    pip install pyinstaller
    ```
2. **Generate the Executable**: Run PyInstaller with the script.
    ```bash
    pyinstaller --onefile train_color_matcher.py
    ```
3. **Distribute the Executable**: The generated `.exe` file can be found in the `dist` directory and can be shared with others.

## Conclusion

This project not only demonstrates my ability to develop a complete game using Python and Pygame but also my capability to package and distribute the application as an executable file. It has been a rewarding experience, and I hope you enjoy playing the Train Color Matching Game as much as I enjoyed creating it.
