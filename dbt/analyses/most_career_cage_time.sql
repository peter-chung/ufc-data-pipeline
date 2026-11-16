-- Top 10 fighters by total career cage time (sum of fight_duration_seconds
-- across every fight).

with dur as (
    select fighter_1_id as fighter_id, fight_duration_seconds as seconds
    from {{ ref('fct_fights') }}
    where fight_duration_seconds is not null
    union all
    select fighter_2_id as fighter_id, fight_duration_seconds as seconds
    from {{ ref('fct_fights') }}
    where fight_duration_seconds is not null
)

select
    f.first_name,
    f.last_name,
    sum(dur.seconds) as total_seconds,
    round(sum(dur.seconds) / 60.0, 1) as total_minutes
from dur
join {{ ref('dim_fighters') }} f on dur.fighter_id = f.fighter_id
group by f.first_name, f.last_name
order by total_seconds desc
limit 10
