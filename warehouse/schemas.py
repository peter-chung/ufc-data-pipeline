from google.cloud import bigquery

UFCSTATS_FIGHTER_REF_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("link", "STRING"),
]

UFCSTATS_ROUND_STATS_SCHEMA = [
    bigquery.SchemaField("round", "INTEGER"),
    bigquery.SchemaField("knockdowns", "STRING"),
    bigquery.SchemaField("sig_str", "STRING"),
    bigquery.SchemaField("sig_str_pct", "STRING"),
    bigquery.SchemaField("total_str", "STRING"),
    bigquery.SchemaField("td", "STRING"),
    bigquery.SchemaField("td_pct", "STRING"),
    bigquery.SchemaField("sub_attempts", "STRING"),
    bigquery.SchemaField("reversals", "STRING"),
    bigquery.SchemaField("control_time", "STRING"),
    bigquery.SchemaField("head_str", "STRING"),
    bigquery.SchemaField("body_str", "STRING"),
    bigquery.SchemaField("leg_str", "STRING"),
    bigquery.SchemaField("distance_str", "STRING"),
    bigquery.SchemaField("clinch_str", "STRING"),
    bigquery.SchemaField("ground_str", "STRING"),
]

UFCSTATS_FIGHT_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("link", "STRING", mode="REQUIRED"),
    bigquery.SchemaField(
        "fighter_1", "RECORD", mode="REQUIRED", fields=UFCSTATS_FIGHTER_REF_SCHEMA
    ),
    bigquery.SchemaField(
        "fighter_2", "RECORD", mode="REQUIRED", fields=UFCSTATS_FIGHTER_REF_SCHEMA
    ),
    bigquery.SchemaField("weight_class", "STRING"),
    bigquery.SchemaField("method", "STRING"),
    bigquery.SchemaField("finish_round", "STRING"),
    bigquery.SchemaField("finish_time", "STRING"),
    bigquery.SchemaField("time_format", "STRING"),
    bigquery.SchemaField("referee", "STRING"),
    bigquery.SchemaField("details", "STRING"),
    bigquery.SchemaField("fighter_1_result", "STRING"),
    bigquery.SchemaField("fighter_2_result", "STRING"),
    bigquery.SchemaField(
        "fighter_1_stats", "RECORD", mode="REPEATED", fields=UFCSTATS_ROUND_STATS_SCHEMA
    ),
    bigquery.SchemaField(
        "fighter_2_stats", "RECORD", mode="REPEATED", fields=UFCSTATS_ROUND_STATS_SCHEMA
    ),
]

UFCSTATS_EVENT_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("link", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("date_raw", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("completed", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("location_raw", "STRING"),
    bigquery.SchemaField(
        "fights", "RECORD", mode="REPEATED", fields=UFCSTATS_FIGHT_SCHEMA
    ),
    bigquery.SchemaField("loaded_at", "STRING"),
]

UFCSTATS_FIGHT_HISTORY_ENTRY_SCHEMA = [
    bigquery.SchemaField("fight_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("fight_link", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("opponent_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("opponent_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("opponent_link", "STRING"),
    bigquery.SchemaField("event_name", "STRING"),
    bigquery.SchemaField("event_link", "STRING"),
    bigquery.SchemaField("event_date_raw", "STRING"),
    bigquery.SchemaField("result", "STRING"),
    bigquery.SchemaField("knockdowns", "STRING"),
    bigquery.SchemaField("sig_str", "STRING"),
    bigquery.SchemaField("td", "STRING"),
    bigquery.SchemaField("sub_attempts", "STRING"),
    bigquery.SchemaField("method", "STRING"),
    bigquery.SchemaField("method_detail", "STRING"),
    bigquery.SchemaField("finish_round", "STRING"),
    bigquery.SchemaField("finish_time", "STRING"),
]

UFCSTATS_FIGHTER_PROFILE_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("last_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("link", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("nickname", "STRING"),
    bigquery.SchemaField("height", "STRING"),
    bigquery.SchemaField("weight", "STRING"),
    bigquery.SchemaField("reach", "STRING"),
    bigquery.SchemaField("stance", "STRING"),
    bigquery.SchemaField("dob", "STRING"),
    bigquery.SchemaField("slpm", "STRING"),
    bigquery.SchemaField("str_acc", "STRING"),
    bigquery.SchemaField("sapm", "STRING"),
    bigquery.SchemaField("str_def", "STRING"),
    bigquery.SchemaField("td_avg", "STRING"),
    bigquery.SchemaField("td_acc", "STRING"),
    bigquery.SchemaField("td_def", "STRING"),
    bigquery.SchemaField("sub_avg", "STRING"),
    bigquery.SchemaField("career_record_raw", "STRING"),
    bigquery.SchemaField(
        "fight_history",
        "RECORD",
        mode="REPEATED",
        fields=UFCSTATS_FIGHT_HISTORY_ENTRY_SCHEMA,
    ),
    bigquery.SchemaField("loaded_at", "STRING"),
]
