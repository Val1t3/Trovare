"""Command registry and descriptions."""

from collections.abc import Awaitable, Callable

from commands.params import CommandParameter

COMMANDS: dict[str, Callable[[CommandParameter], Awaitable[str]]] = {}

DESCRIPTIONS = {
    "new": "Réinitialise l'historique de conversation partagé",
    "help": "Affiche cette liste de commandes",
}
