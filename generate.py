
import argparse, json, yaml, random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os

def load_cfg(path): return yaml.safe_load(open(path))
def set_seeds(seed):
    random.seed(seed); np.random.seed(seed)

def sample_from(d): 
    keys=list(d.keys()); p=np.array(list(d.values()), float); p=p/p.sum(); 
    return np.random.choice(keys, p=p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--sessions", type=int)
    ap.add_argument("--users", type=int)
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()

    cfg = load_cfg(args.config); set_seeds(cfg["seed"])
    S = args.sessions or cfg["volume"]["sessions"]
    U = args.users or cfg["volume"]["users"]

    intents = list(cfg["intents"].keys())
    intent_p = np.array([cfg["intents"][k]["p"] for k in intents]); intent_p=intent_p/intent_p.sum()

    # Users
    users=[]
    for i in range(U):
        users.append(dict(
            user_id=f"U{i:06d}",
            age=int(np.clip(np.random.normal(28,9),13,75)),
            country=sample_from(cfg["countries"]),
            device=sample_from(cfg["devices"]),
            tenure_days=int(np.random.exponential(180))
        ))
    users_df=pd.DataFrame(users)

    # Dims
    dim_channel = pd.DataFrame({"channel_key":[1,2,3], "channel_name":["web","app","messenger"]})
    channel_to_key = dict(zip(dim_channel["channel_name"], dim_channel["channel_key"]))
    dim_intent = pd.DataFrame({"intent_key":range(1,len(intents)+1), "intent_name":intents, "category":[i.split('_')[0] for i in intents]})

    # Time sampling
    start = datetime.fromisoformat(cfg["time_window"]["start"])
    end   = datetime.fromisoformat(cfg["time_window"]["end"])
    dur = (end-start).total_seconds()
    start_times = [start + timedelta(seconds=float(np.random.uniform(0,dur))) for _ in range(S)]

    os.makedirs(args.outdir, exist_ok=True)
    lj=open(f"{args.outdir}/logs.jsonl","w",encoding="utf-8")

    turn_rows=[]; session_rows=[]; fiu_rows=[]
    for sid in range(1,S+1):
        user = users[np.random.randint(0,U)]
        session_id=f"S{sid:07d}"; t0=start_times[sid-1]
        channel = sample_from(cfg["channels"]); locale = sample_from(cfg["locales"])
        turns = np.random.geometric(cfg["session_turns"]["geom_p"]) + 2
        fallbacks=0; latency_sum=0
        intent_counts={k:0 for k in intents}; intent_fallbacks={k:0 for k in intents}

        for t in range(turns):
            intent = np.random.choice(intents, p=intent_p)
            a,b = cfg["intents"][intent]["beta"]
            conf = np.random.beta(a,b)
            fallback = int(conf<0.45 or np.random.rand()<0.02); fallbacks+=fallback
            mu,sig = cfg["latency_lognorm"]["mu"], cfg["latency_lognorm"]["sigma"]
            latency = int(np.random.lognormal(mu,sig) + (200 if channel=="messenger" else 0))
            latency_sum += latency

            event = dict(session_id=session_id, turn_id=t+1, ts=(t0+timedelta(seconds=6*t)).isoformat(),
                         user_id=user["user_id"], channel=channel, locale=locale,
                         intent=intent, confidence=round(float(conf),3),
                         fallback=fallback, latency_ms=latency, text=f"user asks about {intent}")
            lj.write(json.dumps(event)+"\n")
            turn_rows.append(event)
            intent_counts[intent]+=1; intent_fallbacks[intent]+=fallback

        resolved = int(fallbacks<2); avg_latency = latency_sum/turns; fb_rate=fallbacks/turns
        satisfaction = int(np.clip(round(3.6 + 1.2*((1-fb_rate)-0.6) - 1.1*fb_rate),1,5))
        time_key = int(t0.strftime("%Y%m%d"))
        session_rows.append(dict(session_id=session_id, user_id=user["user_id"],
                                 time_key=time_key, channel_key=channel_to_key[channel],
                                 turns_count=turns, avg_latency_ms=int(avg_latency),
                                 fallback_rate=round(fb_rate,3), resolved_flag=resolved,
                                 satisfaction_score=satisfaction))

        for k,cnt in intent_counts.items():
            if cnt>0:
                fiu_rows.append(dict(session_id=session_id,
                                     intent_key=int(dim_intent.loc[dim_intent.intent_name==k,"intent_key"].iloc[0]),
                                     intent_turns=cnt, intent_fallbacks=intent_fallbacks[k]))

    lj.close()

    # Build dims
    dim_time = pd.DataFrame(sorted(set([r["time_key"] for r in session_rows])), columns=["time_key"])
    dim_time["date"]=pd.to_datetime(dim_time["time_key"].astype(str))
    dim_time["year"]=dim_time["date"].dt.year; dim_time["month"]=dim_time["date"].dt.month
    dim_time["day"]=dim_time["date"].dt.day; dim_time["weekday"]=dim_time["date"].dt.weekday

    fact_conv = pd.DataFrame(session_rows)
    fact_intent = pd.DataFrame(fiu_rows)

    # Save STAR
    star_dir=f"{args.outdir}/star"; os.makedirs(star_dir, exist_ok=True)
    fact_conv.to_csv(f"{star_dir}/Fact_Conversation.csv", index=False)
    fact_intent.to_csv(f"{star_dir}/Fact_IntentUsage.csv", index=False)
    users_df.to_csv(f"{star_dir}/Dim_User.csv", index=False)
    dim_time.to_csv(f"{star_dir}/Dim_Time.csv", index=False)
    dim_intent.to_csv(f"{star_dir}/Dim_Intent.csv", index=False)
    dim_channel.to_csv(f"{star_dir}/Dim_Channel.csv", index=False)

    # Save SNOWFLAKE (normalize device)
    snow_dir=f"{args.outdir}/snowflake"; os.makedirs(snow_dir, exist_ok=True)
    dim_device = pd.DataFrame({"device_key":[1,2,3], "device":["Android","iOS","Desktop"]})
    user_sf = users_df.merge(dim_device, on="device", how="left").drop(columns=["device"]).rename(columns={"device_key":"device_key"})
    user_sf.to_csv(f"{snow_dir}/Dim_User.csv", index=False)
    dim_device.to_csv(f"{snow_dir}/Dim_Device.csv", index=False)
    dim_time.to_csv(f"{snow_dir}/Dim_Time.csv", index=False)
    dim_intent.to_csv(f"{snow_dir}/Dim_Intent.csv", index=False)
    dim_channel.to_csv(f"{snow_dir}/Dim_Channel.csv", index=False)
    fact_conv.to_csv(f"{snow_dir}/Fact_Conversation.csv", index=False)
    fact_intent.to_csv(f"{snow_dir}/Fact_IntentUsage.csv", index=False)

    # Summary
    stats = {
        "sessions": len(fact_conv),
        "avg_turns": float(fact_conv["turns_count"].mean()),
        "avg_latency_ms": float(fact_conv["avg_latency_ms"].mean()),
        "fallback_rate_mean": float(fact_conv["fallback_rate"].mean()),
        "satisfaction_mean": float(fact_conv["satisfaction_score"].mean())
    }
    with open(f"{args.outdir}/SUMMARY.json","w") as f: json.dump(stats,f,indent=2)

if __name__=="__main__":
    main()
