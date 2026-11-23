-- Top 10 best striking defense: lowest significant strikes absorbed per
-- minute (career average). Same volume-floor issue as strikes landed per
-- minute -- a fighter with very little total cage time can show an
-- artificially low absorbed rate by chance, so guard with a minimum total
-- strikes absorbed (from fight-level data) rather than just a fight count.

with absorbed as (
    select fighter_1_id as fighter_id, fighter_2_sig_str_landed as landed
    from {{ ref('fct_fights') }}
    where fighter_2_sig_str_landed is not null
    union all
    select fighter_2_id as fighter_id, fighter_1_sig_str_landed as landed
    from {{ ref('fct_fights') }}
    where fighter_1_sig_str_landed is not null
),

totals as (
    select fighter_id, sum(landed) as total_absorbed, count(*) as total_fights
    from absorbed
    group by fighter_id
)

select
    f.first_name,
    f.last_name,
    f.career_sig_str_absorbed_per_min,
    t.total_absorbed,
    t.total_fights
from totals t
join {{ ref('dim_fighters') }} f on t.fighter_id = f.fighter_id
where t.total_fights >= 5 and t.total_absorbed >= 150 and f.career_sig_str_absorbed_per_min is not null
order by f.career_sig_str_absorbed_per_min asc
limit 10
