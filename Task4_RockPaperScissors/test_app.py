"""
Unit and Integration Tests for Rock-Paper-Scissors Flask Application
Covers Single Player, Duo 2-Player, Scores API, and Reset Flow.
"""
import unittest
import json
from app import app, determine_winner, determine_duo_winner, get_computer_choice, VALID_CHOICES


class RockPaperScissorsTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key-123"
        self.client = app.test_client()

    def test_computer_choice_validity(self):
        """Test that get_computer_choice returns a valid choice."""
        for _ in range(30):
            choice = get_computer_choice()
            self.assertIn(choice, VALID_CHOICES)

    def test_single_winner_logic(self):
        """Test single player win, lose, and tie conditions."""
        # Rock beats Scissors
        res, title, reason = determine_winner("rock", "scissors")
        self.assertEqual(res, "win")

        # Scissors beats Paper
        res, title, reason = determine_winner("scissors", "paper")
        self.assertEqual(res, "win")

        # Paper beats Rock
        res, title, reason = determine_winner("paper", "rock")
        self.assertEqual(res, "win")

        # Ties
        for choice in VALID_CHOICES:
            res, title, reason = determine_winner(choice, choice)
            self.assertEqual(res, "tie")

    def test_duo_winner_logic(self):
        """Test Duo player win, lose, and tie conditions with custom names."""
        # Player 1 (Rahul) beats Player 2 (Arjun)
        res, title, reason = determine_duo_winner("rock", "scissors", "Rahul", "Arjun")
        self.assertEqual(res, "p1_win")
        self.assertEqual(title, "RAHUL WINS!")
        self.assertIn("Rahul's Rock beats Arjun's Scissors", reason)

        # Player 2 (Arjun) beats Player 1 (Rahul)
        res, title, reason = determine_duo_winner("paper", "scissors", "Rahul", "Arjun")
        self.assertEqual(res, "p2_win")
        self.assertEqual(title, "ARJUN WINS!")
        self.assertIn("Arjun's Scissors beats Rahul's Paper", reason)

        # Tie
        res, title, reason = determine_duo_winner("paper", "paper", "Rahul", "Arjun")
        self.assertEqual(res, "tie")
        self.assertEqual(title, "IT'S A TIE!")

    def test_home_page_initial_state(self):
        """Home page should render with status 200 and clean state."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn("SINGLE PLAYER", content)
        self.assertIn("DUO PLAYER", content)
        self.assertIn("SCORE", content)
        self.assertIn("THEME", content)
        self.assertIn("Make your move!", content)

    def test_single_play_endpoint(self):
        """Test Single player POST /play."""
        response = self.client.post(
            "/play",
            data=json.dumps({"choice": "rock"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["round"]["user_choice"], "rock")
        self.assertIn(data["round"]["computer_choice"], VALID_CHOICES)

    def test_duo_setup_and_play_endpoint(self):
        """Test Duo player setup and match flow."""
        # 1. Setup
        setup_res = self.client.post(
            "/duo-setup",
            data=json.dumps({"p1_name": "Rahul", "p2_name": "Arjun"}),
            content_type="application/json"
        )
        self.assertEqual(setup_res.status_code, 200)
        setup_data = setup_res.get_json()
        self.assertEqual(setup_data["p1_name"], "Rahul")
        self.assertEqual(setup_data["p2_name"], "Arjun")

        # 2. Play Duo Round: Rahul chooses Rock, Arjun chooses Scissors
        play_res = self.client.post(
            "/play-duo",
            data=json.dumps({
                "p1_name": "Rahul",
                "p2_name": "Arjun",
                "p1_choice": "rock",
                "p2_choice": "scissors"
            }),
            content_type="application/json"
        )
        self.assertEqual(play_res.status_code, 200)
        play_data = play_res.get_json()
        self.assertTrue(play_data["success"])
        self.assertEqual(play_data["round"]["result"], "p1_win")
        self.assertEqual(play_data["scores"]["p1"], 1)
        self.assertEqual(play_data["scores"]["p2"], 0)

    def test_get_scores_endpoint(self):
        """Test GET /get-scores."""
        response = self.client.get("/get-scores")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("single", data)
        self.assertIn("duo", data)

    def test_reset_endpoint(self):
        """Test POST /reset clears all single & duo scores."""
        # Play single round
        self.client.post("/play", json={"choice": "rock"})
        # Play duo round
        self.client.post("/duo-setup", json={"p1_name": "Rahul", "p2_name": "Arjun"})
        self.client.post("/play-duo", json={"p1_choice": "rock", "p2_choice": "scissors"})

        # Call Reset
        reset_res = self.client.post("/reset")
        self.assertEqual(reset_res.status_code, 200)
        reset_data = reset_res.get_json()
        self.assertTrue(reset_data["success"])
        self.assertEqual(reset_data["single"]["user"], 0)
        self.assertEqual(reset_data["single"]["computer"], 0)
        self.assertEqual(reset_data["single"]["ties"], 0)
        self.assertEqual(reset_data["duo"]["p1_score"], 0)
        self.assertEqual(reset_data["duo"]["p2_score"], 0)
        self.assertEqual(reset_data["duo"]["ties"], 0)
        self.assertFalse(reset_data["duo"]["active"])


if __name__ == "__main__":
    unittest.main()
