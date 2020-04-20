#include package
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize
import matplotlib.pyplot as plt

import pandas as pd

#pandasでCSVデータ読む。C:\Users\user\simulation\COVID-19\csse_covid_19_data\japan\test
data = pd.read_csv('COVID-19/csse_covid_19_data/japan/test/test_confirmed.csv')
data_r = pd.read_csv('COVID-19/csse_covid_19_data/japan/test/test_recovered.csv')
data_d = pd.read_csv('COVID-19/csse_covid_19_data/japan/test/test_deaths.csv')
    
confirmed = [0] * (len(data.columns) - 1)
day_confirmed = [0] * (len(data.columns) - 1)
confirmed_r = [0] * (len(data_r.columns) - 1)
day_confirmed_r = [0] * (len(data.columns) - 1)
confirmed_d = [0] * (len(data_d.columns) - 1)
diff_confirmed = [0] * (len(data.columns) - 1)
days_from_26_Mar_20 = np.arange(0, len(data.columns) - 1, 1)
days_from_26_Mar_20_ = np.arange(0, len(data.columns) - 1, 1)
beta_ = [0] * (len(data_r.columns) - 1)
gamma_ = [0] * (len(data_d.columns) - 1)

s0,s1=1,10000
city,city0 = "東京","tokyo"
#city,city0 = "大阪","oosaka" 
#city,city0 = "北海道","hokkaido"
#city = "愛知"
#city,city0 = "千葉","chiba" 
#city,city0 = "埼玉","saitama"
#city,city0 = "福岡","fukuoka"
#city,city0 = "兵庫","hyougo"
#city,city0 = "京都","kyoto"
#city,city0 = "神奈川","kanagawa"
city,city0 = "沖縄","okinawa"
city,city0 = "総計","total_japan"

skd=2 #2 #1 #4 #3 #2 #slopes average factor
#データを加工する
t_cases = 0
t_recover = 0
t_deaths = 0
for i in range(0, len(data_r), 1):
    if (data_r.iloc[i][0] == city): #for country/region
    #if (data_r.iloc[i][0] == city):  #for province:/state  
        print(str(data_r.iloc[i][0]))
        for day in range(1, len(data.columns), 1):            
            confirmed_r[day - 1] += data_r.iloc[i][day]
            if day < 1+skd:
                day_confirmed_r[day-1] += data_r.iloc[i][day]
            else:
                day_confirmed_r[day-1] += (data_r.iloc[i][day] - data_r.iloc[i][day-skd])/(skd)
        t_recover += data_r.iloc[i][day]        
for i in range(0, len(data_d), 1):
    if (data_d.iloc[i][0] == city): #for country/region
    #if (data_d.iloc[i][0] == city):  #for province:/state  
        print(str(data_d.iloc[i][0]))
        for day in range(1, len(data.columns), 1):
            confirmed_d[day - 1] += data_d.iloc[i][day] #fro drawings
        t_deaths += data_d.iloc[i][day]        
for i in range(0, len(data), 1):
    if (data.iloc[i][0] == city): #for country/region
    #if (data.iloc[i][0] == city):  #for province:/state  
        print(str(data.iloc[i][0]))
        for day in range(1, len(data.columns), 1):
            confirmed[day - 1] += data.iloc[i][day] -  confirmed_r[day - 1] -confirmed_d[day-1]
            diff_confirmed[day - 1] += confirmed[day-1] /  (confirmed_r[day - 1]+confirmed_d[day-1])
            if day == 1:
                day_confirmed[day-1] += data.iloc[i][day]
            else:
                day_confirmed[day-1] += data.iloc[i][day] - data.iloc[i][day-1]

tl_confirmed = 0
dlog_confirmed = [0] * (len(data.columns) - 1)
dlog_confirmed[0]=np.log(confirmed[0])
dlog_confirmed[1]=np.log(confirmed[1])-np.log(confirmed[0])
ratio_confirmed = [0] * (len(data.columns) - 1)
ratio_confirmed[0]=np.log(confirmed[0])
ratio_confirmed[1]=(confirmed[1]-confirmed[0]) #/(confirmed[0])
ratio_confirmed[2]=(confirmed[2]-confirmed[0])/2 #/(confirmed[0])/2

for i in range(skd, len(confirmed), 1):        
    if confirmed[i] > 0:    
        gamma_[i]=day_confirmed_r[i]/confirmed[i]
    else:
        continue
tl_confirmed = confirmed[len(confirmed)-1] + confirmed_r[len(confirmed)-1] + confirmed_d[len(confirmed)-1]
t_cases = tl_confirmed

t_max=len(confirmed)
dt=1
t=np.arange(0,t_max,dt)
t1=t

#function which estimate i from seir model func 
def estimate_i(ini_state,r0,a):
    est = r0*np.exp(a*t+0*t)
    return est

def y(params):
    est_i=estimate_i(ini_state,params[0],params[1])
    return np.sum((est_i-obs_i)*(est_i-obs_i))

def estimate_j(ini_state,r0,alpha):
    est = r0+alpha*(t)
    return est

def yj(params):
    est_i=estimate_j(ini_state,params[0],params[1])
    return np.sum((est_i-obs_i)*(est_i-obs_i))

obs_i = confirmed_r
r0=1
a = 1
start_day= len(days_from_26_Mar_20)-10
print("start_day",start_day)

ini_state=[4.34379478e+03, 3.64147576e-02]
#optimize logscale likelihood function
mnmz=minimize(y,ini_state,method="nelder-mead")
print(mnmz)
r0,a = mnmz.x[0],mnmz.x[1] #,mnmz.x[2]
est=estimate_i(ini_state,r0,a)

obs_i = day_confirmed
r0=1
a = 1
start_day= len(days_from_26_Mar_20)-10
print("start_day",start_day)

ini_state=[4.34379478e+03, 3.64147576e-02]
#optimize logscale likelihood function
mnmz=minimize(y,ini_state,method="nelder-mead")
print(mnmz)
r0,a = mnmz.x[0],mnmz.x[1] #,mnmz.x[2]
est_day=estimate_i(ini_state,r0,a)

t=np.arange(start_day,t_max,dt) #63
t2=t
obs_i = confirmed[start_day:] #63
r0_=1
alpha_ = 1
ini_state=[5.70579672, 0.00755685]
#optimize logscale likelihood function
mnmz=minimize(y,ini_state,method="nelder-mead")
print(mnmz)
r0_,alpha_ = mnmz.x[0],mnmz.x[1]
#est_confirmed=estimate_i(ini_state,r0_,alpha_)
#t=np.arange(63,100,dt)
t3=t
est_confirmed=estimate_i(ini_state,r0_,alpha_)

diff_est=[0] * (len(data.columns) - 1)
gamma_est=[0] * (len(data.columns) - 1)
R_est = [0] * (len(data_d.columns) - 1)
R_0 = [0] * (len(data_d.columns) - 1)
C = [0] * (len(data_d.columns) - 1)
for i in range(1,t_max):
    diff_est[i]=est[i]-est[i-1]
for i in range(0, len(confirmed), 1):        
    if confirmed[i] > 0 and diff_est[i] > 0:    
        gamma_est[i]=diff_est[i]/confirmed[i]
        R_est[i]= 1+day_confirmed[i]/diff_est[i] # diff_est=gamma*confirmed
        #R_0[i]= R_est[i]/(1-gamma_est[i]*R_est[i]*confirmed[i]*i/t_cases)
        #C[i]=gamma_est[i]*(R_est[i]-1)
        C[i] += day_confirmed[i]/confirmed[i]   #dI/dt/I
    else:
        continue

#matplotlib描画
fig, (ax1,ax2) = plt.subplots(2,1,figsize=(1.6180 * 4, 4*2))
#ax3 = ax1.twinx()
ax4 = ax2.twinx()

lns1=ax1.semilogy(days_from_26_Mar_20, confirmed, "o-", color="red",label = "cases")
lns8=ax1.semilogy(t3, est_confirmed, "-", color="black",label = "cases_r0_={:.2f}alpha_={:.2e}".format(r0_,alpha_))
lns2=ax1.semilogy(days_from_26_Mar_20, confirmed_r, "*-", color="green",label = "recovered+deaths")
#lns4=ax2.plot(days_from_22_Jan_20_, dlog_confirmed, "o-", color="blue",label = "dlog_confirmed")
#lns3=ax4.plot(days_from_22_Jan_20_, gamma_, "o-", color="black", zorder=1,label = "gamma")
lns3=ax4.plot(days_from_26_Mar_20_, gamma_est, "o-", color="black", zorder=1,label = "gamma_est")
#lns4=ax2.bar(days_from_22_Jan_20_, day_confirmed, zorder=2, label = "day_confirmed")
lns4=ax2.plot(days_from_26_Mar_20_, R_est, "o-", color="blue",label = "R_est")
lns5=ax1.semilogy(days_from_26_Mar_20_, diff_confirmed, ".-", color="black",label = "I/(R+D)")
lns6=ax1.semilogy(t1, est_day,"-", color="black", zorder=1, label = "est_r0={:.2f}alpha={:.2e}".format(r0,a))
#lns7=ax1.plot(t1, diff_est,"-", color="black", zorder=1, label = "diff_est_r0={:.2f}alpha={:.2e}".format(r0,a))
lns9=ax1.bar(days_from_26_Mar_20_, day_confirmed, label = "day_confirmed")
#lns10=ax2.plot(days_from_22_Jan_20_, R_0, "o-", color="red",label = "R_0")
lns4=ax2.plot(days_from_26_Mar_20_, C, "o-", color="red",label = "gamma*(R-1)")

lns_ax1 = lns1 +lns2 +lns5 + lns6 +lns8 
labs_ax1 = [l.get_label() for l in lns_ax1]
ax1.legend(lns_ax1, labs_ax1, loc=0)

lns_ax2 = lns3 #+lns9
labs_ax2 = [l.get_label() for l in lns_ax2]
ax4.legend(lns_ax2, labs_ax2, loc=0)
ax2.legend(loc=2)

ax1.set_title(city0 +" ; {} cases, {} recovered, {} deaths".format(t_cases,t_recover,t_deaths))
ax1.set_xlabel("days_from_26_Mar, 2020")
ax1.set_ylabel("casas, recovered ")
#ax2.set_ylabel("dlog_confirmed")
ax4.set_ylabel("gamma")
ax2.set_ylabel("day_confirmed_r, R")
ax4.set_ylim(0,0.04)
ax1.set_ylim(s0,s1) #0.1,1000
ax2.set_yscale('log')
#ax4.set_yscale('log')

#ax3.set_ylabel("deaths ")
#ax4.set_ylabel("deaths_rate %")
#ax4.set_ylim(-0.5,0.5)
ax1.grid()
ax2.grid()

plt.pause(1)
#city = "Tiwan"
plt.savefig('./fig/removed_{}_gamma_R_{}.png'.format(city,skd)) 
plt.close() 

t=np.arange(start_day,t_max,dt) #63
t4=t
obs_i = C[start_day:] #63
r0_=1
alpha_ = 1
ini_state=[1, 1]
#optimize logscale likelihood function
mnmz=minimize(yj,ini_state,method="nelder-mead")
print(mnmz)
r0_,alpha_ = mnmz.x[0],mnmz.x[1]
#t4=t
est_C = estimate_j(ini_state,r0_,alpha_)

t=np.arange(start_day,40,dt) #63
t4=t
est_C=estimate_j(ini_state,r0_,alpha_)

#matplotlib描画
fig, ax4 = plt.subplots(1,1,figsize=(1.6180 * 4, 4*1))

lns10=ax4.plot(days_from_26_Mar_20_, C, "o-", color="blue",label = "gamma*(R-1)")
lns11=ax4.plot(t4, est_C, ".-", color="black",label = "est_gamma*(R-1)")
ax4.legend(loc=2)

ax4.set_title(city0 +" ; {} cases, {} recovered, {} deaths".format(t_cases,t_recover,t_deaths))
ax4.set_xlabel("days_from_26,Mar, 2020")
ax4.set_ylabel("gamma*(R-1) ")
ax4.set_ylim(0,0.4)

ax4.grid()

plt.pause(1)
plt.savefig('./fig/removed_{}_gammaR_{}_II.png'.format(city,skd)) 
plt.close() 

t=np.arange(start_day,t_max,dt) #63
t2=t
obs_i = confirmed[start_day:]  #63
r0_=1
alpha_ = 1
ini_state=[5.70579672, 0.00755685]
#optimize logscale likelihood function
mnmz=minimize(y,ini_state,method="nelder-mead")
print(mnmz)
r0_,alpha_ = mnmz.x[0],mnmz.x[1]
#est_confirmed=estimate_i(ini_state,r0_,alpha_)
#t=np.arange(63,100,dt)
t3=t
est_confirmed=estimate_i(ini_state,r0_,alpha_)

t=np.arange(start_day,40,dt) #63
t3=t
est_confirmed=estimate_i(ini_state,r0_,alpha_)

#matplotlib描画
fig, ax3 = plt.subplots(1,1,figsize=(1.6180 * 4, 4*1))

lns1=ax3.semilogy(days_from_26_Mar_20, confirmed, "o-", color="red",label = "cases")
lns8=ax3.semilogy(t3, est_confirmed, "-", color="black",label = "cases_r0_={:.2f}alpha_={:.2e}".format(r0_,alpha_))
lns2=ax3.semilogy(days_from_26_Mar_20, confirmed_r, "*-", color="green",label = "recovered+deaths")
lns5=ax3.semilogy(days_from_26_Mar_20_, diff_confirmed, ".-", color="black",label = "I/(R+D)")
lns6=ax3.semilogy(t1, est,"-", color="black", zorder=1, label = "est_r0={:.2f}alpha={:.2e}".format(r0,a))

lns_ax1 = lns1 +lns2 +lns5 + lns6 +lns8
labs_ax1 = [l.get_label() for l in lns_ax1]
ax3.legend(lns_ax1, labs_ax1, loc=0)

ax3.set_title(city0 +" ; {} cases, {} recovered, {} deaths".format(t_cases,t_recover,t_deaths))
ax3.set_xlabel("days_from_26,Mar, 2020")
ax3.set_ylabel("casas, recovered ")
ax3.grid()

plt.pause(1)
plt.savefig('./fig/exterpolate_{}_gamma_R_{}.png'.format(city,skd)) 
plt.close() 

