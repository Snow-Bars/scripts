#!/usr/bin/python3

from proxmoxer import ProxmoxAPI
import subprocess
import getpass
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #ignore warnings while connecting to API

pve_ip = 'enter ip or DNS name here'
ha_group = 'enter ha-group you want to use for resources here'
passwd = getpass.getpass('root password is: ')
proxmox = ProxmoxAPI(pve_ip, user='root@pam', password=passwd, verify_ssl=False, service='PVE')

for node in proxmox.nodes.get(): #get list of all nodes in the cluster over PVE API
    if node['status'] == 'online': #check node is online
        for vm in proxmox.nodes(node['node']).qemu.get(): #get all VMs from every node
            if vm['status'] == 'running' or vm['status'] == 'stopped': #check VM status is started or stopped
                pci_dev = proxmox.nodes(node['node']).qemu(vm['vmid']).config.get() #get property of vm included pci passthrough divices
                ha_state = proxmox.nodes(node['node']).qemu(vm['vmid']).status.current.get() #get vm ha-managed status property
                if ('hostpci0' not in pci_dev) and (ha_state['ha']['managed'] != "0"): #check is vm have pci passthrough hardware in config and ha-managed status
                    subprocess.run(["ha-manager", "add", "vm:" + vm['vmid'], "--group", ha_group, "--state", vm['status']]) #set VM HA-managed with curent state
                elif 'hostpci0' in pci_dev:
                    print('VM ', vm['vmid'], "got at least 1 pce passthrough device", pci_dev['hostpci0'], "and can't be ha-managed") #print info if VMhave pci hardware
                elif ha_state['ha']['managed'] != "0":
                    print('VM ', vm['vmid'], 'is already ha-managed') #print if is already ha-manaaged
