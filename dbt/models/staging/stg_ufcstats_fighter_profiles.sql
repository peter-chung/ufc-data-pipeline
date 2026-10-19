with source as (
    select * from {{ source('raw', 'ufcstats_fighter_profiles') }}
),

renamed as (
    select
        id as fighter_id,
        first_name,
        last_name,
        link as fighter_link,
        nickname,
        cast(regexp_extract(height, r"(\d+)'") as int64) * 12
            + cast(regexp_extract(height, r'(\d+)"') as int64) as height_inches,
        cast(regexp_extract(weight, r'(\d+)') as int64) as weight_lbs,
        cast(regexp_extract(reach, r'(\d+(?:\.\d+)?)') as float64) as reach_inches,
        case when stance = '--' then null else stance end as stance,
        safe.parse_date('%b %d, %Y', dob) as date_of_birth,
        safe_cast(slpm as float64) as sig_str_landed_per_min,
        safe_cast(replace(str_acc, '%', '') as float64) as sig_str_acc_pct,
        safe_cast(sapm as float64) as sig_str_absorbed_per_min,
        safe_cast(replace(str_def, '%', '') as float64) as sig_str_def_pct,
        safe_cast(td_avg as float64) as td_avg_per_15min,
        safe_cast(replace(td_acc, '%', '') as float64) as td_acc_pct,
        safe_cast(replace(td_def, '%', '') as float64) as td_def_pct,
        safe_cast(sub_avg as float64) as sub_avg_per_15min,
        safe_cast(regexp_extract(career_record_raw, r'^(\d+)-') as int64) as wins,
        safe_cast(regexp_extract(career_record_raw, r'^\d+-(\d+)-') as int64) as losses,
        safe_cast(regexp_extract(career_record_raw, r'^\d+-\d+-(\d+)') as int64) as draws,
        coalesce(
            safe_cast(regexp_extract(career_record_raw, r'\((\d+)\s*NC\)') as int64), 0
        ) as no_contests,
        safe_cast(loaded_at as timestamp) as loaded_at
    from source
    qualify row_number() over (partition by fighter_id order by loaded_at desc) = 1
)

select * from renamed
