import os
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

def power_off_vm(vcenter_ip, user, password, vm_name):
    # Bypass SSL verification
    context = ssl._create_unverified_context()
    
    try:
        # Connect to vCenter
        si = SmartConnect(host=vcenter_ip, user=user, pwd=password, sslContext=context)
        
        # Search for the VM
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        
        for vm in container.view:
            if vm.name == vm_name:
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    print(f"VM {vm_name} is already powered off.")
                    return True
                
                print(f"Powering off {vm_name}...")
                task = vm.PowerOff()
                return True
                
        print(f"VM {vm_name} not found.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'si' in locals():
            Disconnect(si)

if __name__ == "__main__":
    # Load env
    env_file = "/home/sysadmin/.openclaw/workspace/.env"
    creds = {}
    with open(env_file) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k] = v
                
    success = power_off_vm(
        creds['VMWARE_VCENTER_IP'],
        creds['VMWARE_USER'],
        creds['VMWARE_PASS'],
        "vm01"
    )
    if success:
        exit(0)
    else:
        exit(1)
