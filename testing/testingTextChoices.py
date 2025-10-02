from django.db import models

class ColorChoices(models.TextChoices):
    """Color Choices"""
    BLUE = "blue", "Blue"   # name = 'value', 'label'
    INDIGO = "indigo", "Indigo"
    PURPLE = "purple", "Purple"
    PINK = "pink", "Pink"
    RED = "red", "Red"
    ORANGE = "orange", "Orange"
    YELLOW = "yellow", "Yellow"
    GREEN = "green", "Green"
    TEAL = "teal", "Teal"
    CYAN = "cyan", "Cyan"

color = models.CharField(
    max_length=6,
    choices=ColorChoices.choices,
    default=ColorChoices.BLUE)

print(color.choices)
#print(color.choices)
print(color)
print(ColorChoices)
#print(repr(color))

#  {BLUE: 'Blue', INDIGO: 'Indigo'...}

print(dict(ColorChoices.choices))  # outputs {'value': 'label', ...}
print(list(ColorChoices.choices))  # outputs {('value', 'label'), ...}
print(dict(zip(ColorChoices.names, ColorChoices.labels)))