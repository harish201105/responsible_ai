# Schemas
## Star
Fact_Conversation(session_id PK, user_id FK, time_key FK, channel_key FK, turns_count, avg_latency_ms, fallback_rate, resolved_flag, satisfaction_score)
Fact_IntentUsage(session_id FK, intent_key FK, intent_turns, intent_fallbacks)
Dim_User(user_id PK, age, country, device, tenure_days)
Dim_Time(time_key PK, date, year, month, day, weekday)
Dim_Intent(intent_key PK, intent_name, category)
Dim_Channel(channel_key PK, channel_name)

## Snowflake (example)
Dim_User -> Dim_Device (device_key), country left as code
Dim_Intent -> Dim_IntentCategory (optional)
