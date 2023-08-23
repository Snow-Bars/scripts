from proxmoxer import ProxmoxAPI
import time
import sys
import csv

proxmox = ProxmoxAPI(host="2pve10.rd.aorti.tech", user="tech-infr-script@ldap", password="6gzfZsBVc9Vnefd", verify_ssl=False, timeout=120)

INITIAL_NODE = sys.argv[1]
TESTS_NODE = ['2pve27','2pve28',]
PVE_NODES_INFO = dict()

# Блок при миграции, создание csv файла
if INITIAL_NODE != 'reverse':
    with open('VM-migrate.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Initial Node', 'VMID', 'Target Node'])
        for node in proxmox.nodes.get():
            if node['node'] in INITIAL_NODE:
                for vm in proxmox.nodes(node['node']).qemu.get():
                    vmid = vm['vmid']
                    writer.writerow([node['node'], vmid])

    #Пустой лист для vmid
    vms = []

    #Добавление vmid в лист vms
    with open('VM-migrate.csv', 'r') as f:
         reader = csv.reader(f, delimiter=';')
         next(reader)
         for row in reader:
             vms.append(row[1])

    #Функция для определения самой свободной ноды
    def get_node():
         for node in proxmox.nodes.get():
             if node['node'] not in TESTS_NODE and node['node'] != INITIAL_NODE:
                 used_mem = (node['mem'])
                 used_cpu = (node['cpu'])
                 PVE_NODES_INFO[node['node']] = {'used_mem': used_mem, 'used_cpu': used_cpu }
                 sorted_servers = sorted(PVE_NODES_INFO.items(), key=lambda x: (x[1]['used_mem'], x[1]['used_cpu']))
                 min_loaded_server = sorted_servers[0][0]
                 target_node = min_loaded_server
         return target_node

    #Создание листа смигрированных тачек
    migrated_vms = []

    #цикл для добавления vmid и ноды (куда уехала тачка)
    for vmid in vms:
        target_node = get_node()
        try: 
            migrate = proxmox.nodes(INITIAL_NODE).qemu(vmid).migrate.post(target=target_node, online=str(1))
            print(migrate)
            print('Таймаут 1 минута')
            time.sleep(60)
        except:
            target_node = 'Error'
        migrated_vms.append([vmid, target_node])

    #Запись результатов миграциив файл (откуда , что и куда уехало)
    with open('VM-migrate.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Initial Node', 'VMID', 'Target Node'])
        for vm in migrated_vms:
             writer.writerow([INITIAL_NODE, vm[0], vm[1]])
#Блок при обратной миграции
else:
    vms =[]

    with open('VM-migrate.csv', 'r') as f:
     reader = csv.reader(f, delimiter=';')
     next(reader)
     for row in reader:
         vms.append(row)

    for vmid in vms:
     target_node = vmid[0]
     if vmid[2] and vmid[2] != 'Error':
        try:
            migrate = proxmox.nodes(vmid[2]).qemu(vmid[1]).migrate.post(target=target_node, online=str(1))
            print(migrate)
            print('Таймаут 30 секунд')
            time.sleep(30)
        except KeyboardInterrupt: 
            exit(1)
        except:
            pass
