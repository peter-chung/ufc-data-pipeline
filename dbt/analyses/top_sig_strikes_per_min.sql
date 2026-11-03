-- Top 10 fighters by significant strikes landed per minute (career average).
--
-- dim_ufcstats_fighter.sig_str_landed_per_min is ufcstats' own career-average
-- stat, but it's unreliable for fighters with very little total cage time --
-- a few landed strikes divided by a tiny total fight duration can produce an
-- inflated rate even with 5+ fights. Guard against that with a volume floor
-- (minimum total significant strikes landed, from fight-level data) rather
-- than just a minimum fight count.

with fighter_strikes as (
    select fighter_1_id as fighter_id, fighter_1_sig_str_landed as landed
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_1_sig_str_landed is not null
    union all
    select fighter_2_id as fighter_id, fighter_2_sig_str_landed as landed
    from {{ ref('fct_ufcstats_fights') }}
    where fighter_2_sig_str_landed is not null
),

totals as (
    select fighter_id, sum(landed) as total_sig_str_landed, count(*) as total_fights
    from fighter_strikes
    group by fighter_id
)

select
    f.first_name,
    f.last_name,
    f.sig_str_landed_per_min,
    t.total_sig_str_landed,
    t.total_fights
from totals t
join {{ ref('dim_ufcstats_fighter') }} f on t.fighter_id = f.fighter_id
where t.total_fights >= 5 and t.total_sig_str_landed >= 150
order by f.sig_str_landed_per_min desc
limit 10
