## Configuration

The game is configured via a JSON file passed as the single command-line argument:

    $> python3 pac-man.py config.json

Comments starting with `#` are supported and stripped before parsing. Any missing,
invalid, or malformed key falls back to a safe default — the game will never crash
because of a bad config file; it logs a message and continues.

### Keys

| Key | Type | Default | Validation rule |
|---|---|---|---|
| `highscore_filename` | string | `"track_score.json"` | Must be a non-empty string. Rejected if it contains `..` or is an absolute path (to prevent writing outside the project directory). Falls back to the default on any of these failures. |
| `lives` | int | `3` | Must be a positive integer (`> 0`). |
| `pacgum` | int | `42` | Must be a positive integer (`> 0`). Total number of pacgums to place across the maze's corridors. |
| `points_per_pacgum` | int | `1` | Must be a positive integer (`> 0`). Points awarded per pacgum eaten. |
| `points_per_super_pacgum` | int | `50` | Must be a positive integer (`> 0`). Points awarded per super-pacgum eaten. |
| `points_per_ghost` | int | `200` | Must be a positive integer (`> 0`). Points awarded per edible ghost eaten. |
| `seed` | int | `42` | Used to seed the random generator for level 1's maze. Any value accepted by Python's `random.Random().seed()` is valid; invalid values fall back to `42`. Only affects the first level — subsequent levels are randomly generated regardless of this value. |
| `level_max_time` | int | `90` | Time limit (in seconds) per level. Must be a positive integer strictly greater than `90` to override the default. |
| `levels` | array of `{width, height}` objects | 10 predefined entries, from `21x21` up to `41x41` (see below) | At least 10 levels are guaranteed. Each `width`/`height` must be an integer within `[MIN_LENGTH, MAX_LENGTH]`; any level entry that fails validation falls back to the corresponding default level instead. |

### Default levels

If `levels` is missing, malformed, or contains invalid entries, the following
defaults are used (maze size increases progressively to raise difficulty):

| Level | Width | Height |
|---|---|---|
| 1  | 21 | 21 |
| 2  | 25 | 25 |
| 3  | 29 | 25 |
| 4  | 29 | 29 |
| 5  | 33 | 29 |
| 6  | 33 | 33 |
| 7  | 37 | 33 |
| 8  | 37 | 37 |
| 9  | 41 | 37 |
| 10 | 41 | 41 |

### Example config file

    {
        # General settings
        "highscore_filename": "track_score.json",
        "lives": 3,

        # Scoring
        "pacgum": 42,
        "points_per_pacgum": 1,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,

        # Maze generation
        "seed": 42,
        "level_max_time": 90,
        "levels": [
            { "width": 21, "height": 21 },
            { "width": 25, "height": 25 }
        ]
    }