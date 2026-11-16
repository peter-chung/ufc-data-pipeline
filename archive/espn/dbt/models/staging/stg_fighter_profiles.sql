with source as (
  select * from {{source('raw', 'fighter_profiles')}}
),

renamed as (
  select
    id as fighter_id,
    first_name,
    last_name,
    nickname,
    gender,
    safe.parse_date('%m/%d/%Y', dob_raw) as date_of_birth,
    country,
    country_code,
    team,
    head_img,
    flag,
    stance,
    weight_class,
    weight_class_short,
    cast(regexp_extract(height, r"(\d+)'") as int64) * 12
      + cast(regexp_extract(height, r'(\d+)"') as int64) as height_inches,
    cast(regexp_extract(reach, r"(\d+(?:\.\d+)?)") as float64) as reach_inches,
    cast(regexp_extract(height_weight, r"(\d+) lbs") as int64) as weight_lbs,
    cast(split(record, '-')[safe_offset(0)] as int64) as wins,
    cast(split(record, '-')[safe_offset(1)] as int64) as losses,
    cast(split(record, '-')[safe_offset(2)] as int64) as draws,
    cast(split(tko_record, '-')[safe_offset(0)] as int64) as tko_wins,
    cast(split(tko_record, '-')[safe_offset(1)] as int64) as tko_losses,
    cast(split(sub_record, '-')[safe_offset(0)] as int64) as sub_wins,
    cast(split(sub_record, '-')[safe_offset(1)] as int64) as sub_losses,
    striking_history,
    striking_columns,
    clinch_history,
    clinch_columns,
    ground_history,
    ground_columns,
    cast(loaded_at as timestamp) as loaded_at
  from source
  qualify row_number() over (partition by fighter_id order by loaded_at desc) = 1
)

select * from renamed