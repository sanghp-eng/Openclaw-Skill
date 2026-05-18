import os
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from dotenv import load_dotenv

def rename_vm(vcenter_ip, user, password, current_name, new_name):
    context = ssl._create_unverified_context()
    try:
        si = SmartConnect(host=vcenter_ip, user=user, pwd=password, sslContext=context)
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        
        for vm in container.view:
            if vm.name == current_name:
                print(f"Renaming {current_name} to {new_name}...")
                task = vm.Rename_Task(new_name)
                # Wait for task completion
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    pass
                if task.info.state == vim.TaskInfo.State.success:
                    print("Success!")
                    return True
                else:
                    print(f"Failed: {task.info.error.msg}")
                    return False
        print(f"VM {current_name} not found.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'si' in locals():
            Disconnect(si)

if __name__ == "__main__":
    load_dotenv()
    rename_vm(
        os.getenv("VMWARE_VCENTER_IP"),
        os.getenv("VMWARE_USER"),
        os.getenv("VMWARE_PASS"),
        "win 2k22",
        "vm-2022-sanghp"
    )
