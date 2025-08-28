# Synthetic Chatbot Dataset Project (v2)

Generates synthetic chatbot conversations and exports:
- Raw logs (JSONL)
- Star schema tables (CSV)
- Snowflake schema tables (normalized CSV)

## Quick start
```
python generate.py --sessions 100 --users 500
```
Outputs go to `./output`.


Chatbot Synthetic Dataset

1. Clear Documentation

This dataset is synthetic, meaning all chatbot conversations were generated artificially using scripts and statistical models.
	•	Why synthetic?
	•	No real-world chatbot log dataset was publicly available that fit the requirements for comparing raw logs, star schema, and snowflake schema in research.
	•	Using synthetic data allows us to control distributions (intents, fallbacks, latencies) and scale to the required size (10k–1M+ sessions) to properly stress test data models.
	•	Privacy and ethical concerns: real chatbot logs often contain sensitive information. Synthetic data avoids this issue.

⸻

2. Generation Methodology

Tools Used
	•	Language: Python (3.10+)
	•	Libraries: numpy, pandas, scipy.stats, faker, yaml, datetime

How Data Was Created
	1.	User Profiles: Generated with Faker + random sampling for age, country, device, tenure.
	2.	Session Creation: Sessions sampled from a non-homogeneous Poisson process to simulate realistic daily/weekly usage.
	3.	Conversation Turns: Number of turns sampled from a geometric distribution (avg ≈ 7 turns).
	4.	Intent Selection: Intents sampled from a multinomial distribution with configurable probabilities.
	5.	Confidence Scores: Drawn from Beta distributions (different per intent).
	6.	Fallbacks: Marked when confidence < threshold (0.45) + small random noise.
	7.	Latency: Sampled from a lognormal distribution (median ≈ 750 ms, mean ≈ 950 ms).
	8.	Sentiment & Satisfaction: Derived from fallback rate and confidence averages.
	9.	Outputs: Data exported in three formats:
	•	Raw Logs (JSONL): one line per conversation turn.
	•	Star Schema (CSV): fact + dimension tables.
	•	Snowflake Schema (CSV): normalized variant of star schema.

Data Distributions
	•	Intents: order_status (22%), billing_issue (18%), technical_support (17%), plan_change (12%), product_info (12%), refund_request (9%), smalltalk (7%), escalation (3%).
	•	Latency: Lognormal μ=6.6, σ=0.35 → median ≈ 735ms, mean ≈ 900–1050ms.
	•	Fallback Rate: Mean ≈ 5–10% depending on intent.
	•	Age: Normal(28, 9), truncated 13–75.
	•	Device: Android (55%), iOS (30%), Desktop (15%).

⸻

3. Validation Evidence

To ensure synthetic data is realistic and useful:
	•	Statistical Checks: Verified mean/variance of latency, fallback rates, and intent distributions matched the configured targets.
	•	Quality Metrics:
	•	Sessions: ~7 turns on average.
	•	Fallback rate ≈ 8%.
	•	Satisfaction scores centered around 3–4 (realistic spread).
	•	Research Objectives Fit: Dataset includes all the features needed for comparing analytics performance across schemas (fact tables, intent usage, user dimensions, time/channel breakdowns).

⸻

4. Reproducibility Elements
	•	Code Included: generate.py script with all logic for dataset generation.
	•	Configuration: config.yaml file stores all parameters (probabilities, distribution settings, error rates).
	•	Assumptions Documented:
	•	Each session represents one user.
	•	Confidence drives fallback probability.
	•	Latency varies by channel (messenger slower).
	•	How to Reproduce:

# Install dependencies
pip install numpy pandas scipy faker pyyaml

# Run generator (example: 1000 sessions, 500 users)
python generate.py --sessions 1000 --users 500 --outdir output



