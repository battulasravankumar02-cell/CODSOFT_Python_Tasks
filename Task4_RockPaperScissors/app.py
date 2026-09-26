"""
Rock, Paper, Scissors Web Application
CODSOFT Python Programming Internship - Task 4

This application implements a complete Rock-Paper-Scissors game
with Single Player (Player vs Computer) and Duo Player (Player 1 vs Player 2)
modes, real-time score tracking, theme customization, and responsive UI.
All core game logic, random selection, winner calculation, and score
tracking are handled entirely in Python.
"""

import os
import random
from flask import Flask, render_template, request, jsonify, session

# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management
app.secret_key = os.environ.get("SECRET_KEY", "rock-paper-scissors-secret-key-2026")

# Valid choices for the game
VALID_CHOICES = ["rock", "paper", "scissors"]

# Visual metadata for choices
CHOICE_META = {
    "rock": {"label": "Rock", "icon": "🪨"},
    "paper": {"label": "Paper", "icon": "📄"},
    "scissors": {"label": "Scissors", "icon": "✂"}
}

# Win condition rules: key beats value
WINNING_RULES = {
    "rock": "scissors",      # Rock beats Scissors
    "scissors": "paper",     # Scissors beats Paper
    "paper": "rock"          # Paper beats Rock
}

# Explanatory messages for victory/loss combinations
OUTCOME_REASONS = {
    ("rock", "scissors"): "Rock crushes Scissors!",
    ("scissors", "paper"): "Scissors cuts Paper!",
    ("paper", "rock"): "Paper covers Rock!"
}


def get_computer_choice() -> str:
    """
    Randomly select one choice for the computer from the valid choices.
    Uses Python's built-in random module.
    """
    return random.choice(VALID_CHOICES)


def determine_winner(user_choice: str, computer_choice: str):
    """
    Determine the outcome of a Single Player round based on standard rules.
    
    Parameters:
        user_choice (str): The choice made by the player ('rock', 'paper', or 'scissors')
        computer_choice (str): The choice randomly picked by the computer
        
    Returns:
        tuple: (result, outcome_title, outcome_reason)
               result is one of: 'win', 'lose', 'tie'
    """
    # Check for a tie
    if user_choice == computer_choice:
        user_label = CHOICE_META[user_choice]["label"]
        return (
            "tie",
            "IT'S A TIE!",
            f"Both selected {user_label}. Great minds think alike!"
        )
    
    # Check if the user's choice beats the computer's choice
    if WINNING_RULES.get(user_choice) == computer_choice:
        reason = OUTCOME_REASONS.get(
            (user_choice, computer_choice),
            f"{CHOICE_META[user_choice]['label']} beats {CHOICE_META[computer_choice]['label']}!"
        )
        return ("win", "YOU WIN!", reason)
    
    # Otherwise, the computer wins
    reason = OUTCOME_REASONS.get(
        (computer_choice, user_choice),
        f"{CHOICE_META[computer_choice]['label']} beats {CHOICE_META[user_choice]['label']}!"
    )
    return ("lose", "COMPUTER WINS!", reason)


def determine_duo_winner(p1_choice: str, p2_choice: str, p1_name: str = "Player 1", p2_name: str = "Player 2"):
    """
    Determine the outcome of a Duo Player round based on standard rules.
    
    Parameters:
        p1_choice (str): Choice made by Player 1
        p2_choice (str): Choice made by Player 2
        p1_name (str): Display name for Player 1
        p2_name (str): Display name for Player 2
        
    Returns:
        tuple: (result, outcome_title, outcome_reason)
               result is one of: 'p1_win', 'p2_win', 'tie'
    """
    clean_p1 = p1_name.strip() if p1_name and p1_name.strip() else "Player 1"
    clean_p2 = p2_name.strip() if p2_name and p2_name.strip() else "Player 2"
    
    if p1_choice == p2_choice:
        choice_label = CHOICE_META[p1_choice]["label"]
        return (
            "tie",
            "IT'S A TIE!",
            f"Both {clean_p1} and {clean_p2} selected {choice_label}!"
        )
    
    if WINNING_RULES.get(p1_choice) == p2_choice:
        reason_template = OUTCOME_REASONS.get((p1_choice, p2_choice), "")
        reason = f"{clean_p1}'s {CHOICE_META[p1_choice]['label']} beats {clean_p2}'s {CHOICE_META[p2_choice]['label']}! {reason_template}".strip()
        return ("p1_win", f"{clean_p1.upper()} WINS!", reason)
    
    reason_template = OUTCOME_REASONS.get((p2_choice, p1_choice), "")
    reason = f"{clean_p2}'s {CHOICE_META[p2_choice]['label']} beats {clean_p1}'s {CHOICE_META[p1_choice]['label']}! {reason_template}".strip()
    return ("p2_win", f"{clean_p2.upper()} WINS!", reason)


def init_session():
    """
    Initialize all game states in the user's session if not already present.
    Ensures a clean initial state with zero mock data.
    """
    # Single Player Session State
    if "user_score" not in session:
        session["user_score"] = 0
    if "computer_score" not in session:
        session["computer_score"] = 0
    if "tie_count" not in session:
        session["tie_count"] = 0
    if "round_history" not in session:
        session["round_history"] = []
    if "last_round" not in session:
        session["last_round"] = None

    # Duo Player Session State
    if "duo_p1_name" not in session:
        session["duo_p1_name"] = ""
    if "duo_p2_name" not in session:
        session["duo_p2_name"] = ""
    if "duo_p1_score" not in session:
        session["duo_p1_score"] = 0
    if "duo_p2_score" not in session:
        session["duo_p2_score"] = 0
    if "duo_tie_count" not in session:
        session["duo_tie_count"] = 0
    if "duo_round_history" not in session:
        session["duo_round_history"] = []
    if "duo_last_round" not in session:
        session["duo_last_round"] = None
    if "duo_active" not in session:
        session["duo_active"] = False


def reset_game():
    """
    Reset all scores, history, and active round state across both single and duo modes.
    """
    session["user_score"] = 0
    session["computer_score"] = 0
    session["tie_count"] = 0
    session["round_history"] = []
    session["last_round"] = None

    session["duo_p1_name"] = ""
    session["duo_p2_name"] = ""
    session["duo_p1_score"] = 0
    session["duo_p2_score"] = 0
    session["duo_tie_count"] = 0
    session["duo_round_history"] = []
    session["duo_last_round"] = None
    session["duo_active"] = False
    session.modified = True


@app.route("/")
def index():
    """
    Serve the main game interface with navigation tabs.
    """
    init_session()
    return render_template(
        "index.html",
        # Single Player state
        user_score=session.get("user_score", 0),
        computer_score=session.get("computer_score", 0),
        tie_count=session.get("tie_count", 0),
        round_history=session.get("round_history", []),
        last_round=session.get("last_round", None),
        # Duo Player state
        duo_p1_name=session.get("duo_p1_name", ""),
        duo_p2_name=session.get("duo_p2_name", ""),
        duo_p1_score=session.get("duo_p1_score", 0),
        duo_p2_score=session.get("duo_p2_score", 0),
        duo_tie_count=session.get("duo_tie_count", 0),
        duo_round_history=session.get("duo_round_history", []),
        duo_last_round=session.get("duo_last_round", None),
        duo_active=session.get("duo_active", False)
    )


@app.route("/play", methods=["POST"])
def play():
    """
    Process a Single Player round (User vs Computer).
    """
    init_session()
    data = request.get_json(silent=True) or request.form
    raw_choice = data.get("choice", "")
    user_choice = str(raw_choice).strip().lower()

    if user_choice not in VALID_CHOICES:
        return jsonify({
            "success": False,
            "error": "Please choose Rock, Paper, or Scissors."
        }), 400

    # 1. Computer makes a random selection
    computer_choice = get_computer_choice()

    # 2. Python determines the winner
    result, result_title, result_reason = determine_winner(user_choice, computer_choice)

    # 3. Update scores
    if result == "win":
        session["user_score"] = session.get("user_score", 0) + 1
    elif result == "lose":
        session["computer_score"] = session.get("computer_score", 0) + 1
    elif result == "tie":
        session["tie_count"] = session.get("tie_count", 0) + 1

    # 4. Construct round details
    round_data = {
        "user_choice": user_choice,
        "user_label": CHOICE_META[user_choice]["label"],
        "user_icon": CHOICE_META[user_choice]["icon"],
        "computer_choice": computer_choice,
        "computer_label": CHOICE_META[computer_choice]["label"],
        "computer_icon": CHOICE_META[computer_choice]["icon"],
        "result": result,
        "result_title": result_title,
        "result_reason": result_reason
    }

    # 5. Maintain recent history (latest 5)
    history = session.get("round_history", [])
    history.insert(0, round_data)
    if len(history) > 5:
        history = history[:5]
    session["round_history"] = history
    session["last_round"] = round_data
    session.modified = True

    return jsonify({
        "success": True,
        "round": round_data,
        "scores": {
            "user": session["user_score"],
            "computer": session["computer_score"],
            "ties": session["tie_count"]
        },
        "history": session["round_history"]
    })


@app.route("/duo-setup", methods=["POST"])
def duo_setup():
    """
    Start or restart a Duo Player match by setting player names and resetting duo scores.
    """
    init_session()
    data = request.get_json(silent=True) or request.form
    p1_name = str(data.get("p1_name", "")).strip() or "Player 1"
    p2_name = str(data.get("p2_name", "")).strip() or "Player 2"

    session["duo_p1_name"] = p1_name
    session["duo_p2_name"] = p2_name
    session["duo_p1_score"] = 0
    session["duo_p2_score"] = 0
    session["duo_tie_count"] = 0
    session["duo_round_history"] = []
    session["duo_last_round"] = None
    session["duo_active"] = True
    session.modified = True

    return jsonify({
        "success": True,
        "p1_name": p1_name,
        "p2_name": p2_name,
        "scores": {
            "p1": 0,
            "p2": 0,
            "ties": 0
        },
        "history": []
    })


@app.route("/play-duo", methods=["POST"])
def play_duo():
    """
    Process a Duo Player round (Player 1 vs Player 2).
    """
    init_session()
    data = request.get_json(silent=True) or request.form
    p1_choice = str(data.get("p1_choice", "")).strip().lower()
    p2_choice = str(data.get("p2_choice", "")).strip().lower()
    p1_name = session.get("duo_p1_name") or str(data.get("p1_name", "")).strip() or "Player 1"
    p2_name = session.get("duo_p2_name") or str(data.get("p2_name", "")).strip() or "Player 2"

    if p1_choice not in VALID_CHOICES or p2_choice not in VALID_CHOICES:
        return jsonify({
            "success": False,
            "error": "Both players must choose Rock, Paper, or Scissors."
        }), 400

    # Python calculates Duo winner
    result, result_title, result_reason = determine_duo_winner(p1_choice, p2_choice, p1_name, p2_name)

    # Update Duo scores
    if result == "p1_win":
        session["duo_p1_score"] = session.get("duo_p1_score", 0) + 1
    elif result == "p2_win":
        session["duo_p2_score"] = session.get("duo_p2_score", 0) + 1
    elif result == "tie":
        session["duo_tie_count"] = session.get("duo_tie_count", 0) + 1

    round_data = {
        "p1_name": p1_name,
        "p1_choice": p1_choice,
        "p1_label": CHOICE_META[p1_choice]["label"],
        "p1_icon": CHOICE_META[p1_choice]["icon"],
        "p2_name": p2_name,
        "p2_choice": p2_choice,
        "p2_label": CHOICE_META[p2_choice]["label"],
        "p2_icon": CHOICE_META[p2_choice]["icon"],
        "result": result,
        "result_title": result_title,
        "result_reason": result_reason
    }

    history = session.get("duo_round_history", [])
    history.insert(0, round_data)
    if len(history) > 5:
        history = history[:5]
    session["duo_round_history"] = history
    session["duo_last_round"] = round_data
    session.modified = True

    return jsonify({
        "success": True,
        "round": round_data,
        "scores": {
            "p1": session["duo_p1_score"],
            "p2": session["duo_p2_score"],
            "ties": session["duo_tie_count"]
        },
        "history": session["duo_round_history"]
    })


@app.route("/play-again", methods=["POST"])
def play_again():
    """
    Clear the active round display for Single Player.
    """
    init_session()
    session["last_round"] = None
    session.modified = True
    return jsonify({
        "success": True,
        "scores": {
            "user": session.get("user_score", 0),
            "computer": session.get("computer_score", 0),
            "ties": session.get("tie_count", 0)
        },
        "history": session.get("round_history", [])
    })


@app.route("/duo-play-again", methods=["POST"])
def duo_play_again():
    """
    Clear the active round display for Duo Player.
    """
    init_session()
    session["duo_last_round"] = None
    session.modified = True
    return jsonify({
        "success": True,
        "scores": {
            "p1": session.get("duo_p1_score", 0),
            "p2": session.get("duo_p2_score", 0),
            "ties": session.get("duo_tie_count", 0)
        },
        "history": session.get("duo_round_history", [])
    })


@app.route("/get-scores", methods=["GET"])
def get_scores():
    """
    Retrieve current actual scores for both Single Player and Duo Player modes.
    """
    init_session()
    return jsonify({
        "success": True,
        "single": {
            "user": session.get("user_score", 0),
            "computer": session.get("computer_score", 0),
            "ties": session.get("tie_count", 0)
        },
        "duo": {
            "p1_name": session.get("duo_p1_name", "") or "Player 1",
            "p2_name": session.get("duo_p2_name", "") or "Player 2",
            "p1_score": session.get("duo_p1_score", 0),
            "p2_score": session.get("duo_p2_score", 0),
            "ties": session.get("duo_tie_count", 0),
            "active": session.get("duo_active", False)
        }
    })


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset all scores, history, and game states cleanly across the board.
    Allows entering new player names for subsequent duo matches.
    """
    reset_game()
    return jsonify({
        "success": True,
        "message": "All scores and game data reset successfully.",
        "single": {
            "user": 0,
            "computer": 0,
            "ties": 0
        },
        "duo": {
            "p1_name": "",
            "p2_name": "",
            "p1_score": 0,
            "p2_score": 0,
            "ties": 0,
            "active": False
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
