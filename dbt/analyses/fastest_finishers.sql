-- Top 10 fastest finishers: lowest average fight_duration_seconds among
-- finish wins (KO/TKO or submission). Requires at least 3 career finishes
-- so a single lucky quick finish doesn't dominate the list.

with finishes as (
    select fighter_1_id as fighter_id, fight_duration_seconds as seconds
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_1_result = 'W' and method_category in ('KO/TKO', 'SUB') and fight_duration_seconds is not null
    union all
    select fighter_2_id as fighter_id, fight_duration_seconds as seconds
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_2_result = 'W' and method_category in ('KO/TKO', 'SUB') and fight_duration_seconds is not null
)

select
    f.first_name,
    f.last_name,
    round(avg(finishes.seconds), 1) as avg_finish_seconds,
    count(*) as finish_count
from finishes
join {{ ref('dim_ufcstats_fighter') }} f on finishes.fighter_id = f.fighter_id
group by f.first_name, f.last_name
having count(*) >= 3
order by avg_finish_seconds asc
limit 10
