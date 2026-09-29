with source as (
    select * from {{ source('raw', 'fighter_profiles') }}
    qualify row_number() over (partition by id order by loaded_at desc) = 1
),

unnested as (
    select
        source.id as fighter_id,
        history,
        clinch_history[safe_offset(idx)] as clinch,
        ground_history[safe_offset(idx)] as ground
    from source
    cross join unnest(striking_history) as history with offset as idx
)

select
  to_hex(md5(concat(
    fighter_id,
    '|',
    coalesce(cast(safe_cast(history.date as timestamp) as string), 'unknown_date'),
    '|',
    coalesce(history.opponent_name, 'unknown_opponent')
  ))) as fight_history_id,
  fighter_id,
  safe_cast(history.date as timestamp) as fight_date,
  history.opponent_name,
  history.opponent_link,
  history.event_name,
  history.event_link,
  history.result,
  safe_cast((select value from unnest(history.stats) where trim(abbreviation) = 'SSL') as int64) as sig_str_landed,
  safe_cast((select value from unnest(history.stats) where trim(abbreviation) = 'SSA') as int64) as sig_str_attempted,
  safe_cast((select value from unnest(history.stats) where trim(abbreviation) = 'KD') as int64) as knockdowns,
  safe_cast((select value from unnest(clinch.stats) where trim(abbreviation) = 'TDL') as int64) as takedowns_landed,
  safe_cast((select value from unnest(clinch.stats) where trim(abbreviation) = 'TDA') as int64) as takedowns_attempted,
  safe_cast((select value from unnest(ground.stats) where trim(abbreviation) = 'SM') as int64) as submission_attempts
from unnested