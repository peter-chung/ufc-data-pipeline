with source as (
    select * from {{ source('raw', 'ufcstats_events') }}
    qualify row_number() over (partition by id order by loaded_at desc) = 1
),

unnested as (
    select
        source.id as event_id,
        fight,
        fight_order,
        (
            select s from unnest(fight.fighter_1_stats) as s
            where s.round is null limit 1
        ) as fighter_1_totals,
        (
            select s from unnest(fight.fighter_2_stats) as s
            where s.round is null limit 1
        ) as fighter_2_totals
    from source
    cross join unnest(fights) as fight with offset fight_order
),

fight_duration_parts as (
    select
        *,
        safe_cast(fight.finish_round as int64) as finish_round,
        array(
            select safe_cast(round_length as int64) * 60
            from unnest(split(regexp_extract(fight.time_format, r'\(([\d-]+)\)'), '-')) as round_length
        ) as round_lengths_seconds,
        time_diff(parse_time('%M:%S', fight.finish_time), time '00:00:00', second) as finish_time_elapsed_seconds
    from unnested
)

select
    fight.id as fight_id,
    event_id,
    fight_order,
    fight.fighter_1.id as fighter_1_id,
    fight.fighter_2.id as fighter_2_id,
    fight.weight_class,
    fight.method,
    case
        when fight.method in ('KO/TKO', "TKO - Doctor's Stoppage") then 'KO/TKO'
        when fight.method = 'Submission' then 'SUB'
        when fight.method in ('Decision - Unanimous', 'Decision - Split', 'Decision - Majority') then 'DEC'
        when fight.method = 'DQ' then 'DQ'
        when fight.method in ('Could Not Continue', 'Overturned') then 'NC'
        when fight.method = 'Other' then 'OTHER'
    end as method_category,
    fight.finish_time,
    finish_round,
    finish_time_elapsed_seconds,
    round_lengths_seconds,
    coalesce(
        (
            select sum(round_length)
            from unnest(round_lengths_seconds) as round_length with offset round_index
            where round_index < finish_round - 1
        ),
        0
    ) + finish_time_elapsed_seconds as fight_duration_seconds,
    fight.time_format,
    fight.referee,
    fight.details,
    fight.fighter_1_result,
    fight.fighter_2_result,

    safe_cast(fighter_1_totals.knockdowns as int64) as fighter_1_knockdowns,
    safe_cast(regexp_extract(fighter_1_totals.sig_str, r'^(\d+) of') as int64) as fighter_1_sig_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.sig_str, r'of (\d+)$') as int64) as fighter_1_sig_str_attempted,
    safe_cast(replace(fighter_1_totals.sig_str_pct, '%', '') as float64) as fighter_1_sig_str_pct,
    safe_cast(regexp_extract(fighter_1_totals.total_str, r'^(\d+) of') as int64) as fighter_1_total_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.total_str, r'of (\d+)$') as int64) as fighter_1_total_str_attempted,
    safe_cast(regexp_extract(fighter_1_totals.td, r'^(\d+) of') as int64) as fighter_1_td_landed,
    safe_cast(regexp_extract(fighter_1_totals.td, r'of (\d+)$') as int64) as fighter_1_td_attempted,
    safe_cast(replace(fighter_1_totals.td_pct, '%', '') as float64) as fighter_1_td_pct,
    safe_cast(fighter_1_totals.sub_attempts as int64) as fighter_1_sub_attempts,
    safe_cast(fighter_1_totals.reversals as int64) as fighter_1_reversals,
    safe_cast(split(fighter_1_totals.control_time, ':')[safe_offset(0)] as int64) * 60
        + safe_cast(split(fighter_1_totals.control_time, ':')[safe_offset(1)] as int64) as fighter_1_control_time_seconds,
    safe_cast(regexp_extract(fighter_1_totals.head_str, r'^(\d+) of') as int64) as fighter_1_head_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.head_str, r'of (\d+)$') as int64) as fighter_1_head_str_attempted,
    safe_cast(regexp_extract(fighter_1_totals.body_str, r'^(\d+) of') as int64) as fighter_1_body_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.body_str, r'of (\d+)$') as int64) as fighter_1_body_str_attempted,
    safe_cast(regexp_extract(fighter_1_totals.leg_str, r'^(\d+) of') as int64) as fighter_1_leg_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.leg_str, r'of (\d+)$') as int64) as fighter_1_leg_str_attempted,
    safe_cast(regexp_extract(fighter_1_totals.distance_str, r'^(\d+) of') as int64) as fighter_1_distance_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.distance_str, r'of (\d+)$') as int64) as fighter_1_distance_str_attempted,
    safe_cast(regexp_extract(fighter_1_totals.clinch_str, r'^(\d+) of') as int64) as fighter_1_clinch_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.clinch_str, r'of (\d+)$') as int64) as fighter_1_clinch_str_attempted,
    safe_cast(regexp_extract(fighter_1_totals.ground_str, r'^(\d+) of') as int64) as fighter_1_ground_str_landed,
    safe_cast(regexp_extract(fighter_1_totals.ground_str, r'of (\d+)$') as int64) as fighter_1_ground_str_attempted,

    safe_cast(fighter_2_totals.knockdowns as int64) as fighter_2_knockdowns,
    safe_cast(regexp_extract(fighter_2_totals.sig_str, r'^(\d+) of') as int64) as fighter_2_sig_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.sig_str, r'of (\d+)$') as int64) as fighter_2_sig_str_attempted,
    safe_cast(replace(fighter_2_totals.sig_str_pct, '%', '') as float64) as fighter_2_sig_str_pct,
    safe_cast(regexp_extract(fighter_2_totals.total_str, r'^(\d+) of') as int64) as fighter_2_total_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.total_str, r'of (\d+)$') as int64) as fighter_2_total_str_attempted,
    safe_cast(regexp_extract(fighter_2_totals.td, r'^(\d+) of') as int64) as fighter_2_td_landed,
    safe_cast(regexp_extract(fighter_2_totals.td, r'of (\d+)$') as int64) as fighter_2_td_attempted,
    safe_cast(replace(fighter_2_totals.td_pct, '%', '') as float64) as fighter_2_td_pct,
    safe_cast(fighter_2_totals.sub_attempts as int64) as fighter_2_sub_attempts,
    safe_cast(fighter_2_totals.reversals as int64) as fighter_2_reversals,
    safe_cast(split(fighter_2_totals.control_time, ':')[safe_offset(0)] as int64) * 60
        + safe_cast(split(fighter_2_totals.control_time, ':')[safe_offset(1)] as int64) as fighter_2_control_time_seconds,
    safe_cast(regexp_extract(fighter_2_totals.head_str, r'^(\d+) of') as int64) as fighter_2_head_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.head_str, r'of (\d+)$') as int64) as fighter_2_head_str_attempted,
    safe_cast(regexp_extract(fighter_2_totals.body_str, r'^(\d+) of') as int64) as fighter_2_body_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.body_str, r'of (\d+)$') as int64) as fighter_2_body_str_attempted,
    safe_cast(regexp_extract(fighter_2_totals.leg_str, r'^(\d+) of') as int64) as fighter_2_leg_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.leg_str, r'of (\d+)$') as int64) as fighter_2_leg_str_attempted,
    safe_cast(regexp_extract(fighter_2_totals.distance_str, r'^(\d+) of') as int64) as fighter_2_distance_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.distance_str, r'of (\d+)$') as int64) as fighter_2_distance_str_attempted,
    safe_cast(regexp_extract(fighter_2_totals.clinch_str, r'^(\d+) of') as int64) as fighter_2_clinch_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.clinch_str, r'of (\d+)$') as int64) as fighter_2_clinch_str_attempted,
    safe_cast(regexp_extract(fighter_2_totals.ground_str, r'^(\d+) of') as int64) as fighter_2_ground_str_landed,
    safe_cast(regexp_extract(fighter_2_totals.ground_str, r'of (\d+)$') as int64) as fighter_2_ground_str_attempted
from fight_duration_parts
