#!/usr/bin/env python3
import sys
import time
import os
import subprocess
import argparse
import requests
#import yaml

hostfile = ""
varsfile = ""

API_VERSION = 1

def check_env_vars():
    userid = os.environ.get('FYRE_USER_ID')
    key = os.environ.get('FYRE_API_KEY')
    if userid is None or key is None:
        print("Please set your env variables and rerun command: \n")
        print("export FYRE_USER_ID=<userid>")
        print("export FYRE_API_KEY=<api_key>")
        sys.exit()
    return userid, key

def get_cluster_info(cluster_name):
    userid,key = check_env_vars()
    base_url = f"https://api.fyre.ibm.com/rest/v{API_VERSION}/"
    headers = {'Content-type': 'application/json',
            'Accept': 'text/plain'}
    operation = f"?operation=query&request=showclusterdetails&cluster_name={cluster_name}"
    status_endpoint = base_url + operation
    response = requests.get(
            status_endpoint,
            verify=False,
            auth=(userid, key),
            headers=headers
            )
    publicips = []
    privateips = []
    try:
      for item in response.json()[cluster_name]:
          if item['publicip'] != "":
              publicips.append(item['publicip'])
          if item['privateip'] != "":
              privateips.append(item['privateip'])
    except:
        print(f"ERROR: {response.json()['details']}")
        print("\tAre you sure the clustername is correct?")
        sys.exit(1)
    return publicips[0], privateips


def build_host_file():
    global hostfile
    if 'LOGNAME' in os.environ:
        logname = os.environ['LOGNAME']
    else:
        print("Cannot get LOGNAME environment variable to create tmp directory for vars file.\n")
        sys.exit(1)

    tmpdir = f"/tmp/{logname}"
    
    try:
        os.makedirs(tmpdir, exist_ok=True)
    except:
        print(f"Cannot create {tmpdir}\n")
        sys.exit(1)

    hostfile = os.path.join(tmpdir, ".hosts.yml")
    with open(hostfile, "w+") as varsfn:
        varsfn.write("[Master]\n")
        varsfn.write(f"masternode ansible_ssh_host={privateips[1]}\n")
        varsfn.write("[Workers]\n")
        varsfn.write(f"workernode ansible_ssh_host={privateips[2]}\n")

def build_vars_file():
    global varsfile
    if 'LOGNAME' in os.environ:
        logname = os.environ['LOGNAME']
    else:
        print("Cannot get LOGNAME environment variable to create tmp directory for vars file.\n")
        sys.exit(1)

    tmpdir = f"/tmp/{logname}"
    try:
        os.makedirs(tmpdir, exist_ok=True)
    except:
        print(f"Cannot create {tmpdir}\n")
        sys.exit(1)

    varsfile = os.path.join(tmpdir, ".vars.yml")
    with open(varsfile, "w+") as varsfn:
        varsfn.write("---\n")
        varsfn.write(f"master_node_ip: \"{privateips[1]}\"\n")

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-clustername", type=str)
    args = parser.parse_args()
    publicips, privateips = get_cluster_info(args.clustername )

    build_vars_file()
    build_host_file()
    
    cmd = f'''ansible-playbook -i {hostfile}  --extra-vars "varsfile={varsfile}" K8s'''

    subprocess.call(cmd, shell=True)

    
        
