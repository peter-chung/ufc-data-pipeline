-- Top 10 fighters by decision rate: % of wins that went to the judges'
-- scorecards rather than ending in a finish. Guarded by a minimum total
-- UFC wins (not decision count), so a 1-win fighter whose only win happened
-- to be a decision doesn't show a meaningless 100%.

with decision_wins as (
    select fighter_1_id as fighter_id
    from {{ ref('fct_fights') }}
    where fighter_1_result = 'W' and method_category = 'DEC'
    union all
    select fighter_2_id as fighter_id
    from {{ ref('fct_fights') }}
    where fighter_2_result = 'W' and method_category = 'DEC'
),

decision_win_totals as (
    select
        fighter_id, count(*) as total_decision_wins
    from decision_wins
    group by fighter_id
),

decision_rates as (
    select
        f.first_name,
        f.last_name,
        f.wins,
        t.total_decision_wins,
        safe_divide(t.total_decision_wins, f.wins) * 100 as decision_rate_pct
    from decision_win_totals t
    join {{ ref('dim_fighters') }} f on t.fighter_id = f.fighter_id
)

select
    first_name,
    last_name,
    wins,
    total_decision_wins,
    decision_rate_pct
from decision_rates
where wins >= 5
order by decision_rate_pct desc, total_decision_wins desc
limit 10
