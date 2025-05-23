# Train Color Matching Game

![Screenshot](https://github.com/dundd2/Train-Color-Matcher/blob/main/Screenshot/Screenshot%20(1).gif)

## Project Background

This project is my first attempt at creating an executable (.exe) file from a Python script, showcasing various programming skills for my portfolio. Before this project, I had no experience in converting Python code into an executable format. The inspiration came from a childhood memory of playing a similar game that left a lasting impression, and I wanted to recreate that enjoyable experience.

## Game Description

The Train Color Matching Game is where players match trains of the same colour. Features include:

- Multiple game states (Menu, Playing, Game Over)
- Light/dark theme options
- Interactive buttons with hover effects
- Dynamic background elements (trees, clouds, stars)

## Screenshot

![Screenshot](https://github.com/dundd2/Train-Color-Matcher/blob/main/Screenshot/Screenshot%20(2).png)
![Screenshot](https://github.com/dundd2/Train-Color-Matcher/blob/main/Screenshot/Screenshot%20(3).png)
![Screenshot](https://github.com/dundd2/Train-Color-Matcher/blob/main/Screenshot/Screenshot%20(4).png)


## Technical Skills Demonstrated

- Python programming fundamentals
- Pygame library implementation
- Particle effect systems
- State management
- UI/UX design
- File handling and resource management

## Development Tools

- Python: Core programming language
- Pygame: Game development library
- PyInstaller: Executable creation tool

## Creating the Executable

To convert the Python script into an executable file, I used the following steps:

1. **Install PyInstaller**: A tool for converting Python applications into standalone executables.

```bash
pip install pyinstaller
```

1. **Generate the Executable**: Run PyInstaller with the script.

```bash
pyinstaller --onefile train_color_matcher.py
```

1. **Distribute the Executable**: The generated `.exe` file can be found in the `dist` directory and can be shared with others.

## Gameplay Instructions

### How to Play

1. Start the game by clicking the "Start Game" button
2. Match the train colours from left to right
3. Click on the coloured train at the bottom that matches the leftmost train on the track
4. Score points for correct matches
5. The game ends when all trains are matched

### Controls

- Mouse Click: Select trains and interact with buttons
- Theme Toggle: Switch between light and dark modes
- Mute Button: Toggle sound effects and background music

## Technical Details

### Game Features in Detail

- **Particle System**: Creates visual effects when buttons are clicked
- **Dynamic Background**:
  - Moving clouds in both themes
  - Twinkling stars in dark mode
  - Decorative trees for the environment

### Code Structure

- **Main Classes**:
  - `ModernGame`: Main game controller
  - `Train`: Train object with movement and rendering
  - `ModernButton`: Enhanced button with hover effects
  - `Particle`: Visual effect system

### Animation Systems

- Train movement animations
- Button hover effects
- Particle effects
- Cloud movement
- Star twinkling (dark mode)

### Theme System

- Light and dark theme support
- Dynamic UI element adaptation
- Smooth theme transitions
- Theme-specific visual effects
