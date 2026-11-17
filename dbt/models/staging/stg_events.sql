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
        array(select trim(part) from unnest(split(location_raw, ',')) as part) as location_parts,
        fights,
        safe_cast(loaded_at as timestamp) as loaded_at
    from source
    qualify row_number() over (partition by event_id order by loaded_at desc) = 1
)

select
    event_id,
    event_name,
    event_link,
    event_date,
    completed,
    location_raw,
    location_parts[safe_offset(0)] as event_city,
    case
        when array_length(location_parts) = 3 then location_parts[safe_offset(1)]
    end as event_state,
    location_parts[safe_offset(array_length(location_parts) - 1)] as event_country,
    fights,
    loaded_at
from renamed
