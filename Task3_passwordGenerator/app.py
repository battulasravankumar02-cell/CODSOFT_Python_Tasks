"""
Flask Web Application for Password Generator
Backend logic using Python's secrets and string modules.
"""

from flask import Flask, render_template, request, jsonify
import string
import secrets
from typing import Tuple, List

app = Flask(__name__)

# Safe symbol set
SAFE_SYMBOLS = "!@#$%^&*()-_=+[]{}?"


def calculate_strength(password: str, has_upper: bool, has_lower: bool, has_digits: bool, has_symbols: bool) -> Tuple[str, float, str]:
    """
    Calculate password strength rating, progress fraction (0.0 to 1.0), and color code.
    Returns: (label, score_ratio, hex_color)
    """
    if not password:
        return "Not generated", 0.0, "#64748B"

    length = len(password)
    categories_count = sum([has_upper, has_lower, has_digits, has_symbols])

    if categories_count <= 1 or length < 8:
        return "Weak", 0.25, "#EF4444"  # Red
    elif length < 12:
        return "Medium", 0.50, "#F59E0B"  # Orange/Amber
    elif length < 16 or categories_count < 3:
        return "Strong", 0.75, "#10B981"  # Emerald Green
    else:
        return "Very Strong", 1.00, "#06B6D4"  # Vibrant Cyan


def generate_password(
    length: int = 16,
    include_upper: bool = True,
    include_lower: bool = True,
    include_digits: bool = True,
    include_symbols: bool = False
) -> str:
    """
    Generate a cryptographically secure random password using Python's secrets and string modules.
    Guarantees at least one character from each selected category.
    """
    categories: List[str] = []
    guaranteed_chars: List[str] = []

    if include_upper:
        categories.append(string.ascii_uppercase)
        guaranteed_chars.append(secrets.choice(string.ascii_uppercase))
    if include_lower:
        categories.append(string.ascii_lowercase)
        guaranteed_chars.append(secrets.choice(string.ascii_lowercase))
    if include_digits:
        categories.append(string.digits)
        guaranteed_chars.append(secrets.choice(string.digits))
    if include_symbols:
        categories.append(SAFE_SYMBOLS)
        guaranteed_chars.append(secrets.choice(SAFE_SYMBOLS))

    if not categories:
        raise ValueError("Please select at least one character type.")

    # Gracefully adjust if requested length is shorter than required categories
    if length < len(guaranteed_chars):
        length = len(guaranteed_chars)

    # Combined pool for remaining characters
    combined_pool = "".join(categories)
    remaining_count = length - len(guaranteed_chars)
    remaining_chars = [secrets.choice(combined_pool) for _ in range(remaining_count)]

    all_chars = guaranteed_chars + remaining_chars

    # Secure shuffle using Fisher-Yates algorithm powered by secrets.randbelow
    for i in range(len(all_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        all_chars[i], all_chars[j] = all_chars[j], all_chars[i]

    return "".join(all_chars)


@app.route("/")
def index():
    """Render the main Password Generator web interface."""
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    API Endpoint: Receives user settings and generates a secure password in Python.
    """
    data = request.get_json(silent=True) or {}

    try:
        length = int(data.get("length", 16))
        # Clamp length between 4 and 32
        length = max(4, min(32, length))

        include_upper = bool(data.get("uppercase", True))
        include_lower = bool(data.get("lowercase", True))
        include_digits = bool(data.get("numbers", True))
        include_symbols = bool(data.get("symbols", False))

        if not (include_upper or include_lower or include_digits or include_symbols):
            return jsonify({
                "success": False,
                "error": "Please select at least one character type."
            }), 400

        # Generate in Python using secrets
        password = generate_password(
            length=length,
            include_upper=include_upper,
            include_lower=include_lower,
            include_digits=include_digits,
            include_symbols=include_symbols
        )

        label, ratio, color = calculate_strength(
            password,
            include_upper,
            include_lower,
            include_digits,
            include_symbols
        )

        return jsonify({
            "success": True,
            "password": password,
            "strength": {
                "label": label,
                "score": ratio,
                "color": color
            }
        })

    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while generating password."
        }), 500


if __name__ == "__main__":
    # Run development server on port 5000
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
