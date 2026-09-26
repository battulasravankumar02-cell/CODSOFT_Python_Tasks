# Rock • Paper • Scissors

A modern, responsive, and interactive Rock-Paper-Scissors web application built with **Python (Flask)**, HTML5, CSS3, and JavaScript. Inspired by the gaming showcase reference artwork, the application features an illustrated hero landing card, top-bar navigation tabs, **Single Player (vs Computer)**, **Duo 2-Player Pass & Play**, real-time **Scoreboards**, **Score Reset**, and dynamic **Dark/Light Theme customization** in a centered tablet-sized layout (700px–860px).

---

## CODSOFT Internship
**Task 4 — Rock-Paper-Scissors Game**  
*Track: Python Programming*

This project fulfills all primary objectives and extensions for CODSOFT Task 4 by implementing a robust Python backend that handles all core game logic, computer randomized moves, duo player battle calculations, score tracking, and round presentations.

---

## Features & Navigation Tabs

The application features an integrated top navigation bar with 5 accessible views:

### 1. Home Showcase (Matching Visual Reference)
- Bold, tall typography (**ROCK / PAPER / SCISSORS**).
- Hand-crafted illustrated clash artwork (Rock fist vs Scissors hand with glowing neon outlines, orange/teal auras, and floating bokeh particles).
- Direct CTA buttons: `PLAY SINGLE PLAYER`, `PLAY DUO PLAYER`.
- Live mini score strip showing current active player scores.

### 2. Single Player (`PLAYER VS COMPUTER`)
- Choose **🪨 ROCK**, **📄 PAPER**, or **✂ SCISSORS**.
- The computer's choice is randomly generated using Python's `random.choice()`.
- Python calculates the outcome (Victory, Defeat, or Tie) and generates descriptive battle reasons.
- Displays live scoreboard counters (**YOU**, **TIES**, **CPU**) and recent round history (up to 5 rounds).
- **Play Next Round** and **Reset Match** controls.

### 3. Duo Player (`PLAYER 1 VS PLAYER 2`)
- Local 2-Player match flow on the same device.
- Contender setup screen allowing custom names (e.g. *Rahul* vs *Arjun*).
- Pass-and-play turn selection with silent weapon locking to keep choices secret until the clash.
- Python backend calculates the winner with custom name victory banners.
- Dedicated Duo Scoreboard (**Player 1 Wins**, **Draws**, **Player 2 Wins**).

### 4. Score Tab (`ACTUAL CURRENT GAME SCORES`)
- Displays real-time match statistics for both Single Player and Duo Player modes.
- Starts cleanly at `0 - 0 - 0` with zero mock data.
- **RESET SCORE Button**: Prompts with a confirmation dialog (*"Reset current game score?"*).
- On confirmation, resets all scores to `0`, clears round results, and prepares the application for a fresh match with new player names.

### 5. Theme Tab (`DARK & LIGHT MODES`)
- **🌙 Dark Mode**: Premium dark gaming atmosphere with deep navy glassmorphism and neon glows.
- **☀️ Light Mode**: Modern, clean slate/indigo theme with high-contrast text and sleek cards.
- Instantly toggles and persists preference using `localStorage`.

---

## Game Rules

The game follows standard classic Rock-Paper-Scissors rules:
- 🪨 **Rock beats Scissors** (*Rock crushes Scissors*)
- ✂ **Scissors beats Paper** (*Scissors cuts Paper*)
- 📄 **Paper beats Rock** (*Paper covers Rock*)
- 🤝 **Identical choices result in a Tie**

---

## Technologies Used

- **Backend / Core Engine**: Python 3.x, Flask
- **Frontend Presentation**: HTML5, Vanilla CSS3 (Custom Glassmorphic Design System, Google Fonts Bebas Neue, Outfit & Plus Jakarta Sans)
- **Client Interactions**: Vanilla JavaScript (Fetch API for asynchronous requests and DOM state updates)

---

## Python Concepts Demonstrated

1. **Random Number Generation**: `random.choice()` for unbiased computer weapon selection.
2. **Rule Lookups & Conditional Logic**: Dictionary-based rule mappings (`WINNING_RULES`, `OUTCOME_REASONS`) for clean $O(1)$ decision logic without nested ladders.
3. **Multiplayer Winner Calculation**: Dynamic resolution for Player 1 vs Player 2 with custom contender names (`determine_duo_winner()`).
4. **Session State Management**: Using Flask's `session` object to persist user scores, ties, and round histories without requiring an external database.
5. **REST API & JSON Serialization**: Structured JSON API endpoints (`/play`, `/play-duo`, `/duo-setup`, `/get-scores`, `/reset`, `/play-again`).
6. **Defensive Input Validation**: Validating weapon choices against `VALID_CHOICES` and returning friendly HTTP 400 responses on invalid input.
7. **Automated Unit Testing**: Comprehensive test suite in `test_app.py` utilizing Python's `unittest` module.

---

## Project Structure

```text
rock-paper-scissors/
│
├── app.py                 # Core Python Flask application & game engine
├── test_app.py            # Automated unit tests for game logic and routes
├── verify_live_app.py     # Live integration verification script
├── requirements.txt       # Python dependencies (Flask)
├── README.md              # Project documentation & evaluation guide
│
├── templates/
│   └── index.html         # Main template with Hero Showcase, 4 modes & modals
│
└── static/
    ├── style.css          # Glassmorphic dark/light styling & responsive layout
    └── script.js          # Tab navigation, Duo turn flow, fetch API, themes
```

---

## Installation & How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## How to Run Automated Tests

To execute the unit and integration tests:

```bash
python test_app.py
```
