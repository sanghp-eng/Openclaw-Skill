import os
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def get_env_var(key):
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith(key + '='):
                    return line.split('=')[1].strip()
    except Exception:
        return None
    return None

def update_vm_ram(vm_name, ram_mb):
    vcenter_ip = get_env_var("VMWARE_VCENTER_IP")
    user = get_env_var("VMWARE_USER")
    password = get_env_var("VMWARE_PASS")
    
    context = ssl._create_unverified_context()
    try:
        si = SmartConnect(host=vcenter_ip, user=user, pwd=password, sslContext=context)
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        
        vm = None
        for v in container.view:
            if v.name == vm_name:
                vm = v
                break
        
        if not vm:
            print(f"VM {vm_name} not found.")
            return False
        
        print(f"Found VM {vm_name}. Current RAM: {vm.config.hardware.memoryMB} MB")
        
        spec = vim.vm.ConfigSpec()
        spec.memoryMB = ram_mb
        
        print(f"Updating RAM to {ram_mb} MB...")
        task = vm.ReconfigVM_Task(spec=spec)
        
        # Wait for task to complete
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            continue
            
        if task.info.state == vim.TaskInfo.State.success:
            print(f"SUCCESS: Updated {vm_name} to {ram_mb} MB.")
            return True
        else:
            print(f"Error: {task.info.error.msg}")
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False
    finally:
        if 'si' in locals():
            Disconnect(si)

if __name__ == "__main__":
    update_vm_ram("vm01", 4096)
