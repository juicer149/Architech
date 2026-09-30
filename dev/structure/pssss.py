

class Example: # head of the class
    """
    This is an example class to demonstrate docstring formatting.

    Attributes:
        name (str): The name of the example.
        value (int): The value associated with the example.
    """

    def __init__(self, name: str, value: int):
        """
        Initializes the Example class with a name and value.

        Args:
            name (str): The name of the example.
            value (int): The value associated with the example.
        """
        self.name = name
        self.value = value

    def display(self) -> str:
        """
        Returns a string representation of the example.

        Returns:
            str: A formatted string containing the name and value.
        """
        return f"Example Name: {self.name}, Value: {self.value}"

#detta skulle via fold ge detta i nvim:

class Example:  # foldar eller unfoldar hela klassen, förutom egna docstringen
    """
    This is an example class to demonstrate docstring formatting. # trycker man med cursor på denna raden så unfoldas hela docstringen
    """

    def __init__(self, name: str, value: int):  # trycker man på unfold på denna raden unfoldas all kod i __init__
        """
        Initializes the Example class with a name and value.  # unfoldar hela docstringen
        """

    def display(self) -> str:
        """
        Returns a string representation of the example.
        """
