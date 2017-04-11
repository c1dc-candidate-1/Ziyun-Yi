# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 15:14:11 2017

@author: ziyunyi
"""
#Q1
def hmda_init():
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    loan_dataset=pd.read_csv('/Users/ziyunyi/Downloads/2012_to_2014_loans_data.csv')
    institution_dataset=pd.read_csv('/Users/ziyunyi/Downloads/2012_to_2014_institutions_data.csv')
    
    add_df1=institution_dataset[['As_of_Year','Agency_Code','Respondent_ID','Respondent_Name_TS']]
    add_df=add_df1.drop_duplicates(keep='first')
    merged=pd.merge(loan_dataset, add_df, left_on=['As_of_Year','Agency_Code','Respondent_ID'], 
                    right_on=['As_of_Year','Agency_Code','Respondent_ID'],how='left')
  
    x=list(merged['Loan_Amount_000'])
    low=0
    moderate=0
    high=0 
    level=[]
    super_high=0
    super_low=0
    for i in range(len(x)):
        if x[i]<=153 and x[i]>10:
            level.append('Low')
            low+=1
        elif x[i]<=10:
            level.append('Suepr_Low')
            super_low+=1
        elif x[i]>153 and x[i]<347:
            level.append('Moderate')
            moderate+=1
        elif x[i]>=347 and x[i]<10000:
            level.append('High')
            high+=1
        elif x[i]>=10000:
            level.append('Super_High')
            super_high+=1
    merged['Loan_Amount_Level']=level
    return merged

expanded_dataset=hmda_init()

def hmda_to_json(data,states='VA',c_c='Y'
                               ,path='/Users/ziyunyi/Downloads/test.json'):
    output_df=data[(data['State'] == states) 
          & (data['Conventional_Conforming_Flag']==c_c)]
    output_df.to_json(path,orient='index') 
    
hmda_to_json(expanded_dataset)

#Q2
#QA Loan_Amount_000
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

loan_dataset=pd.read_csv('/Users/ziyunyi/Downloads/2012_to_2014_loans_data.csv')
institution_dataset=pd.read_csv('/Users/ziyunyi/Downloads/2012_to_2014_institutions_data.csv')

#Missing values:
loan_dataset.isnull().sum()        
institution_dataset.isnull().sum()  #These two variables do not contain null values

amount=loan_dataset['Loan_Amount_000']

#To see if there is non-digit input:
def find_nonnum_input(x):
    ll=[]
    cnt=0
    for e in x:
        if str(e).isdigit()==False:
            ll.append(e)
            cnt+=1      
    print('There are '+str(cnt)+' non-numeric inputs.')
    print('They are:')
    print(ll)
find_nonnum_input(amount) #There is no non digit inputs.

#See descriptive statistics:   
loan_dataset['Loan_Amount_000'].describe() #1,153,235,347,99625
#Very widely ranged.

#See if there is outlier:
plt.boxplot(amount)
plt.ylim(0, 500)

plt.boxplot(amount)
plt.ylim(630, 650)
#Very long tail. (0,638). There are about 38983 points>638, seen as outliers.
#They take about 2.96% of total points.
#They can be removed in statistics. But I do not think they should be removed here. 
#Because they represent the rich people's loan.

#Distribution:
plt.hist(amount,bins=10000)
plt.xlim(0,1000)
#Right-skewed; non-normal distribution

#Normality test：
import scipy
import scipy.stats
scipy.stats.mstats.normaltest(amount)
scipy.stats.kstest(amount, cdf='norm')
scipy.stats.shapiro(amount)
#All three tests give non-normality result.

####QA Respondent_Name
#See if 'As_of_Year', 'Agency_Code' and 'Respondent_ID' determine 
#'Respondent_Name_TS' uniquely:
check_name=institution_dataset.groupby(['As_of_Year','Agency_Code', 'Respondent_ID'])['Respondent_Name_TS'].count().to_frame().reset_index()
cnt=0
for e in check_name['Respondent_Name_TS']:
    if e>1:
        cnt+=1
#cnt=0. So there is no duplicate 'Respondent_Name_TS' with same 'As_of_Year', 'Agency_Code', 'Respondent_ID'.
        
#Dig into those with same 'Respondent_ID' but different 'Respondent_Name_TS':
z=institution_dataset[['Respondent_ID','Respondent_Name_TS']]

d={}
for e in z['Respondent_ID']:
    u=z[z.Respondent_ID == e][[1]]['Respondent_Name_TS'].tolist()
    if len(set(u))!=1:
        d[e]=list(set(u))
#For example: ('22-3603829', ['ABSOLUTE HOME MORTGAGE CORPORA', 'ABSOLUTE HOME MORTGAGE CORP', 'AHMC'])
see=institution_dataset[institution_dataset['Respondent_ID']=='22-3603829']
#This ID corresponeds to three institutions in different locations in 3 successive years.
#They have similar names and two have same locations but I think they are actually 3 institutions.

#Frequency table:
name_freq=institution_dataset['Respondent_Name_TS'].value_counts()
name_freq=name_freq.sort_values(by='Respondent_Name_TS',ascending=False)
#'FIRST NATIONAL BANK' has most applications.


#Other variables' QA:
#'Applicant_Income_000' has a 'NA' input:
#income1=list(set(list(loan_dataset[['Applicant_Income_000']]['Applicant_Income_000'])))
income=loan_dataset['Applicant_Income_000']
find_nonnum_input(income)#There is 117853 non-digit inputs-‘NA‘.

income=[]
list=loan_dataset['Applicant_Income_000']
for e in list:
    if str(e).isdigit()==True:
        income.append(int(e))
income=pd.Series(income) 
income.describe() #0,6,94,142,9999

plt.boxplot(income)
plt.ylim(1, 500) 
   
#See if 'Sequence_Number' is unique given 'As_of_Year' and 'Respondent_ID':
seq=loan_dataset[['As_of_Year','Respondent_ID','Sequence_Number']]

def create_year_dict(x):
    seq_year=seq[seq['As_of_Year']==x]
    return {k: g["Sequence_Number"].tolist() for k,g in seq_year.groupby("Respondent_ID")}

seq_d_2012=create_year_dict(2012)
seq_d_2013=create_year_dict(2013)
seq_d_2014=create_year_dict(2014)

def find_dup_records(year,year_dic):
    for k in year_dic.keys():
        a=year_dic[k]
        vc = pd.Series(a).value_counts()
        x=vc[vc > 1].index.tolist()
        for i in range(len(x)):
            print (loan_dataset[(loan_dataset['Respondent_ID']==k) 
              &(loan_dataset['Sequence_Number']==x[i])&(loan_dataset['As_of_Year']==year)])

find_dup_records(2012,seq_d_2012)
find_dup_records(2013,seq_d_2013)
find_dup_records(2014,seq_d_2014)
#Only one Sequence ID was assigned wrongly to 2 applications only in the year 2013.   
       
#Q3
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
print(__version__) 

from plotly.graph_objs import *
import plotly as py
import plotly.graph_objs as go

def draw_q3_graph(y,var_name,yaxis_title):
    trace12=go.Bar(x=y[y['As_of_Year']==2012]['State'],y=y[y['As_of_Year']==2012][var_name],name='2012')
    trace22=go.Bar(x=y[y['As_of_Year']==2013]['State'],y=y[y['As_of_Year']==2013][var_name],name='2013')
    trace32=go.Bar(x=y[y['As_of_Year']==2014]['State'],y=y[y['As_of_Year']==2014][var_name],name='2014')
    data2=[trace12,trace22,trace32]
    py.offline.plot({
          "data": data2
         ,"layout": go.Layout(xaxis=XAxis(title='State'), 
             yaxis=YAxis(title=yaxis_title))})

#Draw Total Amnout bar chart:
x1=loan_dataset.groupby(['State','As_of_Year'])['Loan_Amount_000'].sum().to_frame().reset_index()
x=x1.sort_values(by='Loan_Amount_000',ascending=False)
draw_q3_graph(x,'Loan_Amount_000','Total Loan Amount 000')

#Draw total number of application bar chart:
y1=loan_dataset.groupby(['State','As_of_Year'])['Sequence_Number'].count().to_frame().reset_index()
y=y1.sort_values(by='Sequence_Number',ascending=False)
draw_q3_graph(y,'Sequence_Number','Total Number of Application')            
 
#Draw average amount bar chart:   
avg_amount=x1['Loan_Amount_000']/y1['Sequence_Number']
avg=x1[['State','As_of_Year']]
avg['avg_amount']=avg_amount
draw_q3_graph(avg,'avg_amount','Avg Amount 000')

#Total amount and number of apps both decreased a lot, but average amount increased
#a bit. I think we should not enter this market.


#Q4
def draw_total_amount_graph(state,Respondent_ID):
    sum=loan_dataset[(loan_dataset['State']==state)&(loan_dataset['Respondent_ID']==Respondent_ID)]
    mkt_sum=loan_dataset[(loan_dataset['State']==state)]
    y=sum.groupby(['As_of_Year'])['Loan_Amount_000'].sum().to_frame().reset_index()
    mkt_y=mkt_sum.groupby(['As_of_Year'])['Loan_Amount_000'].sum().to_frame().reset_index()
    text=['Market Share in %: ' + 
      str(e) for e in (y['Loan_Amount_000']/mkt_y['Loan_Amount_000']*100).tolist()]    
    trace1=go.Bar(x=y['As_of_Year'],y=y['Loan_Amount_000'],name=Respondent_ID,text=text)
    trace2=go.Bar(x=mkt_y['As_of_Year'],y=mkt_y['Loan_Amount_000'],name='Market' )    
    data=[trace1,trace2]
    py.offline.plot({'data':data
             ,'layout': go.Layout(xaxis=XAxis(title='Year'), 
             yaxis=YAxis(title='Total Loan Amount 000 in '+state))})
             
draw_total_amount_graph('WV','9731400737')
 
def draw_app_num_graph(state,Respondent_ID):
    sum=loan_dataset[(loan_dataset['State']==state)&(loan_dataset['Respondent_ID']==Respondent_ID)]
    mkt_sum=loan_dataset[(loan_dataset['State']==state)]
    y=sum.groupby(['As_of_Year'])['Sequence_Number'].count().to_frame().reset_index()
    mkt_y=mkt_sum.groupby(['As_of_Year'])['Sequence_Number'].count().to_frame().reset_index()
    text=['Market Share in %: ' + 
      str(e) for e in (y['Sequence_Number']/mkt_y['Sequence_Number']*100).tolist()]    
    trace1=go.Bar(x=y['As_of_Year'],y=y['Sequence_Number'],name=Respondent_ID,text=text)
    trace2=go.Bar(x=mkt_y['As_of_Year'],y=mkt_y['Sequence_Number'],name='Market' )    
    data=[trace1,trace2]
    
    py.offline.plot({'data':data
             ,'layout': go.Layout(xaxis=XAxis(title='Year'), 
             yaxis=YAxis(title='Total Number of Application in '+state))})
       
draw_app_num_graph('WV','9731400737')

#Interactive drawing:
#Run below in Jupyter notebook:  
from ipywidgets import interact
#interact(draw_total_amount_graph, state=["please choose one","VA", "DE","DC","MD",
#"WV"],Respondent_ID='0000000384')
def draw_graph(x,state,Respondent_ID):
    if x=='draw_app_num_graph':
        draw_app_num_graph(state,Respondent_ID)
    elif x=='draw_total_amount_graph':
        draw_total_amount_graph(state,Respondent_ID)

interact(draw_graph,x=['draw_app_num_graph','draw_total_amount_graph'],state=["please choose one","VA", "DE","DC","MD",
"WV"],Respondent_ID='9731400737')






