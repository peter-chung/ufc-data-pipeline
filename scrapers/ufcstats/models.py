from dataclasses import dataclass, field


@dataclass
class FighterRef:
    id: str
    name: str
    link: str | None = None


@dataclass
class FighterRoundStats:
    # round=None means the fight-totals row, not round 0
    round: int | None = None
    knockdowns: str | None = None
    sig_str: str | None = None
    sig_str_pct: str | None = None
    total_str: str | None = None
    td: str | None = None
    td_pct: str | None = None
    sub_attempts: str | None = None
    reversals: str | None = None
    control_time: str | None = None
    head_str: str | None = None
    body_str: str | None = None
    leg_str: str | None = None
    distance_str: str | None = None
    clinch_str: str | None = None
    ground_str: str | None = None


@dataclass
class Fight:
    id: str
    link: str
    fighter_1: FighterRef
    fighter_2: FighterRef
    weight_class: str | None = None
    method: str | None = None
    finish_round: str | None = None
    finish_time: str | None = None
    time_format: str | None = None
    referee: str | None = None
    details: str | None = None
    fighter_1_result: str | None = None
    fighter_2_result: str | None = None
    fighter_1_stats: list[FighterRoundStats] = field(default_factory=list)
    fighter_2_stats: list[FighterRoundStats] = field(default_factory=list)


@dataclass
class Event:
    id: str
    name: str
    link: str
    date_raw: str
    completed: bool
    location_raw: str | None = None
    fights: list[Fight] = field(default_factory=list)


@dataclass
class FightHistoryEntry:
    """One row of a fighter's own UFC-only fight history. A thin summary,
    not full round-by-round stats -- those live on the fight's own page,
    already captured independently via event_scraper if that card was
    scraped as part of the completed-events backfill."""

    fight_id: str
    fight_link: str
    opponent_id: str
    opponent_name: str
    opponent_link: str | None = None
    event_name: str | None = None
    event_link: str | None = None
    event_date_raw: str | None = None
    result: str | None = None
    knockdowns: str | None = None
    sig_str: str | None = None
    td: str | None = None
    sub_attempts: str | None = None
    method: str | None = None
    method_detail: str | None = None
    finish_round: str | None = None
    finish_time: str | None = None


@dataclass
class FighterProfile:
    id: str
    first_name: str
    last_name: str
    link: str
    nickname: str | None = None
    height: str | None = None
    weight: str | None = None
    reach: str | None = None
    stance: str | None = None
    dob: str | None = None
    slpm: str | None = None
    str_acc: str | None = None
    sapm: str | None = None
    str_def: str | None = None
    td_avg: str | None = None
    td_acc: str | None = None
    td_def: str | None = None
    sub_avg: str | None = None
    career_record_raw: str | None = None
    fight_history: list[FightHistoryEntry] = field(default_factory=list)
