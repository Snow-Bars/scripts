#!/usr/bin/python3

from proxmoxer import ProxmoxAPI
import subprocess
import getpass

pve_ip = 'enter ip or DNS name here'
ha_group = 'enter ha-group you want to use for resources here'

passwd = getpass.getpass('root password is: ')
proxmox = ProxmoxAPI(pve_ip, user='root@pam', password=passwd, verify_ssl=False, service='PVE')
for node in proxmox.nodes.get(): #get list of all nodes in the cluster over PVE API
    if node['status'] == 'online': #check node is online
        for vm in proxmox.nodes(node['node']).qemu.get(): #get all VMs from every node
            if vm['status'] == 'running' or vm['status'] == 'stopped': #check VM status is started or stopped
                subprocess.run(["ha-manager", "add", "vm:" + vm['vmid'], "--group", ha_group, "--state", vm['status']]) #set VM HA-managed with curent state
