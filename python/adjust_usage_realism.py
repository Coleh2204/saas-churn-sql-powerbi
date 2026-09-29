import pandas as pd, numpy as np
from pathlib import Path
rng=np.random.default_rng(20260929)
root=Path(__file__).resolve().parents[1]
u=pd.read_csv(root/'data/raw/usage_monthly.csv',parse_dates=['usage_month'])
s=pd.read_csv(root/'data/raw/subscriptions.csv',parse_dates=['churn_date'])
# 28% of churners are non-usage-driven churn: restore most pre-churn decline.
churn=s[s.status=='Churned'].copy()
non_usage=set(rng.choice(churn.customer_id.to_numpy(), size=int(len(churn)*0.28), replace=False))
for cid in non_usage:
    cd=s.loc[s.customer_id.eq(cid),'churn_date'].iloc[0].to_period('M')
    idx=u.index[u.customer_id.eq(cid)]
    for j in idx:
        mb=(cd-u.at[j,'usage_month'].to_period('M')).n
        if mb==2: mult=1/0.82
        elif mb==1: mult=1/0.60
        elif mb==0: mult=1/0.38
        else: continue
        mult*=rng.uniform(0.88,1.08)
        u.at[j,'sessions']=int(round(u.at[j,'sessions']*mult))
        u.at[j,'active_users']=int(round(u.at[j,'active_users']*mult))
        u.at[j,'features_used']=max(1,int(round(u.at[j,'features_used']*min(mult,1.5))))
        u.at[j,'storage_gb']=round(u.at[j,'storage_gb']*mult,2)
# 10% of active customers experience a temporary recent slowdown without churning.
active=s[s.status=='Active'].customer_id.to_numpy()
slump=set(rng.choice(active,size=int(len(active)*0.10),replace=False))
for cid in slump:
    idx=u.index[u.customer_id.eq(cid)].tolist()
    if not idx: continue
    latest=u.loc[idx,'usage_month'].max().to_period('M')
    severity=rng.uniform(0.48,0.82)
    for j in idx:
        mb=(latest-u.at[j,'usage_month'].to_period('M')).n
        if mb==1: mult=(1+severity)/2
        elif mb==0: mult=severity
        else: continue
        u.at[j,'sessions']=int(round(u.at[j,'sessions']*mult))
        u.at[j,'active_users']=int(round(u.at[j,'active_users']*mult))
        u.at[j,'features_used']=max(1,int(round(u.at[j,'features_used']*max(mult,0.7))))
        u.at[j,'storage_gb']=round(u.at[j,'storage_gb']*mult,2)
u.to_csv(root/'data/raw/usage_monthly.csv',index=False,date_format='%Y-%m-%d')
print('adjusted',len(non_usage),'non-usage churners and',len(slump),'active slump customers')
