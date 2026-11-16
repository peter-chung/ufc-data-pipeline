-- Per-fighter win/loss/finish breakdown. Uses method_category (not the raw
-- method column) so this works consistently regardless of which raw method
-- vocabulary a given fight came from.
--
-- Sort by whichever column is interesting: wins, losses, sub_wins,
-- ko_tko_wins, decision_wins.

with results as (
    select fighter_1_id as fighter_id, fighter_1_result as result, method_category
    from {{ ref('fct_fights') }}
    union all
    select fighter_2_id as fighter_id, fighter_2_result as result, method_category
    from {{ ref('fct_fights') }}
),

agg as (
    select
        fighter_id,
        countif(result = 'W') as wins,
        countif(result = 'L') as losses,
        countif(result = 'W' and method_category = 'SUB') as sub_wins,
        countif(result = 'W' and method_category = 'KO/TKO') as ko_tko_wins,
        countif(result = 'W' and method_category = 'DEC') as decision_wins
    from results
    group by fighter_id
)

select f.first_name, f.last_name, a.*
from agg a
join {{ ref('dim_fighters') }} f on a.fighter_id = f.fighter_id
order by a.wins desc
limit 10
