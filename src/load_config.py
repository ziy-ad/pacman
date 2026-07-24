import json
import re
from typing import Any
import sys
import random
from pathlib import Path
from enum import Enum



class ParseConfig:
    def __init__(self):
        self.path = ParseConfig.get_path()
        self.loaded_json = self.validate_file()
        self.valid_data = self.validate_data()

    @staticmethod
    def get_path() -> str:
        if len(sys.argv) != 2:
            print("Usage: uv run -m src config.json")
            exit(1)
        return sys.argv[1]


    def validate_file(self) -> dict:
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

        try:
            return json.loads(filtred_file)
        except Exception as e:
            print(f"in config file: {e}")
            exit(1)


    def validate_data(self) -> dict:

        DEFAULT_LEVELS: list[LevelConfig] = [
            {"width": 21, "height": 21},
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

        validated_data = {"highscore_filename": "track_score.json",
                          "lives": 3, "pacgum": 42, "points_per_pacgum" : 1,
                          "points_per_super_pacgum": 50, "points_per_ghost": 200,
                          "seed": 42, "level_max_time" : 90}

        int_keys = ["lives", "pacagum", "points_per_pacgum", "points_per_super_pacgum", "points_per_ghost"]


        if "highscore_filename" in self.loaded_json.keys():
            file_name = self.loaded_json.get('highscore_filename')
            if isinstance(file_name, str):
                if file_name.strip() == "":
                    print("Reciving empty file name using 'highscore.json' as default")
                elif ".." in file_name or Path(file_name).is_absolute():
                    print("It could be risk to use a file another path", end=" ")
                    print("using 'highscore.json' as default")
            else:
                print("file name should be string")
                print("using 'highscore.json' as default")


        for key in int_keys:
            if key in self.loaded_json.keys():
                value = self.loaded_json.get(key)
                if isinstance(value, int) and value > 0:
                    validated_data[key] = value

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
                width = level['width']
                height = level['height']


                if isinstance(width, int):
                    print("width should be positive")
                print(i, level)

        return validated_data
