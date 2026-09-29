import pandas as pd, numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/'data'/'raw'; proc=ROOT/'data'/'processed'; out=ROOT/'outputs'
analysis_end=pd.Timestamp('2026-08-31')
subs=pd.read_csv(raw/'subscriptions.csv', parse_dates=['start_date','churn_date'])
plans=pd.read_csv(raw/'plans.csv')
usage=pd.read_csv(raw/'usage_monthly.csv', parse_dates=['usage_month'])
support=pd.read_csv(raw/'support_tickets.csv', parse_dates=['created_date'])
payments=pd.read_csv(raw/'payments.csv', parse_dates=['payment_date'])

active=subs[subs.status=='Active']
current_mrr=active.monthly_recurring_revenue.sum(); arr=current_mrr*12
active_customers=active.customer_id.nunique(); churned=(subs.status=='Churned').sum(); n=len(subs)
overall_churn=churned/n; arpa=current_mrr/active_customers
aug_start=pd.Timestamp('2026-08-01'); aug_end=pd.Timestamp('2026-08-31')
active_at_aug=((subs.start_date<=aug_start)&(subs.churn_date.isna()|(subs.churn_date>=aug_start))).sum()
aug_churn=((subs.churn_date>=aug_start)&(subs.churn_date<=aug_end)).sum(); aug_churn_rate=aug_churn/active_at_aug
kpis=pd.DataFrame([
 ['Customers ever acquired',n,'count'],['Active customers at 2026-08-31',active_customers,'count'],['Total churned customers',churned,'count'],
 ['Current MRR',round(current_mrr,2),'USD'],['Current ARR',round(arr,2),'USD'],['Current ARPA',round(arpa,2),'USD/month'],
 ['Overall observed churn share',round(overall_churn,4),'rate'],['August 2026 logo churn rate',round(aug_churn_rate,4),'rate']],columns=['metric','value','unit'])
kpis.to_csv(out/'kpi_summary.csv',index=False)

planperf=subs.merge(plans[['plan_id','plan_name']],on='plan_id')
plan_summary=planperf.groupby('plan_name').agg(customers=('customer_id','nunique'),churned=('status',lambda s:(s=='Churned').sum()),avg_mrr=('monthly_recurring_revenue','mean')).reset_index()
plan_summary['churn_share']=(plan_summary.churned/plan_summary.customers).round(4); plan_summary['avg_mrr']=plan_summary.avg_mrr.round(2)
plan_summary.to_csv(out/'plan_performance.csv',index=False)

# Vectorized trailing-risk features
refs=subs[['customer_id','status','churn_date']].copy(); refs['reference_date']=refs.churn_date.fillna(analysis_end)
refs['reference_month']=refs.reference_date.dt.to_period('M').dt.to_timestamp()
refs['start_3m']=(refs.reference_date.dt.to_period('M')-2).dt.to_timestamp()

u=usage.merge(refs[['customer_id','reference_month','start_3m']],on='customer_id')
u=u[(u.usage_month>=u.start_3m)&(u.usage_month<=u.reference_month)].sort_values(['customer_id','usage_month'])
ug=u.groupby('customer_id').agg(avg_sessions_last_3m=('sessions','mean'),first_sessions=('sessions','first'),last_sessions=('sessions','last'),obs=('sessions','size')).reset_index()
ug['usage_change_last_3m']=np.where(ug.obs>=2,(ug.last_sessions-ug.first_sessions)/ug.first_sessions.clip(lower=1),0.0)
ug=ug[['customer_id','avg_sessions_last_3m','usage_change_last_3m']]

s=support.merge(refs[['customer_id','reference_date']],on='customer_id'); s=s[(s.created_date<=s.reference_date)&(s.created_date>=s.reference_date-pd.Timedelta(days=89))]
sg=s.groupby('customer_id').size().rename('tickets_last_90d').reset_index()
p=payments.merge(refs[['customer_id','reference_date']],on='customer_id'); p=p[(p.payment_date<=p.reference_date)&(p.payment_date>=p.reference_date-pd.Timedelta(days=89))]
pg=p.assign(failed=(p.payment_status=='Failed').astype(int)).groupby('customer_id').failed.sum().rename('failed_payments_last_90d').reset_index()

risk=refs[['customer_id','status']].merge(ug,on='customer_id',how='left').merge(sg,on='customer_id',how='left').merge(pg,on='customer_id',how='left')
risk['tickets_last_90d']=risk.tickets_last_90d.fillna(0).astype(int); risk['failed_payments_last_90d']=risk.failed_payments_last_90d.fillna(0).astype(int)
risk['avg_sessions_last_3m']=risk.avg_sessions_last_3m.round(2); risk['usage_change_last_3m']=risk.usage_change_last_3m.round(4)
risk.to_csv(proc/'customer_churn_features.csv',index=False)

risk['churned']=(risk.status=='Churned').astype(int)
risk['usage_trend_band']=pd.cut(risk.usage_change_last_3m,[-np.inf,-0.40,-0.15,0.15,np.inf],labels=['Severe decline','Moderate decline','Stable','Growing'])
risk['ticket_band']=pd.cut(risk.tickets_last_90d,[-1,0,1,3,999],labels=['0','1','2-3','4+'])
risk['payment_issue']=np.where(risk.failed_payments_last_90d>0,'Failed payment','No failed payment')
def summarize(c):
 x=risk.groupby(c,observed=False).agg(customers=('customer_id','count'),churn_rate=('churned','mean')).reset_index(); x['churn_rate']=x.churn_rate.round(4); return x
summarize('usage_trend_band').to_csv(out/'churn_by_usage_trend.csv',index=False)
summarize('ticket_band').to_csv(out/'churn_by_support_tickets.csv',index=False)
summarize('payment_issue').to_csv(out/'churn_by_payment_issue.csv',index=False)

# Monthly metrics
rows=[]
for per in pd.period_range('2024-01','2026-08',freq='M'):
 ms=per.start_time; me=per.end_time
 active_start=((subs.start_date<=ms)&(subs.churn_date.isna()|(subs.churn_date>=ms))).sum()
 new=((subs.start_date>=ms)&(subs.start_date<=me)).sum(); ch=((subs.churn_date>=ms)&(subs.churn_date<=me)).sum()
 mask=(subs.start_date<=me)&(subs.churn_date.isna()|(subs.churn_date>me)); active_end=mask.sum(); mrr=subs.loc[mask,'monthly_recurring_revenue'].sum()
 rows.append([per.strftime('%Y-%m'),active_start,new,ch,active_end,round(mrr,2),round(ch/active_start,4) if active_start else None])
monthly=pd.DataFrame(rows,columns=['month','active_start','new_customers','churned_customers','active_end','mrr_end','logo_churn_rate']); monthly.to_csv(out/'monthly_metrics.csv',index=False)

# Cohorts
rows=[]
for cohort in pd.period_range('2024-01','2026-07',freq='M'):
 cm=subs[subs.start_date.dt.to_period('M')==cohort]; size=len(cm)
 if not size: continue
 for age in range(13):
  pt=(cohort+age).end_time
  if pt>analysis_end: break
  ret=((cm.start_date<=pt)&(cm.churn_date.isna()|(cm.churn_date>pt))).sum()
  rows.append([cohort.strftime('%Y-%m'),age,size,ret,round(ret/size,4)])
pd.DataFrame(rows,columns=['signup_cohort','month_number','cohort_size','retained_customers','retention_rate']).to_csv(out/'cohort_retention.csv',index=False)

# Usage prior to churn
churn=subs[subs.churn_date.notna()][['customer_id','churn_date']]; u2=usage.merge(churn,on='customer_id')
u2['months_before_churn']=(u2.churn_date.dt.to_period('M')-u2.usage_month.dt.to_period('M')).apply(lambda x:x.n)
pre=u2[u2.months_before_churn.between(0,6)].groupby('months_before_churn').agg(avg_sessions=('sessions','mean'),avg_active_users=('active_users','mean'),customers=('customer_id','nunique')).reset_index().sort_values('months_before_churn',ascending=False)
pre[['avg_sessions','avg_active_users']]=pre[['avg_sessions','avg_active_users']].round(2); pre.to_csv(out/'usage_before_churn.csv',index=False)

print('ROW COUNTS', {'customers':len(pd.read_csv(raw/'customers.csv')),'subscriptions':len(subs),'usage':len(usage),'support_tickets':len(support),'payments':len(payments)})
print(kpis.to_string(index=False))
print('\nUSAGE\n', summarize('usage_trend_band').to_string(index=False))
print('\nPAYMENT\n', summarize('payment_issue').to_string(index=False))
print('\nTICKETS\n', summarize('ticket_band').to_string(index=False))
print('\nPLAN\n', plan_summary.to_string(index=False))
print('\nPRECHURN\n', pre.to_string(index=False))
