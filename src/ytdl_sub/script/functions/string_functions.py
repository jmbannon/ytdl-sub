from ytdl_sub.script.types import String


class StringFunctions:
    @staticmethod
    def lower(string: String) -> String:
        """
        Returns
        -------
        Lower-cased string
        """
        return String(string.value.lower())

    @staticmethod
    def upper(string: String) -> String:
        """
        Returns
        -------
        Upper-cased string
        """
        return String(string.value.upper())

    @staticmethod
    def capitalize(string: String) -> String:
        """
        Returns
        -------
        Capitalized string
        """
        return String(string.value.capitalize())

    @staticmethod
    def concat(l_string: String, r_string: String) -> String:
        return String(f"{l_string}{r_string}")
