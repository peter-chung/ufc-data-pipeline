select
    f.fight_id,
    f.event_id,
    f.fighter_1_id,
    f.fighter_2_id,
    e.event_name,
    e.event_date,
    e.venue.name as venue_name,
    e.venue.city as venue_city,
    e.venue.country as venue_country,
    f.card_segment,
    f.fight_date_time,
    f.status,
    f.status_detail,
    f.finish_round,
    f.finish_time,
    f.method,
    f.method_short,
    fighter_1.first_name as fighter_1_first_name,
    fighter_1.last_name as fighter_1_last_name,
    fighter_1.wins as fighter_1_wins,
    fighter_1.losses as fighter_1_losses,
    fighter_1.draws as fighter_1_draws,
    f.fighter_1_is_win,
    f.fighter_1_sig_str_lpm,
    f.fighter_1_sig_str_acc_pct,
    f.fighter_1_td_avg,
    f.fighter_1_td_acc_pct,
    f.fighter_1_sub_avg,
    fighter_2.first_name as fighter_2_first_name,
    fighter_2.last_name as fighter_2_last_name,
    fighter_2.wins as fighter_2_wins,
    fighter_2.losses as fighter_2_losses,
    fighter_2.draws as fighter_2_draws,
    f.fighter_2_is_win,
    f.fighter_2_sig_str_lpm,
    f.fighter_2_sig_str_acc_pct,
    f.fighter_2_td_avg,
    f.fighter_2_td_acc_pct,
    f.fighter_2_sub_avg,
    case
        when f.fighter_1_is_win then f.fighter_1_id
        when f.fighter_2_is_win then f.fighter_2_id
    end as winner_fighter_id,
    case
        when f.fighter_1_is_win then fighter_1.first_name
        when f.fighter_2_is_win then fighter_2.first_name
    end as winner_first_name,
    case
        when f.fighter_1_is_win then fighter_1.last_name
        when f.fighter_2_is_win then fighter_2.last_name
    end as winner_last_name
from {{ ref('stg_events__fights') }} as f
left join {{ ref('stg_events') }} as e
    on f.event_id = e.event_id
left join {{ ref('stg_fighter_profiles') }} as fighter_1
    on f.fighter_1_id = fighter_1.fighter_id
left join {{ ref('stg_fighter_profiles') }} as fighter_2
    on f.fighter_2_id = fighter_2.fighter_id
