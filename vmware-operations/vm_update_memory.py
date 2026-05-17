import os
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def update_vm_memory(vcenter_ip, user, password, vm_name, memory_mb):
    # Bypass SSL verification
    context = ssl._create_unverified_context()
    
    try:
        # Connect to vCenter
        si = SmartConnect(host=vcenter_ip, user=user, pwd=password, sslContext=context)
        
        # Search for the VM
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        
        target_vm = None
        for vm in container.view:
            if vm.name == vm_name:
                target_vm = vm
                break
        
        if not target_vm:
            print(f"VM '{vm_name}' not found.")
            return False
        
        print(f"Found VM: {target_vm.name}")
        print(f"Current memory: {target_vm.config.hardware.memoryMB} MB")
        print(f"Power state: {target_vm.runtime.powerState}")
        
        # Determine if we need to power off
        was_powered_on = target_vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn
        if was_powered_on:
            print("VM is powered on. Powering off...")
            task = target_vm.PowerOffVM_Task()
            while task.info.state == vim.TaskInfo.State.running:
                pass
            if task.info.state != vim.TaskInfo.State.success:
                print(f"Failed to power off VM: {task.info.error}")
                return False
            print("VM powered off.")
        
        # Reconfigure VM memory using configSpec.memoryMB
        spec = vim.vm.ConfigSpec()
        spec.memoryMB = memory_mb
        print(f"Setting memory to {memory_mb} MB...")
        task = target_vm.ReconfigVM_Task(spec)
        while task.info.state == vim.TaskInfo.State.running:
            pass
        if task.info.state != vim.TaskInfo.State.success:
            print(f"Failed to update memory: {task.info.error}")
            return False
        print("Memory updated successfully.")
        
        # Power on the VM if it was originally on
        if was_powered_on:
            print("Powering on VM...")
            task = target_vm.PowerOnVM_Task()
            while task.info.state == vim.TaskInfo.State.running:
                pass
            if task.info.state != vim.TaskInfo.State.success:
                print(f"Failed to power on VM: {task.info.error}")
                return False
            print("VM powered on successfully.")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
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
                
    success = update_vm_memory(
        creds['VMWARE_VCENTER_IP'],
        creds['VMWARE_USER'],
        creds['VMWARE_PASS'],
        "vm01",
        8192  # 8 GB in MB
    )
    if success:
        exit(0)
    else:
        exit(1)