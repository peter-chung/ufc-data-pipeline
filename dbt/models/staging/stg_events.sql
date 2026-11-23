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
),

-- Event ids on ufcstats' upcoming-events page in the most recent snapshot.
upcoming_index as (
    select id as event_id, safe_cast(loaded_at as timestamp) as loaded_at
    from {{ source('raw', 'ufcstats_upcoming_index') }}
),

latest_upcoming_index as (
    select distinct event_id
    from upcoming_index
    where loaded_at = (select max(loaded_at) from upcoming_index)
),

latest_snapshot as (
    select max(loaded_at) as latest_snapshot_at from upcoming_index
)

select
    r.event_id,
    r.event_name,
    r.event_link,
    r.event_date,
    r.completed,
    case
        when r.completed then 'completed'
        -- Still in the future but missing from the latest snapshot of ufcstats'
        -- schedule. Conditions:
        -- * a snapshot exists (none before the first pipeline run that saves one)
        -- * the event was last loaded before that snapshot, so an event first
        --   seen in a run whose snapshot failed to save isn't misread as gone
        -- * past-dated events without results stay 'upcoming' (results not
        --   posted yet): ufcstats can drop an event from the upcoming page
        --   shortly before listing it as completed
        when s.latest_snapshot_at is not null
            and r.loaded_at < s.latest_snapshot_at
            and r.event_date > current_date()
            and l.event_id is null
            then 'cancelled'
        else 'upcoming'
    end as event_status,
    r.location_raw,
    r.location_parts[safe_offset(0)] as event_city,
    case
        when array_length(r.location_parts) = 3 then r.location_parts[safe_offset(1)]
    end as event_state,
    r.location_parts[safe_offset(array_length(r.location_parts) - 1)] as event_country,
    r.fights,
    r.loaded_at
from renamed as r
cross join latest_snapshot as s
left join latest_upcoming_index as l
    on r.event_id = l.event_id
