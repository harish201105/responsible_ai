Dataset Card: Chatbot Synthetic Dataset

Dataset Summary

This dataset contains synthetic chatbot conversation logs created for research on data modeling (raw logs vs. star schema vs. snowflake schema). It provides raw chat turns and structured fact/dimension tables.
All data is artificial, generated with Python scripts, and designed to mimic realistic chatbot interactions in terms of session length, intent distribution, latency, fallback rates, and user profiles.

⸻

Motivation
	•	Why synthetic? No public datasets met the need for comparing schema models in chatbot analytics.
	•	Advantages: Synthetic data allows precise control of distributions, scaling to millions of sessions, and avoids privacy risks.
	•	Research Objective: Evaluate how different schemas (raw, star, snowflake) affect query speed, scalability, and analytics usability.

⸻

Dataset Structure

Files Provided
	•	logs.json – raw unstructured chat logs (JSONL style).
	•	Fact_Conversation.csv – one row per session with aggregated metrics.
	•	Fact_IntentUsage.csv – per session × intent usage counts.
	•	Dim_User.csv – synthetic user demographics.
	•	Dim_Intent.csv – intent dictionary.
	•	Dim_Time.csv – date/time dimension.
	•	Dim_Channel.csv – channel dimension.

Schema Overview

Fact Tables

Table	Description
Fact_Conversation	Aggregated session-level metrics
Fact_IntentUsage	Intent usage counts per session

Dimension Tables

Table	Description
Dim_User	Age, country, device, tenure_days
Dim_Intent	Intent key, name, category
Dim_Time	Date, year, month, day, weekday
Dim_Channel	Channel key + name (web, app, messenger)


⸻

Generation Methodology
	•	Tools: Python 3.10+, numpy, pandas, scipy.stats, faker, pyyaml.
	•	Process:
	1.	User demographics generated with Faker + random sampling.
	2.	Sessions simulated with geometric distribution for turns.
	3.	Intents chosen from multinomial distribution with configurable probabilities.
	4.	Confidence values from Beta distributions (varies per intent).
	5.	Fallbacks triggered when confidence < threshold.
	6.	Latency sampled from lognormal distribution.
	7.	Satisfaction derived from fallback rate & confidence.
	•	Configuration: All parameters are stored in config.yaml for reproducibility.

⸻

Distributions and Properties
	•	Intents: order_status (22%), billing_issue (18%), technical_support (17%), plan_change (12%), product_info (12%), refund_request (9%), smalltalk (7%), escalation (3%).
	•	Latency: Lognormal μ=6.6, σ=0.35 → median ~735ms, mean ~950ms.
	•	Turns per Session: Geometric(p=0.18) + 2 → mean ~7–8 turns.
	•	Fallback Rate: Mean ~8%.
	•	User Age: Normal(28, 9), truncated 13–75.
	•	Devices: Android (55%), iOS (30%), Desktop (15%).

⸻

Validation
	•	Statistical checks: Ensured distributions matched configured targets.
	•	Session metrics: Avg ~7 turns/session, fallback ~8%, satisfaction ~3–4 stars.
	•	Quality metrics: Latency and fallback distributions were realistic and stable across runs.

⸻

Example Rows

Raw Log (JSON)

{
 "session_id": "S0001",
 "turn_id": 1,
 "ts": "2025-08-01T00:00:00",
 "user_id": "U004",
 "channel": "app",
 "intent": "order_status",
 "confidence": 0.751,
 "fallback": 0,
 "latency_ms": 1025,
 "text": "user asks about order_status"
}

Fact_Conversation (CSV)

session_id	user_id	channel	turns_count	avg_latency_ms	fallback_rate	resolved_flag	satisfaction_score
S0001	U004	app	4	748	0.0	1	3

Dim_User (CSV)

user_id	age	country	device	tenure_days
U000	32	IN	Android	163


⸻

Reproducibility
	•	Code: generate.py script included.
	•	Config: config.yaml stores all parameters (intents, distributions, error rates).
	•	Assumptions:
	•	Each session is one user.
	•	Confidence <0.45 triggers fallback.
	•	Messenger channel slower latency.
	•	How to regenerate:

python generate.py --sessions 1000 --users 500 --outdir output



