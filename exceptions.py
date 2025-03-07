class Impossible(Exception):
    """Exception raised when an action is impossible to be performedd.

    The reason is given as the exception message.
    """


class QuitWithoutSaving(SystemExit):
    """Can be raised to exit the game without automatically saving."""


class ReturnToMainGameHandler(Exception):
    """Signal to return control to the main game handler."""
    pass

