-- Top 10 fighters by total career takedown/ground control time.

with ct as (
    select fighter_1_id as fighter_id, fighter_1_control_time_seconds as seconds
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_1_control_time_seconds is not null
    union all
    select fighter_2_id as fighter_id, fighter_2_control_time_seconds as seconds
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_2_control_time_seconds is not null
)

select
    f.first_name,
    f.last_name,
    sum(ct.seconds) as total_control_seconds,
    round(sum(ct.seconds) / 60.0, 1) as total_control_minutes
from ct
join {{ ref('dim_ufcstats_fighter') }} f on ct.fighter_id = f.fighter_id
group by f.first_name, f.last_name
order by total_control_seconds desc
limit 10
