with source as (
    select * from {{ source('raw', 'events') }}
),

renamed as (
    select
        id as event_id,
        name as event_name,
        short_name,
        link as event_link,
        parse_timestamp('%Y-%m-%dT%H:%M%Ez', date) as event_date,
        status,
        status_detail,
        completed,
        is_postponed_or_canceled,
        venue,
        fights,
        safe_cast(loaded_at as timestamp) as loaded_at
    from source
    qualify row_number() over (partition by event_id order by loaded_at desc) = 1
)

select * from renamed
