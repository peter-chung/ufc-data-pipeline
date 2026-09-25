from google.cloud import bigquery

STAT_VALUE_SCHEMA = [
    bigquery.SchemaField("abbreviation", "STRING"),
    bigquery.SchemaField("value", "STRING"),
]

STAT_COLUMN_SCHEMA = [
    bigquery.SchemaField("abbreviation", "STRING"),
    bigquery.SchemaField("name", "STRING"),
]

FIGHT_HISTORY_ROW_SCHEMA = [
    bigquery.SchemaField("date", "STRING"),
    bigquery.SchemaField("opponent_name", "STRING"),
    bigquery.SchemaField("opponent_link", "STRING"),
    bigquery.SchemaField("event_name", "STRING"),
    bigquery.SchemaField("event_link", "STRING"),
    bigquery.SchemaField("result", "STRING"),
    bigquery.SchemaField("stats", "RECORD", mode="REPEATED", fields=STAT_VALUE_SCHEMA),
]

FIGHTER_PROFILE_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("last_name", "STRING"),
    bigquery.SchemaField("nickname", "STRING"),
    bigquery.SchemaField("country", "STRING"),
    bigquery.SchemaField("country_code", "STRING"),
    bigquery.SchemaField("team", "STRING"),
    bigquery.SchemaField("head_img", "STRING"),
    bigquery.SchemaField("flag", "STRING"),
    bigquery.SchemaField("dob", "STRING"),
    bigquery.SchemaField("dob_raw", "STRING"),
    bigquery.SchemaField("gender", "STRING"),
    bigquery.SchemaField("height", "STRING"),
    bigquery.SchemaField("height_weight", "STRING"),
    bigquery.SchemaField("reach", "STRING"),
    bigquery.SchemaField("stance", "STRING"),
    bigquery.SchemaField("weight_class", "STRING"),
    bigquery.SchemaField("weight_class_short", "STRING"),
    bigquery.SchemaField("record", "STRING"),
    bigquery.SchemaField("tko_record", "STRING"),
    bigquery.SchemaField("sub_record", "STRING"),
    bigquery.SchemaField(
        "striking_history", "RECORD", mode="REPEATED", fields=FIGHT_HISTORY_ROW_SCHEMA
    ),
    bigquery.SchemaField(
        "striking_columns", "RECORD", mode="REPEATED", fields=STAT_COLUMN_SCHEMA
    ),
    bigquery.SchemaField(
        "clinch_history", "RECORD", mode="REPEATED", fields=FIGHT_HISTORY_ROW_SCHEMA
    ),
    bigquery.SchemaField(
        "clinch_columns", "RECORD", mode="REPEATED", fields=STAT_COLUMN_SCHEMA
    ),
    bigquery.SchemaField(
        "ground_history", "RECORD", mode="REPEATED", fields=FIGHT_HISTORY_ROW_SCHEMA
    ),
    bigquery.SchemaField(
        "ground_columns", "RECORD", mode="REPEATED", fields=STAT_COLUMN_SCHEMA
    ),
    bigquery.SchemaField("loaded_at", "STRING"),
]

FIGHTER_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("last_name", "STRING"),
    bigquery.SchemaField("country", "STRING"),
    bigquery.SchemaField("link", "STRING"),
    bigquery.SchemaField("flag", "STRING"),
    bigquery.SchemaField("gender", "STRING"),
    bigquery.SchemaField("head_img", "STRING"),
    bigquery.SchemaField("body_img", "STRING"),
    bigquery.SchemaField("height", "STRING"),
    bigquery.SchemaField("weight", "STRING"),
    bigquery.SchemaField("reach", "STRING"),
    bigquery.SchemaField("stance", "STRING"),
    bigquery.SchemaField("age", "INTEGER"),
    bigquery.SchemaField("record", "STRING"),
    bigquery.SchemaField("sig_str_lpm", "STRING"),
    bigquery.SchemaField("sig_str_acc", "STRING"),
    bigquery.SchemaField("td_avg", "STRING"),
    bigquery.SchemaField("td_acc", "STRING"),
    bigquery.SchemaField("sub_avg", "STRING"),
    bigquery.SchemaField("is_pre", "BOOLEAN"),
    bigquery.SchemaField("is_win", "BOOLEAN"),
]

FIGHT_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("fighter_1", "RECORD", mode="REQUIRED", fields=FIGHTER_SCHEMA),
    bigquery.SchemaField("fighter_2", "RECORD", mode="REQUIRED", fields=FIGHTER_SCHEMA),
    bigquery.SchemaField("card_segment", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("note", "STRING"),
    bigquery.SchemaField("date_time", "STRING"),
    bigquery.SchemaField("networks", "STRING"),
    bigquery.SchemaField("status", "STRING"),
]

VENUE_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("city", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("state", "STRING"),
    bigquery.SchemaField("address", "STRING"),
]

EVENT_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("link", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("date", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("status_detail", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("completed", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("is_postponed_or_canceled", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("venue", "RECORD", mode="REQUIRED", fields=VENUE_SCHEMA),
    bigquery.SchemaField("fights", "RECORD", mode="REPEATED", fields=FIGHT_SCHEMA),
    bigquery.SchemaField("short_name", "STRING"),
    bigquery.SchemaField("loaded_at", "STRING"),
]
