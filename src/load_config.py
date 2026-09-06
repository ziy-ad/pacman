import json
import re
import sys
import random
from pathlib import Path
from dataclasses import dataclass

MIN_LENGTH = 10
MAX_LENGTH = 40

@dataclass
class ConfigData:
    levels: list[dict]
    highscore_filename: str
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: None | int | float | str | bytes
    level_max_time: int

class ParseConfig:
    """Class that contain and parse the config and returning a valid json/dict"""
    def __init__(self):
        """class attributes where the config_file data should be stored"""
        self.path = ParseConfig.get_path()
        self.loaded_json = self.validate_file()
        self.valid_data = ConfigData(**self.validate_data())

    @staticmethod
    def get_path() -> str:
        """function that check if the number of arguments is 2 and return the 2nd parameter"""
        if len(sys.argv) != 2:
            print("Usage: uv run -m src config.json")
            exit(1)
        return sys.argv[1]

    def validate_file(self) -> dict:
        """this function is responsable about filtring comments from the config file and try
        to load the json if its valid raise error if the json file isn't valid"""
        filtred_file = ""
        in_comment = 0
        with open(self.path) as f:
            for line in f:
                n_line = line.strip()
                if n_line.startswith("#"):
                    continue
                elif n_line.startswith("//"):
                    continue
                elif n_line.startswith("/*"):
                    if not n_line.endswith("*/"):
                        in_comment = 1
                    continue
                elif in_comment == 1:
                    if n_line.endswith("*/"):
                        in_comment = 0
                    continue
                else:
                    if in_comment == 1:
                        print("comment still not closed")
                        exit(1)
                    filtred_file += line
            if in_comment == 1:
                print("comment still not closed")
                exit(1)

        # for line in filtred_file.splitlines():
        #     line = re.sub(r"#.*$", "", line)
        #     line = re.sub(r"//.*$", "", line)
        #     line = re.sub(r"/\*.*?\*/", "", line)
        #     last_text += line


        def strip_json_comments(text):
            out = []
            i = 0
            n = len(text)

            in_string = False
            escape = False

            while i < n:
                c = text[i]

                if in_string:
                    out.append(c)
                    if escape:
                        escape = False
                    elif c == "\\":
                        escape = True
                    elif c == '"':
                        in_string = False
                    i += 1
                    continue

                if c == '"':
                    in_string = True
                    out.append(c)
                    i += 1
                    continue

                # //
                if text.startswith("//", i):
                    while i < n and text[i] != "\n":
                        i += 1
                    continue

                # #
                if c == "#":
                    while i < n and text[i] != "\n":
                        i += 1
                    continue

                # /* */
                if text.startswith("/*", i):
                    i += 2
                    while i + 1 < n and not text.startswith("*/", i):
                        i += 1
                    i += 2
                    continue

                out.append(c)
                i += 1

            return "".join(out)


        # filtred_file = re.sub(r"#.*$", "", filtred_file, flags=re.MULTILINE)
        # filtred_file = re.sub(r"//.*$", "", filtred_file, flags=re.MULTILINE)
        # filtred_file = re.sub(r"/\*.*?\*/", "", filtred_file, flags=re.DOTALL)
        # print(filtred_file)
        try:
            return json.loads(filtred_file)
        except Exception as e:
            print(f"in config file: {e}")
            exit(1)

    def validate_data(self) -> dict:
        """Check if the required keys in the config file and their values are valid, if not log a clear message
        and continue with the default value"""
        default_levels: list[dict] = [
            {"width": 10, "height": 10},
            {"width": 25, "height": 25},
            {"width": 29, "height": 25},
            {"width": 29, "height": 29},
            {"width": 33, "height": 29},
            {"width": 33, "height": 33},
            {"width": 37, "height": 33},
            {"width": 37, "height": 37},
            {"width": 41, "height": 37},
            {"width": 41, "height": 41},
        ]

        validated_data = {
            "highscore_filename": "track_score.json",
            "lives": 3,
            "pacgum": 42,
            "points_per_pacgum": 1,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level_max_time": 90,
            "levels": default_levels,
        }

        int_keys = [
            "lives",
            "pacgum",
            "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost",
        ]

        if "highscore_filename" in self.loaded_json.keys():
            file_name = self.loaded_json.get("highscore_filename")
            if isinstance(file_name, str):
                if file_name.strip() == "":
                    print(
                        "Reciving empty file name using 'track_score.json' as default"
                    )
                elif ".." in file_name or Path(file_name).is_absolute():
                    print("It could be risk to use a file another path", end=" ")
                    print("using 'track_score.json' as default")
                else:
                    validated_data["highscore_filename"] = file_name
            else:
                print("file name should be string")
                print("using 'track_score.json' as default")

        for key in int_keys:
            if key in self.loaded_json.keys():
                value = self.loaded_json.get(key)
                if isinstance(value, int) and value > 0:
                    validated_data[key] = value
                else:
                    if not isinstance(value, int):
                        print(f"value of {key} should be integer", end=" ")
                    else:
                        print(f"value of {key} should be positive", end=" ")
                    print(f"using {validated_data[key]} as default")

        if "seed" in self.loaded_json.keys():
            seed = self.loaded_json.get("seed")
            try:
                rg = random.Random()
                rg.seed(seed)
                validated_data["seed"] = seed
            except Exception as e:
                print(e)
                print("using 42 as default !")

        if "level_max_time" in self.loaded_json.keys():
            level_max_time = self.loaded_json.get("level_max_time")
            if isinstance(level_max_time, int) and level_max_time > 90:
                validated_data["level_max_time"] = level_max_time

        if "levels" in self.loaded_json.keys():
            levels = self.loaded_json.get("levels")

            for i, level in enumerate(levels):
                use_default = 0
                width = level.get("width")
                if not width:
                    print("width key not found")
                    if i > 9:
                        default_levels.append(default_levels[i % 10])
                    continue

                    
                height = level.get("height")
                if not height:
                    print("height key not found")
                    if i > 9:
                        default_levels.append(default_levels[i % 10])
                    continue


                if not isinstance(width, int):
                    print("width should be positive")
                    use_default = 1
                else:
                    width = int(width)
                    if width < MIN_LENGTH or width > MAX_LENGTH:
                        print(
                            f"number not in range of {MIN_LENGTH}-{MAX_LENGTH}", end=" "
                        )
                        print("using a default level for width and heigth")
                        use_default = 1

                if not isinstance(height, int):
                    use_default = 1
                    print("height should be positive")
                else:
                    height = int(height)
                    if (height < MIN_LENGTH or height > MAX_LENGTH) and not use_default:
                        print(
                            f"number not in range of {MIN_LENGTH}-{MAX_LENGTH}", end=" "
                        )
                        print("using a default level for width and heigth")
                        use_default = 1

                if use_default == 0:
                    if i <= 9:
                        default_levels[i] = level
                    else:
                        default_levels.append(level)
                else:
                    if i > 9:
                        default_levels.append(default_levels[i % 10])

        return validated_data
    