-- Top 10 fighters by takedown accuracy (career average).
--
-- dim_ufcstats_fighter.career_td_acc_pct is ufcstats' own career-average stat,
-- but it's unreliable for fighters with very few career takedown attempts --
-- a fighter who's gone 1-for-1 or 2-for-2 shows a meaningless 100%. Guard
-- against that with a volume floor on total takedowns attempted (not landed,
-- since accuracy = landed/attempted) from fight-level data.
--
-- Checked empirically: flat 100% outliers (e.g. 1-for-1-style small samples)
-- persist up through a 10-attempt floor; they clear up by >= 20 attempts,
-- which is also low enough to keep 801 fighters eligible.

with fighter_takedowns as (
    select fighter_1_id as fighter_id, fighter_1_td_attempted as attempted, fighter_1_td_landed as landed
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_1_td_attempted is not null
    union all
    select fighter_2_id as fighter_id, fighter_2_td_attempted as attempted, fighter_2_td_landed as landed
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_2_td_attempted is not null
),

totals as (
    select 
        fighter_id, sum(attempted) as total_td_attempted, 
        sum(landed) as total_td_landed
    from fighter_takedowns
    group by fighter_id
),

td_accuracy as (
    select
        fighter_id,
        total_td_attempted,
        total_td_landed,
        safe_divide(total_td_landed, total_td_attempted) * 100 as td_acc_pct
    from totals
)

select
    f.first_name,
    f.last_name,
    t.total_td_attempted,
    t.total_td_landed,
    t.td_acc_pct
from td_accuracy t
join {{ ref('dim_ufcstats_fighter') }} f on t.fighter_id = f.fighter_id
where t.total_td_attempted >= 20
order by t.td_acc_pct desc
limit 10
