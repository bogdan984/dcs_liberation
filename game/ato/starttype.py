from enum import Enum, unique


@unique
class StartType(Enum):
    """The start type for a Flight.

    This is distinct from dcs.mission.StartType because we need a fourth state:
    IN_FLIGHT.
    """

    COLD = "Cold"
    WARM = "Warm"
    RUNWAY = "Runway"
    IN_FLIGHT = "In Flight"

    @property
    def display_name(self) -> str:
        return {
            StartType.COLD: "Холодный",
            StartType.WARM: "Горячий",
            StartType.RUNWAY: "С ВПП",
            StartType.IN_FLIGHT: "В воздухе",
        }[self]
