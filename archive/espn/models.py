from dataclasses import dataclass, field


@dataclass
class Fighter:
    # identity (always required)
    id: str
    first_name: str

    # identity (optional)
    last_name: str | None = None
    country: str | None = None
    link: str | None = None
    flag: str | None = None
    gender: str | None = None
    head_img: str | None = None
    body_img: str | None = None

    # physical stats (optional)
    height: str | None = None
    weight: str | None = None
    reach: str | None = None
    stance: str | None = None
    age: int | None = None

    # performance stats (optional)
    record: str | None = None
    sig_str_lpm: str | None = None
    sig_str_acc: str | None = None
    td_avg: str | None = None
    td_acc: str | None = None
    sub_avg: str | None = None
    is_pre: bool | None = None
    is_win: bool | None = None


@dataclass
class Fight:
    # matchup (always required)
    id: str
    fighter_1: Fighter
    fighter_2: Fighter
    card_segment: str

    # fight details (optional)
    note: str | None = None
    date_time: str | None = None

    # broadcast / status (optional)
    networks: str | None = None
    status: str | None = None
    status_detail: str | None = None
    round_number: str | None = None
    finish_time: str | None = None
    method: str | None = None
    method_short: str | None = None


@dataclass
class Venue:
    id: str
    name: str
    city: str
    country: str
    state: str | None = None
    address: str | None = None


@dataclass
class Event:
    id: str
    name: str
    link: str
    date: str
    status: str
    status_detail: str
    completed: bool
    is_postponed_or_canceled: bool
    venue: Venue
    fights: list[Fight] = field(default_factory=list)
    short_name: str | None = None


@dataclass
class StatValue:
    abbreviation: str
    value: str


@dataclass
class StatColumn:
    abbreviation: str
    name: str


@dataclass
class FightHistoryRow:
    date: str | None = None
    opponent_name: str | None = None
    opponent_link: str | None = None
    event_name: str | None = None
    event_link: str | None = None
    result: str | None = None
    stats: list[StatValue] = field(default_factory=list)


@dataclass
class FighterProfile:
    # identity (always required)
    id: str
    first_name: str

    # identity (optional)
    last_name: str | None = None
    nickname: str | None = None
    country: str | None = None
    country_code: str | None = None
    team: str | None = None
    head_img: str | None = None
    flag: str | None = None

    # physical / bio (optional)
    dob: str | None = None
    dob_raw: str | None = None
    gender: str | None = None
    height: str | None = None
    height_weight: str | None = None
    reach: str | None = None
    stance: str | None = None
    weight_class: str | None = None
    weight_class_short: str | None = None

    # career totals (optional)
    record: str | None = None
    tko_record: str | None = None
    sub_record: str | None = None

    # fight history (optional)
    striking_history: list[FightHistoryRow] = field(default_factory=list)
    striking_columns: list[StatColumn] = field(default_factory=list)
    clinch_history: list[FightHistoryRow] = field(default_factory=list)
    clinch_columns: list[StatColumn] = field(default_factory=list)
    ground_history: list[FightHistoryRow] = field(default_factory=list)
    ground_columns: list[StatColumn] = field(default_factory=list)
