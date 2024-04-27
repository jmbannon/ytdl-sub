import os
from abc import abstractmethod
from pathlib import Path

REGENERATE_DOCS: bool = bool(os.environ.get("REGENERATE_DOCS", 1))


class DocGen:
    """
    Home-made auto doc generation
    """

    LOCATION: Path

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
        contents = cls.generate()
        if REGENERATE_DOCS:
            with open(cls.LOCATION, "w", encoding="utf-8") as out:
                out.write(contents)

        return contents
