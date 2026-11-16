-- Top 10 fighters by career KO/TKO wins.

select winner_first_name, winner_last_name, count(*) as ko_tko_wins
from {{ ref('fct_fights') }}
where winner_fighter_id is not null and method_category = 'KO/TKO'
group by winner_first_name, winner_last_name
order by ko_tko_wins desc
limit 10
