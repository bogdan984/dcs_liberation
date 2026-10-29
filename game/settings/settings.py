import logging
from collections.abc import Iterator
from dataclasses import Field, dataclass, fields
from datetime import timedelta
from enum import Enum, unique
from pathlib import Path
from typing import Any, Optional, get_type_hints

import yaml
from dcs.forcedoptions import ForcedOptions

from .booleanoption import boolean_option
from .boundedfloatoption import bounded_float_option
from .boundedintoption import bounded_int_option
from .choicesoption import choices_option
from .minutesoption import minutes_option
from .optiondescription import OptionDescription, SETTING_DESCRIPTION_KEY
from .skilloption import skill_option
from ..ato.starttype import StartType
from ..persistence.paths import liberation_user_dir


@unique
class AutoAtoBehavior(Enum):
    Disabled = "Disabled"
    Never = "Never assign player pilots"
    Default = "No preference"
    Prefer = "Prefer player pilots"


@unique
class FastForwardStopCondition(Enum):
    DISABLED = "Fast forward disabled"
    FIRST_CONTACT = "First contact"
    PLAYER_TAKEOFF = "Player takeoff time"
    PLAYER_TAXI = "Player taxi time"
    PLAYER_STARTUP = "Player startup time"
    PLAYER_AT_IP = "Player at IP"
    MANUAL = "Manual fast forward control"


@unique
class CombatResolutionMethod(Enum):
    PAUSE = "Pause simulation"
    RESOLVE = "Resolve combat"
    SKIP = "Skip combat"


DIFFICULTY_PAGE = "Сложность"

AI_DIFFICULTY_SECTION = "Сложность ИИ"
MISSION_DIFFICULTY_SECTION = "Сложность миссий"
MISSION_RESTRICTIONS_SECTION = "Ограничения миссий"

CAMPAIGN_MANAGEMENT_PAGE = "Управление кампанией"

GENERAL_SECTION = "Общие"
PILOTS_AND_SQUADRONS_SECTION = "Пилоты и эскадрильи"
HQ_AUTOMATION_SECTION = "Автоматизация штаба"

MISSION_GENERATOR_PAGE = "Генератор миссий"

COMMANDERS_SECTION = "Командиры на поле боя"

GAMEPLAY_SECTION = "Игровой процесс"

# TODO: Make sections a type and add headers.
# This section had the header: "Disabling settings below may improve performance, but
# will impact the overall quality of the experience."
PERFORMANCE_SECTION = "Производительность"


@dataclass
class Settings:
    version: Optional[str] = None

    # Difficulty settings
    # AI Difficulty
    player_skill: str = skill_option(
        "Уровень ИИ коалиции игрока",
        page=DIFFICULTY_PAGE,
        section=AI_DIFFICULTY_SECTION,
        default="Good",
    )
    enemy_skill: str = skill_option(
        "Уровень ИИ коалиции противника",
        page=DIFFICULTY_PAGE,
        section=AI_DIFFICULTY_SECTION,
        default="Average",
    )
    enemy_vehicle_skill: str = skill_option(
        "Уровень вражеской ПВО и техники",
        page=DIFFICULTY_PAGE,
        section=AI_DIFFICULTY_SECTION,
        default="Average",
    )
    player_income_multiplier: float = bounded_float_option(
        "Множитель дохода игрока",
        page=DIFFICULTY_PAGE,
        section=AI_DIFFICULTY_SECTION,
        min=0,
        max=5,
        divisor=10,
        default=1.0,
    )
    enemy_income_multiplier: float = bounded_float_option(
        "Множитель дохода противника",
        page=DIFFICULTY_PAGE,
        section=AI_DIFFICULTY_SECTION,
        min=0,
        max=5,
        divisor=10,
        default=1.0,
    )
    invulnerable_player_pilots: bool = boolean_option(
        "Пилоты игроков не могут погибнуть",
        page=DIFFICULTY_PAGE,
        section=AI_DIFFICULTY_SECTION,
        detail=(
            "Самолёты уязвимы, но пилот игрока вернётся в эскадрилью " "в конце миссии"
        ),
        default=True,
    )
    # Mission Difficulty
    manpads: bool = boolean_option(
        "ПЗРК на линии фронта",
        page=DIFFICULTY_PAGE,
        section=MISSION_DIFFICULTY_SECTION,
        default=True,
    )
    night_disabled: bool = boolean_option(
        "Без ночных миссий",
        page=DIFFICULTY_PAGE,
        section=MISSION_DIFFICULTY_SECTION,
        default=False,
    )
    # Mission Restrictions
    labels: str = choices_option(
        "Метки в игре",
        page=DIFFICULTY_PAGE,
        section=MISSION_RESTRICTIONS_SECTION,
        choices={
            "Полные": "Full",
            "Сокращённые": "Abbreviated",
            "Только точка": "Dot Only",
            "Нейтральная точка": "Neutral Dot",
            "Выключены": "Off",
        },
        default="Full",
    )
    map_coalition_visibility: ForcedOptions.Views = choices_option(
        "Видимость на карте",
        page=DIFFICULTY_PAGE,
        section=MISSION_RESTRICTIONS_SECTION,
        choices={
            "Всё": ForcedOptions.Views.All,
            "Туман войны": ForcedOptions.Views.Allies,
            "Только союзники": ForcedOptions.Views.OnlyAllies,
            "Только свой ЛА": ForcedOptions.Views.MyAircraft,
            "Только карта": ForcedOptions.Views.OnlyMap,
        },
        default=ForcedOptions.Views.All,
    )
    external_views_allowed: bool = boolean_option(
        "Разрешить внешние виды",
        DIFFICULTY_PAGE,
        MISSION_RESTRICTIONS_SECTION,
        default=True,
    )

    easy_communication: Optional[bool] = choices_option(
        "Упрощённая связь",
        page=DIFFICULTY_PAGE,
        section=MISSION_RESTRICTIONS_SECTION,
        choices={
            "На выбор игрока": None,
            "Принудительно вкл.": True,
            "Принудительно выкл.": False,
        },
        default=None,
    )

    battle_damage_assessment: Optional[bool] = choices_option(
        "Оценка боевых повреждений",
        page=DIFFICULTY_PAGE,
        section=MISSION_RESTRICTIONS_SECTION,
        choices={
            "На выбор игрока": None,
            "Принудительно вкл.": True,
            "Принудительно выкл.": False,
        },
        default=None,
    )

    # Campaign management
    # General
    restrict_weapons_by_date: bool = boolean_option(
        "Ограничить оружие по дате",
        page=CAMPAIGN_MANAGEMENT_PAGE,
        section=GENERAL_SECTION,
        default=True,
        detail=(
            "Ограничивает доступность оружия датой кампании. Может не применяться "
            "к своим подвескам из-за неполных данных."
        ),
    )
    # Pilots and Squadrons
    ai_pilot_levelling: bool = boolean_option(
        "Рост уровня пилотов ИИ",
        CAMPAIGN_MANAGEMENT_PAGE,
        PILOTS_AND_SQUADRONS_SECTION,
        default=True,
        detail=(
            "Повышают ли пилоты ИИ уровень после определённого числа вылетов."
            " Уровень пилота влияет на мастерство ИИ, так что это можно отключить,"
            " чтобы не встретить аса!"
        ),
    )
    #: Feature flag for squadron limits.
    enable_squadron_pilot_limits: bool = boolean_option(
        "Лимит пилотов на эскадрилью (в разработке)",
        CAMPAIGN_MANAGEMENT_PAGE,
        PILOTS_AND_SQUADRONS_SECTION,
        default=False,
        detail=(
            "Если включено, число пилотов в эскадрильях ограничено, а погибшие "
            "пилоты восполняются с фиксированной скоростью (см. настройки ниже). "
            "Автозакупка может купить ЛА, для которых нет пилотов, "
            "поэтому функция ещё в разработке."
        ),
    )
    #: The maximum number of pilots a squadron can have at one time. Changing this after
    #: the campaign has started will have no immediate effect; pilots already in the
    #: squadron will not be removed if the limit is lowered and pilots will not be
    #: immediately created if the limit is raised.
    squadron_pilot_limit: int = bounded_int_option(
        "Максимум пилотов в эскадрилье",
        CAMPAIGN_MANAGEMENT_PAGE,
        PILOTS_AND_SQUADRONS_SECTION,
        default=12,
        min=12,
        max=72,
        detail=(
            "Максимальное число активных пилотов эскадрильи. "
            "Изменение подействует не сразу, но повлияет "
            "на пополнение в следующих ходах."
        ),
    )
    #: The number of pilots a squadron can replace per turn.
    squadron_replenishment_rate: int = bounded_int_option(
        "Скорость пополнения пилотов",
        CAMPAIGN_MANAGEMENT_PAGE,
        PILOTS_AND_SQUADRONS_SECTION,
        default=4,
        min=1,
        max=20,
        detail=(
            "Сколько пилотов максимум набирает каждая эскадрилья в конце хода. "
            "Сверх лимита пилоты не набираются, но каждая эскадрилья со свободными "
            "местами каждый ход набирает столько пилотов, пока не дойдёт до лимита."
        ),
    )

    # HQ Automation
    automate_runway_repair: bool = boolean_option(
        "Автоматический ремонт ВПП",
        CAMPAIGN_MANAGEMENT_PAGE,
        HQ_AUTOMATION_SECTION,
        default=False,
        remember_player_choice=True,
    )
    automate_front_line_reinforcements: bool = boolean_option(
        "Автоматические закупки для фронта",
        CAMPAIGN_MANAGEMENT_PAGE,
        HQ_AUTOMATION_SECTION,
        default=False,
        remember_player_choice=True,
    )
    automate_aircraft_reinforcements: bool = boolean_option(
        "Автоматические закупки ЛА",
        CAMPAIGN_MANAGEMENT_PAGE,
        HQ_AUTOMATION_SECTION,
        default=False,
        remember_player_choice=True,
    )
    auto_ato_behavior: AutoAtoBehavior = choices_option(
        "Автоматическое планирование пакетов",
        CAMPAIGN_MANAGEMENT_PAGE,
        HQ_AUTOMATION_SECTION,
        default=AutoAtoBehavior.Default,
        choices={
            "Выключено": AutoAtoBehavior.Disabled,
            "Никогда не назначать пилотов-игроков": AutoAtoBehavior.Never,
            "Без предпочтений": AutoAtoBehavior.Default,
            "Предпочитать пилотов-игроков": AutoAtoBehavior.Prefer,
        },
        detail=(
            "Автозакупкой ЛА управляет автопланировщик, поэтому отключение "
            "автопланирования отключает и автозакупку."
        ),
    )
    auto_ato_player_missions_asap: bool = boolean_option(
        "Автопакеты с игроками планируются как можно раньше",
        CAMPAIGN_MANAGEMENT_PAGE,
        HQ_AUTOMATION_SECTION,
        default=True,
    )
    automate_front_line_stance: bool = boolean_option(
        "Автоматически управлять тактикой на фронте",
        CAMPAIGN_MANAGEMENT_PAGE,
        HQ_AUTOMATION_SECTION,
        default=True,
    )
    reserves_procurement_target: int = 10

    # Mission Generator

    # Commanders
    game_master_slots: int = bounded_int_option(
        "Мастер игры",
        page=MISSION_GENERATOR_PAGE,
        section=COMMANDERS_SECTION,
        default=0,
        min=0,
        max=100,
    )
    tactical_commander_slots: int = bounded_int_option(
        "Тактический командир",
        page=MISSION_GENERATOR_PAGE,
        section=COMMANDERS_SECTION,
        default=0,
        min=0,
        max=100,
    )
    jtac_operator_slots: int = bounded_int_option(
        "JTAC/оператор",
        page=MISSION_GENERATOR_PAGE,
        section=COMMANDERS_SECTION,
        default=0,
        min=0,
        max=100,
    )
    observer_slots: int = bounded_int_option(
        "Наблюдатель",
        page=MISSION_GENERATOR_PAGE,
        section=COMMANDERS_SECTION,
        default=0,
        min=0,
        max=100,
    )

    # Gameplay
    ai_has_unlimited_fuel: bool = boolean_option(
        "Бесконечное топливо для звеньев ИИ",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        default=True,
        detail=(
            "Если включено, у звеньев только из ИИ топливо бесконечно. Можно "
            "отключить, чтобы ИИ играл по тем же правилам, что и игроки, но учтите: "
            "ИИ DCS не слишком бережёт топливо и часто остаётся без него там, "
            "где игрок бы справился."
        ),
    )
    reload_pre_sim_checkpoint_on_abort: bool = boolean_option(
        "При прерывании возвращать миссию к состоянию до взлёта",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        default=True,
        detail=(
            "Если включено, при прерывании взлёта игра автоматически загрузит "
            "сохранение до взлёта. Если выключено, после прерывания взлёта игру "
            "нужно будет загрузить вручную."
        ),
    )
    turnless_mode: bool = boolean_option(
        "Режим без ходов (в разработке)",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        default=False,
        detail=(
            "Если включено, ход не заканчивается после миссии. Новую миссию "
            "можно начать с того места, где закончилась предыдущая."
        ),
    )
    fast_forward_stop_condition: FastForwardStopCondition = choices_option(
        "Ускорять время до",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        default=FastForwardStopCondition.DISABLED,
        choices={
            "Без ускорения": FastForwardStopCondition.DISABLED,
            "Время запуска игрока": FastForwardStopCondition.PLAYER_STARTUP,
            "Время руления игрока": FastForwardStopCondition.PLAYER_TAXI,
            "Время взлёта игрока": FastForwardStopCondition.PLAYER_TAKEOFF,
            "Игрок на IP": FastForwardStopCondition.PLAYER_AT_IP,
            "Первый контакт": FastForwardStopCondition.FIRST_CONTACT,
            "Вручную": FastForwardStopCondition.MANUAL,
        },
        detail=(
            "Когда прекращается ускорение времени: "
            "Без ускорения — ускорение отключено. "
            "Время запуска игрока — ускорять до времени запуска двигателей игрока. "
            "Время руления игрока — ускорять до времени руления игрока. "
            "Время взлёта игрока — ускорять до времени взлёта игрока. "
            "Первый контакт — ускорять до первого контакта синих и красных. "
            "Вручную — ручное управление ускорением. Кнопки управления включаются ключом --show-sim-speed-controls."
        ),
    )
    combat_resolution_method: CombatResolutionMethod = choices_option(
        "Бой при ускорении времени",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        default=CombatResolutionMethod.SKIP,
        choices={
            "Пауза": CombatResolutionMethod.PAUSE,
            "Расчёт боя (в разработке)": CombatResolutionMethod.RESOLVE,
            "Пропуск боя": CombatResolutionMethod.SKIP,
        },
        detail=(
            "Что происходит, если при ускорении времени начинается бой. "
            "Пауза — остановить ускорение и сгенерировать миссию. Ускорение может прекратиться раньше условия из настройки выше. "
            "Расчёт боя (в разработке) — автоматически рассчитать бой. Метод очень примитивный и приводит к большим потерям. "
            "Пропуск боя — пропустить бой, как будто его не было."
        ),
    )
    supercarrier: bool = boolean_option(
        "Использовать модуль Supercarrier",
        MISSION_GENERATOR_PAGE,
        GAMEPLAY_SECTION,
        default=False,
        remember_player_choice=True,
    )
    generate_marks: bool = boolean_option(
        "Отмечать цели на карте",
        MISSION_GENERATOR_PAGE,
        GAMEPLAY_SECTION,
        default=True,
    )
    generate_dark_kneeboard: bool = boolean_option(
        "Тёмный планшет (kneeboard)",
        MISSION_GENERATOR_PAGE,
        GAMEPLAY_SECTION,
        default=False,
        detail=(
            "Тёмный планшет для ночных миссий. Скорее всего, планшет на "
            "колене пилота станет нечитаемым."
        ),
    )
    never_delay_player_flights: bool = boolean_option(
        "Звенья игроков игнорируют TOT и появляются сразу",
        MISSION_GENERATOR_PAGE,
        GAMEPLAY_SECTION,
        default=False,
        detail=(
            "Не меняет время путевых точек пакетов. Не используйте, если игроки "
            "стартуют с ВПП или в воздухе."
        ),
        tooltip=(
            "Всегда создаёт ЛА игроков сразу, даже если их время старта больше чем "
            "через 10 минут после начала миссии. <strong>Это не меняет "
            "расписание миссии. Ваш TOT не изменится. Параметр лишь "
            "позволяет игроку подождать на земле.</strong>"
        ),
    )
    default_start_type: StartType = choices_option(
        "Тип старта ИИ по умолчанию",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        choices={v.display_name: v for v in StartType},
        default=StartType.COLD,
        detail=(
            "Внимание: любой вариант, кроме холодного, заметно сократит число "
            "целей для заданий OCA/Aircraft, а звенья OCA/Aircraft не будут "
            "включаться в автоматически планируемые пакеты OCA."
        ),
    )
    # Mission specific
    desired_player_mission_duration: timedelta = minutes_option(
        "Желаемая длительность миссии",
        page=MISSION_GENERATOR_PAGE,
        section=GAMEPLAY_SECTION,
        default=timedelta(minutes=60),
        min=30,
        max=150,
        detail=(
            "Время от начала хода, в течение которого "
            "действует прикрытие одним или несколькими звеньями CAP, "
            "заправщики, не привязанные к пакету, находятся в зоне, "
            "а у остальных звеньев наступает их TOT."
        ),
    )

    # Performance
    perf_smoke_gen: bool = boolean_option(
        "Дым на линии фронта",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    perf_smoke_spacing: int = bounded_int_option(
        "Шаг генераторов дыма (больше — меньше дыма)",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=1600,
        min=800,
        max=24000,
    )
    perf_red_alert_state: bool = boolean_option(
        "ЗРК стартуют в режиме боевой готовности",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    perf_artillery: bool = boolean_option(
        "Артиллерийские удары",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    generate_fire_tasks_for_missile_sites: bool = boolean_option(
        "Задачи на пуск для ракетных позиций",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        detail=(
            "Если включено, ракетные позиции (V2, Scud и т. п.) в начале миссии "
            "стреляют по случайным целям."
        ),
        default=True,
    )
    perf_moving_units: bool = boolean_option(
        "Движущаяся наземная техника",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    convoys_travel_full_distance: bool = boolean_option(
        "Колонны проходят весь путь между контрольными точками",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    perf_infantry: bool = boolean_option(
        "Пехотные отделения вместе с техникой",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    perf_destroyed_units: bool = boolean_option(
        "Остовы техники, уничтоженной в прошлые ходы",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    # Performance culling
    perf_culling: bool = boolean_option(
        "Отсечение дальних единиц",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=False,
    )
    perf_culling_distance: int = bounded_int_option(
        "Дистанция отсечения (км)",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=100,
        min=10,
        max=10000,
        causes_expensive_game_update=True,
    )
    perf_do_not_cull_threatening_iads: bool = boolean_option(
        "Не отсекать угрожающую ПВО",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
    )
    perf_do_not_cull_carrier: bool = boolean_option(
        "Не отсекать окрестности авианосца",
        page=MISSION_GENERATOR_PAGE,
        section=PERFORMANCE_SECTION,
        default=True,
        causes_expensive_game_update=True,
    )

    # Cheating. Not using auto settings because the same page also has buttons which do
    # not alter settings.
    show_red_ato: bool = False
    enable_frontline_cheats: bool = False
    enable_base_capture_cheat: bool = False
    enable_runway_state_cheat: bool = False

    only_player_takeoff: bool = True  # Legacy parameter do not use

    def save_player_settings(self) -> None:
        """Saves the player's global settings to the user directory."""
        settings: dict[str, Any] = {}
        for name, description in self.all_fields():
            if description.remember_player_choice:
                settings[name] = self.__dict__[name]

        with self._player_settings_file.open("w", encoding="utf-8") as settings_file:
            yaml.dump(settings, settings_file, sort_keys=False, explicit_start=True)

    def merge_player_settings(self) -> None:
        """Updates with the player's global settings."""
        settings_path = self._player_settings_file
        if not settings_path.exists():
            return
        with settings_path.open(encoding="utf-8") as settings_file:
            data = yaml.safe_load(settings_file)

        if data is None:
            logging.warning("Saved settings file %s is empty", settings_path)
            return

        expected_types = get_type_hints(Settings)
        for key, value in data.items():
            if key not in self.__dict__:
                logging.warning(
                    "Unexpected settings key found in %s: %s. Ignoring.",
                    settings_path,
                    key,
                )
                continue

            expected_type = expected_types[key]
            if not isinstance(value, expected_type):
                logging.error(
                    "%s in %s does not have the expected type %s (is %s). Ignoring.",
                    key,
                    settings_path,
                    expected_type.__name__,
                    value.__class__.__name__,
                )
                continue
            self.__dict__[key] = value

    @property
    def _player_settings_file(self) -> Path:
        """Returns the path to the player's global settings file."""
        return liberation_user_dir() / "settings.yaml"

    def __setstate__(self, state: dict[str, Any]) -> None:
        # __setstate__ is called with the dict of the object being unpickled. We
        # can provide save compatibility for new settings options (which
        # normally would not be present in the unpickled object) by creating a
        # new settings object, updating it with the unpickled state, and
        # updating our dict with that.
        new_state = Settings().__dict__
        new_state.update(state)
        self.__dict__.update(new_state)

    @classmethod
    def _field_description(cls, settings_field: Field[Any]) -> OptionDescription:
        return settings_field.metadata[SETTING_DESCRIPTION_KEY]

    @classmethod
    def pages(cls) -> Iterator[str]:
        seen: set[str] = set()
        for settings_field in cls._user_fields():
            description = cls._field_description(settings_field)
            if description.page not in seen:
                yield description.page
                seen.add(description.page)

    @classmethod
    def sections(cls, page: str) -> Iterator[str]:
        seen: set[str] = set()
        for settings_field in cls._user_fields():
            description = cls._field_description(settings_field)
            if description.page == page and description.section not in seen:
                yield description.section
                seen.add(description.section)

    @classmethod
    def all_fields(cls) -> Iterator[tuple[str, OptionDescription]]:
        for settings_field in cls._user_fields():
            yield settings_field.name, cls._field_description(settings_field)

    @classmethod
    def fields_for(
        cls, page: str, section: str
    ) -> Iterator[tuple[str, OptionDescription]]:
        for name, description in cls.all_fields():
            if description.page == page and description.section == section:
                yield name, description

    @classmethod
    def _user_fields(cls) -> Iterator[Field[Any]]:
        for settings_field in fields(cls):
            if SETTING_DESCRIPTION_KEY in settings_field.metadata:
                yield settings_field
