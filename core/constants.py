import zoneinfo
import re
from django.utils import timezone


# Color constants; used as the site's primary color.
BLUE = "blue"
INDIGO = "indigo"
PURPLE = "purple"
PINK = "pink"
RED = "red"
ORANGE = "orange"
YELLOW = "yellow"
GREEN = "green"
TEAL = "teal"
CYAN = "cyan"
COLORS = {
    BLUE: "Blue", INDIGO: "Indigo", PURPLE: "Purple",
    PINK: "Pink", RED: "Red", ORANGE: "Orange",
    YELLOW: "Yellow", GREEN: "Green", TEAL: "Teal", CYAN: "Cyan"
}

ENGLISH = "en"
GERMAN = "de"
LANGUAGES = {
    ENGLISH: "English", GERMAN: "German"
}


# Years; Used for the User's Birthday option
YEARS = list(reversed(range(1960, timezone.now().year-13)))


# Timezones; Used for the User's tz option
def get_timezones() -> dict:
    def gmt_timezones(tz: str):
        return (tz.__contains__("Etc/GMT+") or (tz.__contains__("Etc/GMT-") and not tz.__contains__("Etc/GMT-0")))

    tz_list = sorted(filter(
        gmt_timezones,
        zoneinfo.available_timezones()),
        key=lambda num: int(num.replace("Etc/GMT", "") + "0"))
    output: dict = {}
    tz: str

    for tz in tz_list:
        try:
            num: int = int(tz.replace("Etc/GMT", ""))
            output[tz] = "UTC" + f"{tz.replace("Etc/GMT", "")}:00"
        except (Exception):
            pass
    return output


TIMEZONES = []
TIMEZONES = get_timezones()
