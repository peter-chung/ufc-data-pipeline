with source as (
    select * from {{ source('raw', 'ufcstats_events') }}
),

renamed as (
    select
        id as event_id,
        name as event_name,
        link as event_link,
        safe.parse_date('%B %d, %Y', date_raw) as event_date,
        completed,
        location_raw,
        fights,
        safe_cast(loaded_at as timestamp) as loaded_at
    from source
    qualify row_number() over (partition by event_id order by loaded_at desc) = 1
)

select * from renamed
