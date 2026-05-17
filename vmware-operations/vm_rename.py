
import traceback
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

# Credentials from .env
VCENTER_IP = "172.16.40.250"
USER = "opc@vsphere.local"
PASS = "Admin@123"
VM_OLD_NAME = "vm windows server 2022"
VM_NEW_NAME = "win 2k22"

def rename_vm():
    # Disable SSL certificate verification
    context = ssl._create_unverified_context()
    
    try:
        # Connect to vCenter
        si = SmartConnect(host=VCENTER_IP, user=USER, pwd=PASS, sslContext=context)
        
        # Find the VM by name
        content = si.RetrieveContent()
        vm = None
        
        # Search for the VM in the inventory
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for v in container.view:
            if v.name == VM_OLD_NAME:
                vm = v
                break
        
        if vm:
            print(f"Found VM: {vm.name}. Renaming to {VM_NEW_NAME}...")
            vm.Rename(VM_NEW_NAME)
            print("Rename successful!")
        else:
            print(f"VM '{VM_OLD_NAME}' not found.")
            
        Disconnect(si)
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    rename_vm()
