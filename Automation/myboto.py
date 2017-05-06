import boto
import os
import time
from boto.ec2.regioninfo import RegionInfo

instances = []

def execute_command(command):
    os.system(command)

# create inventory file
def create_inventory(instances):
    with open("inventory", "w") as f:
        for i in range(len(instances)):
            while(instances[i].update() != "running"):
                time.sleep(5)
            f.write("node%s ansible_ssh_host=%s"%(i+1, instances[i].private_ip_address) + os.linesep)
        f.write("[all_servers]" + os.linesep)
        for i in range(len(instances)):
            f.write("node%s"%(i+1) + os.linesep)
        f.write("[all_servers:vars]" + os.linesep)
        f.write("ansible_ssh_user=ubuntu" + os.linesep)
        f.write("ansible_ssh_private_key_file=team25.key" + os.linesep)

def terminate_instances(id):
    ec2_conn.terminate_instances(id)

def create_instances(n_instance):
    for i in range(n_instance):
        reservations = ec2_conn.run_instances(image_id='ami-b549e714', placement='melbourne-np', key_name='team25', instance_type='m2.small', security_groups=['ssh'])
        instances.append(reservations.instances[0])

def show_reservations():
    reservations = ec2_conn.get_all_reservations()
    for idx, res in enumerate(reservations):
        print(idx, res.id, res.instances, res.name)

def show_volumns():
    curr_vols = ec2_conn.get_all_volumes()
    for v in curr_vols:
        print(v.id)
        print(v.status)
        print(v.zone)

def create_volumn():
    return ec2_conn.create_volume(50, "melbourne-np")

def attach_volumn(vol_id, istance_id):
    ec2_conn.attach_volume(vol_id, istance_id, "/dev/vdc")

def create_snapshot(vol_id):
    return ec2_conn.create_snapshot(vol_id, 'Mysnapshot')

region = RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
ec2_conn = boto.connect_ec2(aws_access_key_id='525b7076eb3b4d91929e573c44586d02', aws_secret_access_key='bb1e1c0798ca4a57872725dc0c8a27c7', \
                            is_secure=True, region=region, port=8773, path='/services/Cloud', validate_certs=False)

# read number of instances from input
n_instance = int(input('Enter number of instance to create: '))


# create n_instance instances
create_instances(n_instance)
create_inventory(instances)

new_vol = create_volumn()
attach_volumn(new_vol.id, instances[0].id)
create_snapshot(new_vol.id)
execute_command("ansible-playbook database.yml -i inventory -sudo")





