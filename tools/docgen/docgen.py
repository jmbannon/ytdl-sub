import os
from abc import abstractmethod
from pathlib import Path
from typing import final

REGENERATE_DOCS: bool = bool(os.environ.get("REGENERATE_DOCS", 0))


class DocGen:
    """
    Home-made auto doc generation
    """

    LOCATION: Path

    # human-readable location of where to edit the underlying docstrings
    DOCSTRING_LOCATION: str

    @classmethod
    def _generate_warning(cls) -> str:
        return (
            "..\n"
            "  WARNING: This RST file is generated from docstrings in:\n"
            f"    {cls.DOCSTRING_LOCATION}\n"
            "  In order to make a change to this file, edit the respective docstring\n"
            "  and run `make docs`. This will automatically sync the Python RST-based\n"
            "  docstrings into this file.\n"
        )

    @classmethod
    @abstractmethod
    def generate(cls) -> str:
        """
        Generate the docs as a single string
        """

    @classmethod
    def generate_and_maybe_write_to_file(cls) -> str:
        """
        Maybe writes the docs to their file if the global is set to True, and returns
        the generated docs
        """
        contents = cls._generate_warning() + cls.generate()
        if REGENERATE_DOCS:
            with open(cls.LOCATION, "w", encoding="utf-8") as out:
                out.write(contents)

        return contents
