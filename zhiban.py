#!/usr/bin/env python
#coding: utf-8
#author: huange@enmonster.com

import requests
import json
import time
import sys
import re
import os

emp_list= [{'张三': '下午'}, {'李四': '上午'}, {'王五': '下午'}, {'欧阳修': '上午'}, {'上官婷': '下午'}]

zb_num_everyday= 2
ztab_a_record_f= './ztab_a.ztb'
ztab_b_record_f= './ztab_b.ztb'
ztab_now_record_f= './ztab_now.ztb'
ztab_order_f= './ztab_order.ztb'

ddtoken= 'ddtoken'

api_festival='http://pc.suishenyun.net/peacock/api/h5/festival'
headers= {'referer': 'Referer: http://yun.rili.cn/', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
festival_json= requests.get(api_festival,headers= headers).json()
festival_list= festival_json["national_holiday"]['cn']

def senddd(msg,t):
    if t== "markdown":
        dingmsg= {
            "msgtype": t,
            "markdown": {
                "title":"值班信息",
                "text": ""
            },
             "at": {
                 "isAtAll": True
             }
        }
        dingmsg['markdown']['text']= "\
        \n# 值班信息：\
        \n#### (测试阶段，请以[WIKI](http://wiki.enmonster.com/pages/viewpage.action?pageId=86905344)为准！)\
        \n %s \
        \n> ![screenshot](https://obs-emcsapp-public.obs.cn-north-4.myhwclouds.com/image%%2Feditor%%2F0458b6e8-79ea-457a-87fc-66e7e1afc6b5.png)\
        \n" %msg
    else:
        dingmsg= {"msgtype": "text", "text": {"content": ""}, "isAtAll": True}
        dingmsg['text']['content']= "值班排表如下(测试阶段，请以wiki为准):\n"+ str(msg)
    dingapi= 'https://oapi.dingtalk.com/robot/send?access_token='+ ddtoken
    headers= {'Content-Type': 'application/json'}
    print(dingmsg)
    res= requests.post(dingapi,data= json.dumps(dingmsg), headers=headers)
    print(res.text)

def w_json_to_file(data, data_f):
#    print('w2222222')
    with open(data_f,"w+") as dt:
        json.dump(data, dt, ensure_ascii=False)
def r_json_from_file(data_f):
#    print('eeeeeee'+ data_f+ 'eeeeeeeee')
    if not os.path.exists(ztab_a_record_f): 
        w_json_to_file(emp_list,ztab_a_record_f)
    if not os.path.exists(data_f): 
#        print(data_f)
        w_json_to_file([],data_f)
#        print('w1111111111')
    with open(data_f,"r+") as dt:
        return json.load(dt)

def day_to(num):
    date_now= time.strftime("%Y%m%d")
    return {time.strftime("%Y%m%d", time.localtime(time.time()+ 86400* num)): time.strftime("%u", time.localtime(time.time()+ 86400* num))} 

def get_zhiban_list(num=1):
    ztab_a_record= r_json_from_file(ztab_a_record_f)
    ztab_b_record= r_json_from_file(ztab_b_record_f)
    zhiban_member_list= []
    get_dtime= lambda x: "下午" if x== "上午" else "上午"
    zb_list=[]
    f_stat_d= r_json_from_file(ztab_order_f)
    if len(f_stat_d) < 1:
        f_stat= 'a'
    else:
        f_stat= f_stat_d["start"]
    print(f_stat)
    change_stat= lambda x: "b" if x=='a' else "b"
    for x in range(0,num):
        new_one={}
        if f_stat== 'a':
            if len(ztab_a_record) < 1:
                f_stat= 'b'
            else:
                c_ztab= ztab_a_record
                o_ztab= ztab_b_record
        if f_stat== 'b':
            if len(ztab_b_record) < 1:
                f_stat= 'a'
                c_ztab= ztab_a_record
                o_ztab= ztab_b_record
            else:
                c_ztab= ztab_b_record
                o_ztab= ztab_a_record
        #else:
        #    print("值班表选取异常！")
        #    raise Exception
        ## 取值班人，并将
        last_one= c_ztab.pop()
        zb_list.append(last_one)
        new_one[list(last_one.keys())[0]]= get_dtime(list(last_one.values())[0])
        o_ztab.insert(0,new_one)
    w_json_to_file({'start': f_stat}, ztab_order_f)
    if f_stat== 'b':
        w_json_to_file(c_ztab, ztab_b_record_f)
        w_json_to_file(o_ztab, ztab_a_record_f)
    elif f_stat== 'a':
        w_json_to_file(c_ztab, ztab_a_record_f)
        w_json_to_file(o_ztab, ztab_b_record_f)
    else:
        print('异常了。。。。。')
        raise Exception
    print(c_ztab,o_ztab)
    return zb_list

##生成未来7天的日期，带周标记, exp: [{"20200101","1"}]
future_7days= [day_to(num) for num in range(1,8)]
print('未来7天：',str(future_7days))

##生成未来七天的周末列表, exp: ["20200101"]
weekends= []
for day in future_7days:
    for x,y in day.items():
        if y== "7" or y== "6":
            weekends.append(x)
#print("未来7天周末:", str(weekends))
#print(type(future_7days))

##生成节日日期列表, exp: ["20200101"]
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
##生成正常周末日期， exp: ["20200101"]
nor_weekends=(list(set(weekends)- set(sp_workday_list)))
#print("周末放假日期列表：", nor_weekends)
##生成所有放假日期， exp: ["20200101"]
all_hd_list= hd_list+ nor_weekends
#print("所有放假日期列表：", all_hd_list)

ztab_now_record= r_json_from_file(ztab_now_record_f)
day_cnt= 0
for day in future_7days:
    day_cnt+=1
    day_date= list(day.keys())[0]
    if len(ztab_now_record) > 0:
        ##清理过期值班数据：
        for item in ztab_now_record:
            print(int(list(item.keys())[0].split('_')[0]), int(day_date)- day_cnt)
            if int(list(item.keys())[0].split('_')[0]) < int(day_date)- day_cnt:
                ztab_now_record.remove(item)
        ## 若当天已经排过班，则跳过
        if day_date in [ list(x.keys())[0].split('_')[0] for x in ztab_now_record ]:
            print('下一个------')
            continue
    if day_date in all_hd_list:  ## 假日排班
        #print(day_date)
        ## 获取值班人列表
        zhiban_memb_list= get_zhiban_list(zb_num_everyday)
        print(day_date,"*******当日值班人*****：",zhiban_memb_list)
        for memb_d in zhiban_memb_list:
            dtime= memb_d[list(memb_d.keys())[0]]
            ztab_now_record.append({day_date+ "_"+ dtime: memb_d})
        ## 写入当前排班表(放上一个if内则保留上一次值班，放外层则只显示新的值班表。)
        w_json_to_file(ztab_now_record, ztab_now_record_f)


zhiban_source= r_json_from_file(ztab_now_record_f)
zhiban_msg=''
for item in zhiban_source:
    zhiban_msg+= "### "+ list(item.keys())[0]+ "："+ list(list(item.values())[0].keys())[0]+"\n"
print(zhiban_msg)
senddd(zhiban_msg,"markdown")
