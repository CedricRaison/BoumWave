"""Commands module for BoumWave CLI"""

from boumwave.commands.generate import generate as generate_command
from boumwave.commands.init import init_command
from boumwave.commands.new_post import new_post_command
from boumwave.commands.scaffold import scaffold_command

__all__ = ["init_command", "scaffold_command", "new_post_command", "generate_command"]
