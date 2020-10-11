#!/usr/bin/env python
#coding: utf-8
#author: huange@enmonster.com

import requests
import json
import time
import sys
import re

emp_list= ['zhangsan', 'xiaohuang']
#emp_list= [x for x in reversed(emp_list)]
print(emp_list,'yuan shi zhi')
zhiban_start= {"zhangsan":"下午"}
zhiban_num_everyday= 2
dingapi= 'https://oapi.dingtalk.com/robot/send?access_token=xxxx'

dingmsg= {"msgtype": "text", "text": {"content": ""}, "isAtAll": False}
zhiban_start_record_file= '/home/next_zhiban.emp'
zhiban_time_record_file= '/home/zhiban_time.record'
try:
    with open(zhiban_start_record_file,'r') as next_zhiban_record:
        next_zhiban_emp= json.load(next_zhiban_record)
        if len(next_zhiban_emp) > 0:
            zhiban_start= next_zhiban_emp
        print("zhiban_record", next_zhiban_emp)
except Exception:
    pass
finally:
    print("next zhiban record1", zhiban_start)

try:
    with open(zhiban_time_record_file,'r') as zhiban_record:
        for line in zhiban_record.readlines():
            record_date= line.split(" ")[0]
            now_time= int(time.time())
            record_time= int(time.mktime(time.strptime("%s-%s-%s 06:06:06" %(record_date[0:4],record_date[4:6],record_date[6:8]),"%Y-%m-%d %H:%M:%S") ))
            print(now_time, record_time)
            next_zhiban_emp= line.split(' ')[2]
            if record_time > now_time:
                zhiban_start= {next_zhiban_emp.strip('\n'): line.split(' ')[1]}
                break
            else: 
                print('contiune')
                continue
            print("zhiban_record", next_zhiban_emp)
except Exception:
    pass
finally:
    print("next zhiban record2", zhiban_start)
#sys.exit() 

api_festival='http://pc.suishenyun.net/peacock/api/h5/festival'
headers= {'referer': 'Referer: http://yun.rili.cn/', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
festival_json= requests.get(api_festival,headers= headers).json()
festival_list= festival_json["national_holiday"]['cn']
#print(festival_list)
def senddd(msg):
    headers= {'Content-Type': 'application/json'}
    dingmsg['text']['content']= "值班排表如下(测试阶段，请以wiki为准):\n"+ str(msg)
    print(dingmsg)
    res= requests.post(dingapi,data= json.dumps(dingmsg), headers=headers)
    print(res.text)


def gen_zhiban_time_dict(emp=emp_list,zhiban_start=zhiban_start):
    zhiban_time_dict={}
    print("start gen dict #####################################")
    print('zhiban_start', zhiban_start)
    emp_x= [x for x in emp]
    for mem in reversed(emp_x):
        print('employ', mem)
        if mem in zhiban_start.keys():
            xtype= zhiban_start[mem]
            print(xtype,zhiban_start.keys())
            for mem_name in reversed(emp_list):
                zhiban_time_dict[mem_name]= xtype
                get_dtime= lambda x: "下午" if x== "上午" else "上午"
                xtype= get_dtime(xtype)
            print("generate.........", zhiban_time_dict)
            break
        else:
            last_one= emp_list.pop()
            emp_list.insert(0,last_one)
    print(emp_list,'zhiba-dict')
    print("END gen dict #####################################")
    return zhiban_time_dict

def day_to(num):
    date_now= time.strftime("%Y%m%d")
    return {time.strftime("%Y%m%d", time.localtime(time.time()+ 86400* num)): time.strftime("%u", time.localtime(time.time()+ 86400* num))} 

def get_zhiban_list(num=1):
    zhiban_member_list= []
    #print(emp_list,222222)
    for x in range(0,num):
        last_one= emp_list.pop()
        #print(emp_list,'aaaaa')
        emp_list.insert(0, last_one)
        #print(emp_list,33333)
        zhiban_member_list.append(last_one)
    if len(zhiban_member_list)== 1:
        return zhiban_member_list[0]
    return zhiban_member_list

future_7days= [day_to(num) for num in range(1,8)]
#print('未来7天：',str(future_7days))

weekends= []
for day in future_7days:
    for x,y in day.items():
        if y== "7" or y== "6":
            weekends.append(x)
#print("未来7天周末:", str(weekends))

hd_list=[]
sp_workday_list= []
for day in festival_list:
    year= day['date'][0:4]
    hd_start_date_re_list= re.findall('\d+',day['h'].split('-')[0])
    get_date= lambda x: x if len(x)== 2 else "0"+ x
    hd_start= year+ get_date(hd_start_date_re_list[0])+ get_date(hd_start_date_re_list[1])
    day_ts= time.mktime(time.strptime("%s-%s-%s 06:06:06" %(year,hd_start[4:6],hd_start[6:8]),
        "%Y-%m-%d %H:%M:%S") )
    #print(day['hn'])
    hd_hn= [x for x in range(0,day['hn'])]
    #print(hd_hn)
    for x in hd_hn:
        #print(x,day['hn'])
        hd_list.append(time.strftime("%Y%m%d", time.localtime(day_ts+ 86400* x)) )
    
    if len(day['w']) > 0:
        sp_workday_list_name= day['w'].split('、')
        for sday in sp_workday_list_name:
            sdate_re_list= re.findall('\d+',sday)
            sp_date= year+ get_date(sdate_re_list[0])+ get_date(sdate_re_list[1])
            sp_workday_list.append(sp_date)


#print("节日放假日期列表:", str(hd_list))
#print("特殊工作日期列表:", str(sp_workday_list))

nor_weekends=(list(set(weekends)- set(sp_workday_list)))
#print("周末放假日期列表：", nor_weekends)
all_hd_list= hd_list+ nor_weekends

#print("所有放假日期列表：", all_hd_list)

zhiban_time_dict= gen_zhiban_time_dict()
print("chu shi hua de dict", zhiban_time_dict)
#sys.exit()
#try:
#    with open(zhiban_time_dict_record_file,'r') as zhiban_time_dict_record:
#        zhiban_time_dict_tmp= json.load(zhiban_time_dict_record)
#        if len(zhiban_time_dict_tmp) > 0:
#            zhiban_time_dict= zhiban_time_dict_tmp
#except Exception:
#    zhiban_time_dict= gen_zhiban_time_dict()
#finally:
#    print(zhiban_time_dict,'sdfasdfasfasfs')
##         
zhiban_msg= []
for day in future_7days:
    for day_date,y in day.items():
        if day_date in all_hd_list:  ## 假日
            #print(day_date)
            zhiban_memb_list= get_zhiban_list(zhiban_num_everyday)
            print("huo qu zhiban ren shu hou",emp_list)
            print(day_date,"当日值班人：",zhiban_memb_list)
            for memb in zhiban_memb_list:
                xtype= zhiban_time_dict[memb]
                zhiban_msg.append({day_date: {xtype: memb}})
                print(day_date, xtype, memb)
                with open(zhiban_time_record_file, 'a+') as zhiban_record:
                    zhiban_record.writelines(day_date+" "+ xtype+" "+ memb+"\n")
print(str(zhiban_msg))
senddd(zhiban_msg)

#                r_dtime= lambda x: "下午" if x== "上午" else "上午"
#                xtype= r_dtime(xtype)
#                zhiban_time_dict[memb]= xtype
#            with open(zhiban_time_dict_record_file,'w+') as zhiban_time_dict_record:
#                json.dump(zhiban_time_dict, zhiban_time_dict_record, ensure_ascii=False)

print(emp_list,'zhiban hou xxxx')
next_zhiban= {emp_list[-1]: zhiban_time_dict[emp_list[-1]] }
print("下一轮第一个值班的人是：", next_zhiban)
with open(zhiban_start_record_file, "w+") as next_zhiban_record:
    json.dump(next_zhiban, next_zhiban_record, ensure_ascii= False)



