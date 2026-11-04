with ufc_results as (
    select fighter_1_id as fighter_id, fighter_1_result as result
    from {{ ref('stg_ufcstats_events__fights') }}
    union all
    select fighter_2_id as fighter_id, fighter_2_result as result
    from {{ ref('stg_ufcstats_events__fights') }}
),

ufc_record as (
    select
        fighter_id,
        countif(result = 'W') as wins,
        countif(result = 'L') as losses,
        countif(result = 'D') as draws,
        countif(result = 'NC') as no_contests
    from ufc_results
    group by fighter_id
)

select
  p.fighter_id,
  p.first_name,
  p.last_name,
  p.fighter_link,
  p.nickname,
  p.height_inches,
  p.weight_lbs,
  p.reach_inches,
  p.stance,
  p.date_of_birth,
  p.career_sig_str_landed_per_min,
  p.career_sig_str_acc_pct,
  p.career_sig_str_absorbed_per_min,
  p.career_sig_str_def_pct,
  p.career_td_avg_per_15min,
  p.career_td_acc_pct,
  p.career_td_def_pct,
  p.career_sub_avg_per_15min,
  p.career_wins,
  p.career_losses,
  p.career_draws,
  p.career_no_contests,
  coalesce(r.wins, 0) as wins,
  coalesce(r.losses, 0) as losses,
  coalesce(r.draws, 0) as draws,
  coalesce(r.no_contests, 0) as no_contests,
  p.loaded_at
from {{ ref('stg_ufcstats_fighter_profiles') }} p
left join ufc_record r on p.fighter_id = r.fighter_id
