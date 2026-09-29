import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta

rng = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]
raw = ROOT/'data'/'raw'
proc = ROOT/'data'/'processed'
out = ROOT/'outputs'

# ---------- Reference tables ----------
plans = pd.DataFrame([
    ['P1','Starter',29.0,3,'Individuals and very small teams'],
    ['P2','Pro',79.0,10,'Growing small businesses'],
    ['P3','Business',199.0,30,'Mid-market teams'],
    ['P4','Enterprise',499.0,100,'Large organizations'],
], columns=['plan_id','plan_name','monthly_price','included_seats','plan_description'])
plans.to_csv(raw/'plans.csv', index=False)

n=8000
customer_ids=[f'C{i:06d}' for i in range(1,n+1)]
segments = rng.choice(['SMB','Mid-Market','Enterprise'], n, p=[0.65,0.28,0.07])
channels = rng.choice(['Paid Search','Organic','Partner','Referral','Content','Outbound'], n, p=[0.24,0.23,0.12,0.15,0.16,0.10])
countries = rng.choice(['United States','United Kingdom','Canada','Germany','Australia','France','Netherlands','Ireland'], n,
                       p=[0.50,0.15,0.10,0.07,0.06,0.05,0.04,0.03])
industries = rng.choice(['Technology','Professional Services','Retail','Healthcare','Education','Manufacturing','Financial Services','Other'], n,
                        p=[0.22,0.17,0.14,0.10,0.10,0.09,0.08,0.10])

# Growing acquisition volume over time (Jan 2024 - Jul 2026)
months = pd.period_range('2024-01','2026-08',freq='M')
weights = np.linspace(0.7,1.5,len(months)); weights/=weights.sum()
start_months = rng.choice(months.astype(str), n, p=weights)
start_dates=[]
for sm in start_months:
    p=pd.Period(sm, freq='M')
    day=int(rng.integers(1, min(28,p.days_in_month)+1))
    start_dates.append(pd.Timestamp(p.start_time.year,p.start_time.month,day))
start_dates=pd.to_datetime(start_dates)

# Plan selection conditioned on segment
plan_name=[]
for s in segments:
    if s=='SMB':
        plan_name.append(rng.choice(['Starter','Pro','Business'],p=[0.56,0.39,0.05]))
    elif s=='Mid-Market':
        plan_name.append(rng.choice(['Pro','Business','Enterprise'],p=[0.27,0.61,0.12]))
    else:
        plan_name.append(rng.choice(['Business','Enterprise'],p=[0.25,0.75]))
plan_name=np.array(plan_name)
plan_map=dict(zip(plans.plan_name,plans.plan_id))
price_map=dict(zip(plans.plan_name,plans.monthly_price))
seat_map=dict(zip(plans.plan_name,plans.included_seats))
plan_ids=np.array([plan_map[x] for x in plan_name])

billing=[]
for s in segments:
    annual_p = {'SMB':0.22,'Mid-Market':0.40,'Enterprise':0.70}[s]
    billing.append('Annual' if rng.random()<annual_p else 'Monthly')
billing=np.array(billing)

# Latent customer characteristics used to create coherent behavior
engagement = np.clip(rng.beta(2.5,2.0,n),0.03,0.98)
support_burden = np.clip(rng.beta(1.5,5.0,n),0.01,0.95)
payment_risk = np.clip(rng.beta(1.2,10.0,n),0.005,0.8)

# Customer/company names intentionally synthetic
company_names=[f'Northstar Account {i:04d}' for i in range(1,n+1)]
customers=pd.DataFrame({
    'customer_id':customer_ids,
    'company_name':company_names,
    'country':countries,
    'industry':industries,
    'segment':segments,
    'acquisition_channel':channels,
    'signup_date':start_dates.date,
})
customers.to_csv(raw/'customers.csv', index=False)

# ---------- Simulate churn ----------
analysis_end=pd.Timestamp('2026-08-31')
churn_dates=[]
for i in range(n):
    current=pd.Timestamp(start_dates[i]).to_period('M')
    last=analysis_end.to_period('M')
    churn=None
    tenure=0
    while current<=last:
        tenure += 1
        # low engagement, high support burden, payment risk, monthly billing -> higher hazard
        hazard = 0.0035 + (1-engagement[i])*0.020 + support_burden[i]*0.010 + payment_risk[i]*0.020
        if billing[i]=='Monthly': hazard += 0.004
        if plan_name[i]=='Starter': hazard += 0.003
        if plan_name[i]=='Enterprise': hazard -= 0.003
        # first 2 months lower hazard; modest increase after long tenure
        if tenure <= 2: hazard *= 0.45
        if tenure >= 18: hazard += 0.002
        hazard=float(np.clip(hazard,0.001,0.075))
        if rng.random()<hazard:
            # churn mid/later in month
            day=int(rng.integers(5, min(28,current.days_in_month)+1))
            churn=pd.Timestamp(current.start_time.year,current.start_time.month,day)
            break
        current += 1
    churn_dates.append(churn)

# churn reasons
reasons=[]
for i,ch in enumerate(churn_dates):
    if ch is None:
        reasons.append(None); continue
    probs=np.array([0.30,0.18,0.16,0.12,0.10,0.06,0.08],float)
    labels=np.array(['Low engagement','Price','Missing feature','Payment issue','Support experience','Company closed','Other'])
    probs[0] += (1-engagement[i])*0.25
    probs[3] += payment_risk[i]*0.35
    probs[4] += support_burden[i]*0.30
    probs/=probs.sum()
    reasons.append(rng.choice(labels,p=probs))

status=np.array(['Churned' if d is not None else 'Active' for d in churn_dates])
monthly_price=np.array([price_map[x] for x in plan_name])
mrr=np.where(billing=='Annual',monthly_price*0.85,monthly_price)
subscriptions=pd.DataFrame({
    'subscription_id':[f'S{i:06d}' for i in range(1,n+1)],
    'customer_id':customer_ids,
    'plan_id':plan_ids,
    'start_date':start_dates.date,
    'billing_cycle':billing,
    'monthly_recurring_revenue':np.round(mrr,2),
    'status':status,
    'churn_date':[d.date() if d is not None else None for d in churn_dates],
    'cancellation_reason':reasons,
})
subscriptions.to_csv(raw/'subscriptions.csv', index=False)

# ---------- Monthly usage ----------
usage_rows=[]
for i,cid in enumerate(customer_ids):
    startp=start_dates[i].to_period('M')
    endp=(pd.Timestamp(churn_dates[i]).to_period('M') if churn_dates[i] is not None else analysis_end.to_period('M'))
    base_sessions={'Starter':22,'Pro':58,'Business':150,'Enterprise':390}[plan_name[i]]
    base_users={'Starter':2,'Pro':7,'Business':22,'Enterprise':70}[plan_name[i]]
    base_features={'Starter':3,'Pro':6,'Business':10,'Enterprise':14}[plan_name[i]]
    p=startp; tenure=0
    while p<=endp:
        tenure+=1
        months_to_churn = None if churn_dates[i] is None else (pd.Timestamp(churn_dates[i]).to_period('M') - p).n
        # gradual adoption early, mild organic growth, then decline before churn
        adoption=min(1.0,0.65+0.10*tenure)
        organic=1+0.008*min(tenure,18)
        decline=1.0
        if months_to_churn is not None:
            if months_to_churn==2: decline=0.82
            elif months_to_churn==1: decline=0.60
            elif months_to_churn==0: decline=0.38
        noise=max(0.45,rng.normal(1,0.12))
        sess=max(0,int(round(base_sessions*(0.35+1.05*engagement[i])*adoption*organic*decline*noise)))
        active=max(0,int(round(base_users*(0.45+0.85*engagement[i])*decline*max(0.65,rng.normal(1,0.08)))))
        features=max(1,int(round(base_features*(0.50+0.65*engagement[i])*decline*max(0.75,rng.normal(1,0.08)))))
        storage=round(max(0.1, active*({'Starter':0.5,'Pro':1.2,'Business':2.0,'Enterprise':3.0}[plan_name[i]])*max(0.6,rng.normal(1,0.15))),2)
        usage_rows.append([cid,str(p),sess,active,features,storage])
        p+=1
usage=pd.DataFrame(usage_rows,columns=['customer_id','usage_month','sessions','active_users','features_used','storage_gb'])
usage['usage_month']=pd.to_datetime(usage['usage_month']+'-01').dt.date
usage.to_csv(raw/'usage_monthly.csv', index=False)

# ---------- Support tickets ----------
ticket_rows=[]; tid=1
categories=['How-to','Bug','Billing','Integration','Feature request']
for i,cid in enumerate(customer_ids):
    startp=start_dates[i].to_period('M')
    endp=(pd.Timestamp(churn_dates[i]).to_period('M') if churn_dates[i] is not None else analysis_end.to_period('M'))
    p=startp
    while p<=endp:
        mtc=None if churn_dates[i] is None else (pd.Timestamp(churn_dates[i]).to_period('M')-p).n
        lam=0.05 + support_burden[i]*0.65
        if mtc is not None and mtc<=2: lam*=1.8
        count=int(rng.poisson(lam))
        for _ in range(count):
            day=int(rng.integers(1,min(28,p.days_in_month)+1))
            created=pd.Timestamp(p.start_time.year,p.start_time.month,day)
            cat=rng.choice(categories,p=[0.30,0.27,0.16,0.15,0.12])
            priority=rng.choice(['Low','Medium','High','Urgent'],p=[0.28,0.47,0.20,0.05])
            base_res={'Low':15,'Medium':20,'High':28,'Urgent':36}[priority]
            resolution=max(0.5, rng.gamma(shape=2, scale=base_res/2)*(0.85+support_burden[i]))
            csat=np.clip(5.1 - 0.055*resolution + rng.normal(0,0.65),1,5)
            ticket_rows.append([f'T{tid:07d}',cid,created.date(),cat,priority,round(resolution,2),round(csat,1)])
            tid+=1
        p+=1
support=pd.DataFrame(ticket_rows,columns=['ticket_id','customer_id','created_date','category','priority','resolution_hours','csat_score'])
support.to_csv(raw/'support_tickets.csv', index=False)

# ---------- Payments ----------
payment_rows=[]; pid=1
for i,cid in enumerate(customer_ids):
    start=pd.Timestamp(start_dates[i])
    end=pd.Timestamp(churn_dates[i]) if churn_dates[i] is not None else analysis_end
    if billing[i]=='Monthly':
        pay_months=pd.period_range(start.to_period('M'),end.to_period('M'),freq='M')
    else:
        # annual invoice at start and anniversaries
        dates=[]; d=start
        while d<=end:
            dates.append(d.to_period('M')); d=d+pd.DateOffset(years=1)
        pay_months=pd.PeriodIndex(dates, freq='M')
    for p in pay_months:
        day=min(start.day,28)
        paydate=pd.Timestamp(p.start_time.year,p.start_time.month,day)
        if billing[i]=='Monthly': amount=monthly_price[i]
        else: amount=monthly_price[i]*12*0.85
        fail_prob=0.008 + payment_risk[i]*0.18
        if churn_dates[i] is not None:
            mtc=(pd.Timestamp(churn_dates[i]).to_period('M')-p).n
            if mtc<=1: fail_prob += 0.11
        failed=rng.random()<min(fail_prob,0.45)
        payment_rows.append([f'PAY{pid:07d}',cid,paydate.date(),round(float(amount),2),'Failed' if failed else 'Paid',
                             rng.choice(['Card','ACH','Invoice'],p=[0.72,0.18,0.10])])
        pid+=1
payments=pd.DataFrame(payment_rows,columns=['payment_id','customer_id','payment_date','amount','payment_status','payment_method'])
payments.to_csv(raw/'payments.csv', index=False)

print('Raw dataset generated.')
