select
    f.fight_id,
    f.event_id,
    f.fight_order,
    f.fighter_1_id,
    f.fighter_2_id,
    e.event_name,
    e.event_date,
    e.completed as event_completed,
    e.location_raw,
    e.event_city,
    e.event_state,
    e.event_country,
    f.weight_class,
    f.method,
    f.method_category,
    f.finish_round,
    f.finish_time,
    f.time_format,
    f.referee,
    f.details,
    f.round_lengths_seconds,
    f.finish_time_elapsed_seconds,
    f.fight_duration_seconds,

    fighter_1.first_name as fighter_1_first_name,
    fighter_1.last_name as fighter_1_last_name,
    fighter_1.career_wins as fighter_1_career_wins,
    fighter_1.career_losses as fighter_1_career_losses,
    fighter_1.career_draws as fighter_1_career_draws,
    f.fighter_1_result,
    f.fighter_1_knockdowns,
    f.fighter_1_sig_str_landed,
    f.fighter_1_sig_str_attempted,
    f.fighter_1_sig_str_pct,
    f.fighter_1_total_str_landed,
    f.fighter_1_total_str_attempted,
    f.fighter_1_td_landed,
    f.fighter_1_td_attempted,
    f.fighter_1_td_pct,
    f.fighter_1_sub_attempts,
    f.fighter_1_reversals,
    f.fighter_1_control_time_seconds,
    f.fighter_1_head_str_landed,
    f.fighter_1_head_str_attempted,
    f.fighter_1_body_str_landed,
    f.fighter_1_body_str_attempted,
    f.fighter_1_leg_str_landed,
    f.fighter_1_leg_str_attempted,
    f.fighter_1_distance_str_landed,
    f.fighter_1_distance_str_attempted,
    f.fighter_1_clinch_str_landed,
    f.fighter_1_clinch_str_attempted,
    f.fighter_1_ground_str_landed,
    f.fighter_1_ground_str_attempted,

    fighter_2.first_name as fighter_2_first_name,
    fighter_2.last_name as fighter_2_last_name,
    fighter_2.career_wins as fighter_2_career_wins,
    fighter_2.career_losses as fighter_2_career_losses,
    fighter_2.career_draws as fighter_2_career_draws,
    f.fighter_2_result,
    f.fighter_2_knockdowns,
    f.fighter_2_sig_str_landed,
    f.fighter_2_sig_str_attempted,
    f.fighter_2_sig_str_pct,
    f.fighter_2_total_str_landed,
    f.fighter_2_total_str_attempted,
    f.fighter_2_td_landed,
    f.fighter_2_td_attempted,
    f.fighter_2_td_pct,
    f.fighter_2_sub_attempts,
    f.fighter_2_reversals,
    f.fighter_2_control_time_seconds,
    f.fighter_2_head_str_landed,
    f.fighter_2_head_str_attempted,
    f.fighter_2_body_str_landed,
    f.fighter_2_body_str_attempted,
    f.fighter_2_leg_str_landed,
    f.fighter_2_leg_str_attempted,
    f.fighter_2_distance_str_landed,
    f.fighter_2_distance_str_attempted,
    f.fighter_2_clinch_str_landed,
    f.fighter_2_clinch_str_attempted,
    f.fighter_2_ground_str_landed,
    f.fighter_2_ground_str_attempted,

    case
        when f.fighter_1_result = 'W' then f.fighter_1_id
        when f.fighter_2_result = 'W' then f.fighter_2_id
    end as winner_fighter_id,
    case
        when f.fighter_1_result = 'W' then fighter_1.first_name
        when f.fighter_2_result = 'W' then fighter_2.first_name
    end as winner_first_name,
    case
        when f.fighter_1_result = 'W' then fighter_1.last_name
        when f.fighter_2_result = 'W' then fighter_2.last_name
    end as winner_last_name
from {{ ref('stg_events__fights') }} as f
left join {{ ref('stg_events') }} as e
    on f.event_id = e.event_id
left join {{ ref('stg_fighter_profiles') }} as fighter_1
    on f.fighter_1_id = fighter_1.fighter_id
left join {{ ref('stg_fighter_profiles') }} as fighter_2
    on f.fighter_2_id = fighter_2.fighter_id
