with source as (
    select * from {{ source('raw', 'events') }}
    qualify row_number() over (partition by id order by loaded_at desc) = 1
),

unnested as (
    select
        source.id as event_id,
        fight
    from source
    cross join unnest(fights) as fight
)

select
    fight.id as fight_id,
    event_id,
    fight.fighter_1.id as fighter_1_id,
    fight.fighter_2.id as fighter_2_id,
    fight.card_segment,
    safe_cast(fight.date_time as timestamp) as fight_date_time,
    fight.status,
    fight.status_detail,
    safe_cast(regexp_extract(fight.round_number, r'(\d+)') as int64) as finish_round,
    fight.finish_time,
    fight.method,
    fight.method_short,
    fight.fighter_1.is_win as fighter_1_is_win,
    fight.fighter_2.is_win as fighter_2_is_win,
    safe_cast(fight.fighter_1.sig_str_lpm as float64) as fighter_1_sig_str_lpm,
    safe_cast(replace(fight.fighter_1.sig_str_acc, '%', '') as float64) as fighter_1_sig_str_acc_pct,
    safe_cast(fight.fighter_1.td_avg as float64) as fighter_1_td_avg,
    safe_cast(replace(fight.fighter_1.td_acc, '%', '') as float64) as fighter_1_td_acc_pct,
    safe_cast(fight.fighter_1.sub_avg as float64) as fighter_1_sub_avg,
    safe_cast(fight.fighter_2.sig_str_lpm as float64) as fighter_2_sig_str_lpm,
    safe_cast(replace(fight.fighter_2.sig_str_acc, '%', '') as float64) as fighter_2_sig_str_acc_pct,
    safe_cast(fight.fighter_2.td_avg as float64) as fighter_2_td_avg,
    safe_cast(replace(fight.fighter_2.td_acc, '%', '') as float64) as fighter_2_td_acc_pct,
    safe_cast(fight.fighter_2.sub_avg as float64) as fighter_2_sub_avg
from unnested
