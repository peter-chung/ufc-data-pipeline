with source as (
    select * from {{ source('raw', 'ufcstats_fighter_profiles') }}
    qualify row_number() over (partition by id order by loaded_at desc) = 1
),

unnested as (
    select
        source.id as fighter_id,
        history
    from source
    cross join unnest(fight_history) as history
)

select
    history.fight_id,
    fighter_id,
    history.opponent_id,
    history.opponent_name,
    history.opponent_link,
    history.event_name,
    history.event_link,
    safe.parse_date('%b %d, %Y', replace(history.event_date_raw, '.', '')) as event_date,
    history.result,
    safe_cast(history.knockdowns as int64) as knockdowns,
    safe_cast(history.sig_str as int64) as sig_str_landed,
    safe_cast(history.td as int64) as td_landed,
    safe_cast(history.sub_attempts as int64) as sub_attempts,
    history.method,
    history.method_detail,
    safe_cast(history.finish_round as int64) as finish_round,
    history.finish_time
from unnested
