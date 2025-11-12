from datetime import datetime
import argparse
import json
import requests
import pandas as pd
import openpyxl
import os,sys, time

def logs_processor(logs, df):
    for event in logs:
        event_dict = json.loads(event)
        time = ''
        user = ''
        namespace = ''
        method = ''
        requestPath = ''
        message = ''
        peerCN = ''
        for key in event_dict:
            if key == 'time':
                time = event_dict[key]
            if key == 'user':
                user = event_dict[key]
            if key == 'namespace':
                namespace = event_dict[key]
            if key == 'method':
                method = event_dict[key]
            if key == 'req_path':
                requestPath = event_dict[key].split('?')[0]
            if key.endswith('user_message'):
                message = event_dict[key]
            if key == 'peer_CN':
                peerCN = event_dict[key]
        if not 'cdn_loadbalancer/metrics' in requestPath and not 'cdn_loadbalancer/access_logs' in requestPath:
            tmp = {'Time':time, 'User':user, 'Namespace':namespace, 'Method':method, 'Request Path':requestPath, 'Message':message, 'peerCN':peerCN }
            df_dictionary = pd.DataFrame([tmp])
            df = pd.concat([df, df_dictionary], ignore_index=True)
    return df

def get_audit_logs(token,tenant,namespace,hours):
    try:
        df = pd.DataFrame(columns = ['Time', 'User', 'Namespace', 'Method', 'Request Path', 'Message'])
        currentTime = datetime.now()
        midTime = int(round(datetime.timestamp(currentTime)))
        startTime = midTime - (hours*3600)
        print(f"Start to fetch audit logs for namespace {namespace}, please wait for some moments...")
        while True:
            endTime = midTime
            midTime = endTime - (24*3600)
            if hours < 24:
                midTime=startTime
            BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/audit_logs'.format(tenant,namespace)
            headers = {'Authorization': "APIToken {}".format(token)}
            auth_response = requests.post(BASE_URL, data=json.dumps({"aggs": {}, "end_time": "{}".format(endTime), "limit": 0, "namespace": "{}".format(namespace), "sort": "DESCENDING", "start_time": "{}".format(midTime),"scroll":True }), headers=headers)
            auditLogs = auth_response.json()
            if 'logs' in auditLogs:
                df = logs_processor(auditLogs['logs'], df)
                while (auditLogs["scroll_id"]!=""):
                    BASE_URL = 'https://{}.console.ves.volterra.io/api/data/namespaces/{}/audit_logs/scroll'.format(tenant,namespace)
                    auth_response = requests.post(BASE_URL, data=json.dumps({"namespace": "{}".format(namespace), "scroll_id": "{}".format(auditLogs["scroll_id"])}), headers=headers)
                    auditLogs = auth_response.json()
                    if 'logs' in auditLogs:
                        df = logs_processor(auditLogs['logs'], df)
            hours=hours-24
            print("Still processing logs, please wait for some moments...")
            if hours<24:
                break
        return df
    except Exception as e:
        print(f"An error occurred: {e}, and the error is {e.doc}")
        sys.exit()

def get_xc_namespaces(token,tenant):
    nsList = []
    BASE_URL = f'https://{tenant}.console.ves.volterra.io/api/web/namespaces'
    headers = {'Authorization': "APIToken {}".format(token)}
    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        sys.exit()
    else:
        json = response.json()
        jsonNsList = json['items']
        for ns in jsonNsList:
            nsList.append(ns["name"])
    return nsList

def main():
    nsList = []
    parser = argparse.ArgumentParser(description = "This *Python* script exports audit logs from *F5 Distributed Cloud* via the XC API into a Excel file.", epilog='The script generates a XLSX file named: f5-xc-audit_logs-<TENANT>-<date>.xlsx')
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--tenant', type=str, required=True)
    parser.add_argument('--namespace', type=str, required=True)
    parser.add_argument('--hours', type=int, required=True)
    args = parser.parse_args()
    currentTime = datetime.now()
        
    if args.namespace == 'ALL':
        fileName = f'f5-xc-audit_logs-{args.tenant}-ALL-{currentTime.strftime("%m-%d-%Y")}.xlsx'
        nsList = get_xc_namespaces(args.token,args.tenant)
    else:
        fileName = f'f5-xc-audit_logs-{args.tenant}-{args.namespace}-{currentTime.strftime("%m-%d-%Y")}.xlsx'
        nsList.append(args.namespace)

    with pd.ExcelWriter(fileName, engine='openpyxl') as writer:
        for ns in nsList:
            auditLogs = get_audit_logs(args.token,args.tenant,ns,args.hours)
            auditLogs.to_excel(writer, sheet_name=ns, index = False )
            time.sleep(5)  # To avoid hitting API rate limits
        print("The logs have been exported successfully for all namespaces, Please Check them")
        sys.exit()

if __name__ == "__main__":
   main()