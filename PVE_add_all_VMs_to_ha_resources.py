#!/bin/python3

import os
import subprocess

#define HA group
group = "all_hosts"
#create lists of VMs and states
os.system("qm list | grep running | awk '{print $1}' | tail -n +1 > /opt/vmids_run")
running = open("/opt/vmids_run", "r").read().split("\n")
os.remove("/opt/vmids_run")
os.system("qm list | grep stopped | awk '{print $1}' | tail -n +1 > /opt/vmids_stop")
stopped = open("/opt/vmids_stop", "r").read().split("\n")
os.remove("/opt/vmids_stop")

#add VMs to HA resources state started
for vmid in running:
    if vmid != "" and vmid != 0:
        subprocess.run(["ha-manager", "add", "vm:" + vmid, "--group", group, "--state", "started"])
        subprocess.run(["echo", "vmid is", vmid])

#add VMs to HA resources state stopped
for vmid in stopped:
    if vmid != "" and vmid != 0:
        subprocess.run(["ha-manager", "add", "vm:" + vmid, "--group", group, "--state", "stopped"])
        subprocess.run(["echo", "vmid is", vmid])
