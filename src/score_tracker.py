"""Highscore storage."""

import json
import re
from typing import Any, List


class score_board:
    """Load, validate and save the highscores."""

    NAME_RE = re.compile(r"^[A-Za-z0-9 ]{1,10}$")

    def __init__(self, path: str) -> None:
        """Set up the board and load the scores."""
        self.scores: List[dict[str, Any]] = []
        self.path = path
        self.load_scores()

    def load_scores(self) -> None:
        """Read the scores from the json file."""
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.scores = [
                        {
                            "name": str(e.get("name", "")),
                            "score": int(e.get("score")),
                        }
                        for e in data
                    ]
                else:
                    self.scores = []
        except FileNotFoundError:
            self.scores = []
        if len(self.scores) > 10:
            self.scores = sorted(self.scores, key=lambda x: x["score"])[:10]
            with open(self.path, "w") as f:
                json.dump(
                    self.scores,
                    f,
                    indent=4
                )

    def save_scores(self) -> None:
        """Write the scores to the json file."""
        with open(self.path, "w") as f:
            json.dump(self.scores, f, indent=4)

    def validate_name(self, name: str) -> bool:
        """Check that the player name is valid."""
        return bool(self.NAME_RE.match(name))

    def add_score(self, player_name: str, score: int) -> None:
        """Add or update a player score and save it."""
        name = player_name.strip()
        if not self.validate_name(name):
            return
        try:
            score = int(score)
        except ValueError:
            return

        if score <= 0:
            return

        existed = None
        for e in self.scores:
            if e["name"] == name:
                existed = e
                break
        if existed:
            if score > existed["score"]:
                existed["score"] = score
        else:
            self.scores.append({"name": name, "score": score})

        self.scores = sorted(
            self.scores, key=lambda e: e["score"], reverse=True
        )[:10]
        self.save_scores()

    def get_all_scores(self) -> List[dict[str, Any]]:
        """Return the scores sorted from best to worst."""
        return sorted(self.scores, key=lambda e: e["score"], reverse=True)
