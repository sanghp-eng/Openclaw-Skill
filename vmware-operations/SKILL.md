---
name: vmware-operations
description: Operate VMware vSphere via REST API (VM creation, modification, deletion, network, storage, user management)
---

<!-- ui:visible=true -->
<!-- ui:label=VMware Operations -->
<!-- ui:icon=server -->

## Setup & Installation (Step-by-Step)

### Bước 1: Cài đặt Dependencies
Máy cần có Python 3 và các thư viện hỗ trợ SOAP/REST. Chạy lệnh sau:
```bash
pip install pyvmomi python-dotenv
```

### Bước 2: Khởi tạo Credential (.env)
Tại thư mục workspace (`~/.openclaw/workspace/`), tạo file `.env` để lưu thông tin vCenter:
```bash
cat <<EOF > ~/.openclaw/workspace/.env
VMWARE_VCENTER_IP=<your_vcenter_ip>
VMWARE_USER=<your_username>
VMWARE_PASS=<your_password>
EOF
```
*(Thay thông tin thật của Sếp vào)*.

### Bước 3: Kiểm tra kết nối vCenter
Thử lấy session ID xem thông tin đã đúng chưa:
```bash
curl -k -u "$VMWARE_USER:$VMWARE_PASS" -X POST "https://$VMWARE_VCENTER_IP/api/session"
```
Nếu nhận về session ID, chúc mừng Sếp đã thông vCenter! 💀


## General Workflow

1. **Authenticate to vCenter**
   - POST `https://{vcenter}/api/session` with username/password to obtain a session ID.
   - The response includes a `vmware-api-session-id` token.
   - Include this token in the header `vmware-api-session-id` for all subsequent API calls.

2. **Perform Desired Operation**
   - Use the appropriate REST endpoint for the task (VM, network, storage, etc.).
   - All requests are JSON-based; set `Content-Type: application/json`.
   - Handle standard VAPI error responses (error type, messages, data).

3. **Cleanup (Optional)**
   - DELETE `https://{vcenter}/api/session` to invalidate the session when done.

## Platform-Specific Notes

- **API Version**: vSphere Automation API (REST) available in vSphere 6.5+, aligns with vSphere 7.0 and 8.0.
- **Base URL**: `https://{vcenter}/api`
- **Authentication**: Session-based via `vmware-api-session-id` header.
- **Privileges**: Operations require specific privileges (e.g., `VirtualMachine.Inventory.Create`, `Resource.AssignVMToPool`).
- **Error Handling**: Standard VAPI error format with `messages` stack and `error_type`.
- **ID Format**: Most identifiers are strings (e.g., `vm-42`, `datastore-12`).
- **Concurrency**: The API is stateless per request; sessions are scalable.

## Common Guest OS Identifiers

Based on empirical testing in this environment, the following `guest_OS` values are known to be valid:

- Windows Server 2022: `WINDOWS_SERVER_2021`
- Ubuntu 64-bit: `UBUNTU_64`
- Windows Server 2019: `WINDOWS_SERVER_2019`

*Note: These identifiers may vary between vCenter versions and patch levels. Always verify the correct identifier for your target OS by inspecting an existing VM or consulting VMware documentation.*

## VM Operations

### Create a Virtual Machine
- **Endpoint**: `POST /api/vcenter/vm`
- **Required Parameters**:
  - `guest_OS`: Guest OS identifier (note: uppercase with underscores, e.g., `WINDOWS_SERVER_2019`, `UBUNTU_64`).
- **Optional Parameters**:
  - `name`: VM name (if omitted, server generates a name).
  - `placement`: Object specifying `folder`, `resource_pool`, `datastore`, `host` (if omitted, server attempts placement).
    - `folder`: Folder identifier where VM will be placed.
    - `resource_pool`: Resource pool identifier for VM.
    - `datastore`: Datastore identifier for VM home and disks.
    - `host`: Host identifier where VM will run.
  - `hardware_version`: Virtual hardware version (defaults to latest).
  - `boot`: Boot configuration.
  - `cpu`: CPU count.
  - `memory`: Memory size in MB.
  - `disks`: List of disk specifications (each disk requires `new_vmdk` for capacity and `datastore`).
  - `nics`: List of NIC specifications (each requires `backing` with `network` and `type`, and `adapter_type`).
  - `cdroms`, `floppies`, `serial_ports`, `parallel_ports`, `sata_adapters`, `scsi_adapters`, `nvme_adapters`.
  - `storage_policy`: Storage policy for VM home (vSphere 6.7+).
- **Success Response**: `201 Created` with VM identifier (string).
- **Common Errors**:
  - `400 Bad Request`: `InvalidArgument`, `Unsupported`, `ResourceInUse`, `AlreadyExists`.
  - `403 Forbidden`: Insufficient privileges.

### Get VM Information
- **Endpoint**: `GET /api/vcenter/vm/{vm_id}`
- **Response**: JSON object with VM details (name, power state, guest OS, hardware, etc.).

### Update VM Settings
- **Endpoint**: `PATCH /api/vcenter/vm/{vm_id}`
- **Updatable Fields**:
  - `name`
  - `boot`
  - `cpu`
  - `memory`
  - `disks` (add/reconfigure via sub-resources; direct replacement not supported)
  - *Note*: Some hardware changes require the VM to be powered off.
- **Success Response**: `204 No Content`.
- **⚠️ Critical Note**: In some vSphere 7.x/8.x environments, this REST endpoint may return `404 Not Found` for hardware updates or renaming. If this occurs, you **must** use the SOAP API via the `pyvmomi` library (see SOAP API section below).

### Rename a Virtual Machine
Since the REST API `PATCH` for renaming can be unreliable in certain vSphere 7.x environments (returning `404 Not Found`), the recommended way to rename a VM is via the SOAP API using `pyvmomi`.

- **Method**: Call `vm.Rename("new_name")` on the VirtualMachine object.
- **Reference Script**: Use `vm_rename.py` located in the skill folder.
- **Example Usage**:
  ```bash
  python3 ~/.openclaw/workspace/skills/vmware-operations/vm_rename.py
  ```
  *(Ensure you configure the target names in the script or modify it to accept arguments)*.

### Delete a Virtual Machine
- **Endpoint**: `DELETE /api/vcenter/vm/{vm_id}`
- **Prerequisites**: VM must be powered off (or use `force` parameter if supported).
- **Success Response**: `204 No Content`.

### VM Snapshots
- **List Snapshots**: `GET /api/vcenter/vm/{vm_id}/snapshots`
  - **Response**: Array of snapshot objects (each with `snapshot`, `name`, `description`, `create_time`, `state`).
- **Create Snapshot**: `POST /api/vcenter/vm/{vm_id}/snapshots`
  - **Request Body**:
    ```json
    {
      "name": "string",
      "description": "string" (optional),
      "memory": boolean (optional, default false),
      "quiesce": boolean (optional, default false)
    }
    ```
    - `memory`: Include memory in snapshot.
    - `quiesce`: Quiesce guest file system (requires VMware Tools).
  - **Success Response**: `201 Created` with snapshot identifier (string).
- **Delete Snapshot**: `DELETE /api/vcenter/vm/{vm_id}/snapshots/{snapshot_id}`
  - **Success Response**: `204 No Content`.
- **Restore to Snapshot**: `POST /api/vcenter/vm/{vm_id}/snapshots/{snapshot_id}/restore`
  - **Success Response**: `204 No Content` (task started).

### Power Operations

> **Critical Note for vSphere 7.x**: On many vSphere 7 installations, the REST API endpoints for power operations return `404 Not Found`. In these cases, you **must** use the SOAP API via the `pyvmomi` library.

#### REST API (Standard)
- **Power On**: `POST /api/vcenter/vm/{vm_id}/power/start`
- **Power Off**: `POST /api/vcenter/vm/{vm_id}/power/stop`
- **Suspend**: `POST /api/vcenter/vm/{vm_id}/power/suspend`
- **Reset**: `POST /api/vcenter/vm/{vm_id}/power/reset`
- **Success Response**: `204 No Content`.

#### SOAP API (via pyvmomi - Recommended for vSphere 7.x)
For environments where REST fails (Power operations or Hardware Config updates), use a Python script calling the following methods:
- **Power On**: `vm.PowerOn()`
- **Power Off**: `vm.PowerOff()`
- **Reset**: `vm.ResetVM_Task()`
- **Hardware Reconfig (RAM, CPU, etc.)**: Use `vim.vm.ConfigSpec` and `vm.ReconfigVM_Task(spec=spec)`.

**Reference Scripts in skill folder**:
- `vm_power_on.py`, `vm_power_off.py`, `vm_reset.py`
- `update_vm_ram.py` (Utility for updating VM memory)

## VM Network Operations

### List Networks
- **Endpoint**: `GET /api/vcenter/network`
- **Response**: Array of network objects (each with `network`, `name`, `type`).

### Add Network Adapter to VM
- **Method**: Update VM NICs via `PATCH /api/vcenter/vm/{vm_id}` or use dedicated NIC endpoints (if available).
- **Typical NIC Specification**:
  ```json
  {
    "network": "network-12",
    "adapter_type": "VMXNET3",
    "mac_address": "00:50:56:xx:xx:xx",
    "allow_guest_mac_change": false,
    "wake_on_lan_enabled": false
  }
  ```
- **Success Response**: `204 No Content`.

### Remove Network Adapter
- **Method**: Remove the NIC entry from the VM's NIC list and PATCH the VM.
- **Alternative**: Some APIs expose `DELETE /api/vcenter/vm/{vm_id}/nics/{nic_id}`.

## VM Storage Operations

### List Datastores
- **Endpoint**: `GET /api/vcenter/datastore`
- **Response**: Array of datastore objects (each with `datastore`, `name`, `capacity`, `free_space`, `type`).

### Add Disk to VM
- **Method**: Include disk specification in VM creation or reconfigure via `PATCH /api/vcenter/vm/{vm_id}` (if supported) or use dedicated disk endpoints.
- **Typical Disk Specification**:
  ```json
  {
    "capacity": 53687091200,
    "datastore": "datastore-12",
    "type": "THIN_PROVISIONED"
  }
  ```
- **Success Response**: `204 No Content`.

### Extend Disk
- **Method**: Update disk capacity via PATCH (if supported) or use storage policy APIs.

## User and Access Management

### Session Management (Authentication)
- **Create Session**: `POST /api/session`
  - **Request Body**: `{ "username": "<username>", "password": "<password>" }`
  - **Response**: `{ "value": "session-id-token" }` (the token is also returned in the `vmware-api-session-id` header).
- **Delete Session**: `DELETE /api/session`
  - **Header**: `vmware-api-session-id: <token>`
  - **Response**: `204 No Content`.

### Permission Management (via Authorization APIs)
*Note: The vSphere Automation API includes authorization services for managing roles and permissions.*
- **List Roles**: `GET /api/authorization/roles`
- **Create Role**: `POST /api/authorization/roles` with privileges list.
- **Assign Permission**: `POST /api/authorization/permissions` with subject (user/group), role, and propagation flag.
- **Update Permission**: `PATCH /api/authorization/permissions/{permission_id}`.
- **Delete Permission**: `DELETE /api/authorization/permissions/{permission_id}`.

### Tagging Operations
The vSphere Automation API includes tagging services for organizing inventory objects (VMs, hosts, datastores, etc.) with categories and tags.

#### List Tagging Categories
- **Endpoint**: `GET /api/cis/tagging/category`
- **Response**: Array of category objects (each with `category`, `name`, `description`, `cardinality`, `associable_types`).

#### Create Tagging Category
- **Endpoint**: `POST /api/cis/tagging/category`
- **Required Parameters**:
  - `name`: Display name of the category.
  - `description`: Description of the category.
  - `cardinality`: Associated cardinality (e.g., `SINGLE` or `MULTIPLE`).
  - `associable_types`: Array of object types to which this category's tags can be attached (e.g., `["VirtualMachine"]` for VMs).
- **Optional Parameter**:
  - `category_id`: If provided, use this identifier; otherwise server generates one.
- **Success Response**: `201 Created` with category identifier (string).

#### List Tags in a Category
- **Endpoint**: `GET /api/cis/tagging/tag?category_id={category_id}`
- **Response**: Array of tag objects (each with `tag`, `name`, `description`, `category_id`).

#### Create Tag
- **Endpoint**: `POST /api/cis/tagging/tag`
- **Required Parameters**:
  - `name`: Tag name.
  - `description`: Tag description.
  - `category_id`: Identifier of the category to which this tag belongs.
- **Success Response**: `201 Created` with tag identifier (string).

#### Attach Tag to an Object
- **Endpoint**: `POST /api/cis/tagging/tag-association`
- **Request Body**:
  ```json
  {
    "object_id": "string",
    "object_type": "string",
    "tag_id": "string"
  }
  ```
  - `object_id`: Identifier of the object to tag (e.g., `vm-42`).
  - `object_type`: Type of the object (e.g., `VirtualMachine`).
  - `tag_id`: Identifier of the tag to attach.
- **Success Response**: `204 No Content`.

#### Detach Tag from an Object
- **Endpoint**: `DELETE /api/cis/tagging/tag-association?object_id={object_id}&object_type={object_type}&tag_id={tag_id}`
- **Success Response**: `204 No Content`.

#### List Tags Attached to an Object
- **Endpoint**: `GET /api/cis/tagging/tag-association?object_ids={object_id}&object_types={object_type}`
- **Response**: Array of tag IDs attached to the object.

## Examples

### Authenticate and Create a VM
```bash
# 1. Obtain session
# Note: The session ID is returned as a raw quoted string in some API versions.
SESSION=$(curl -k -u <username>:<password> \
  -X POST "https://<vcenter_ip>/api/session" \
  -H "Content-Type: application/json" | tr -d '"')

# 2. Create VM
# Adjust guest_OS, name, placement, and hardware as needed.
# See 'Common Guest OS Identifiers' section for valid OS strings.
curl -k "https://vcenter.example.com/api/vcenter/vm" \
  -X POST \
  -H "vmware-api-session-id: $SESSION" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_OS": "WINDOWS_SERVER_2019",
    "name": "test-vm",
    "placement": {
      "folder": "group-v4",
      "resource_pool": "resgroup-2209",
      "datastore": "datastore-29"
    },
    "cpu": 2,
    "memory": 4096,
    "disks": [
      {
        "new_vmdk": {
          "capacity": 53687091200
        },
        "datastore": "datastore-12"
      }
    ],
    "nics": [
      {
        "backing": {
          "network": "network-12",
          "type": "DISTRIBUTED_PORTGROUP"
        },
        "adapter_type": "VMXNET3"
      }
    ]
  }'
```

### Power On a VM
```bash
curl -k "https://vcenter.example.com/api/vcenter/vm/vm-42/power/start" \
  -X POST \
  -H "vmware-api-session-id: $SESSION" \
  -H "Content-Type: application/json"
```

### Add a Disk to an Existing VM
```bash
# Assuming VM is powered off or supports hot-add
curl -k "https://vcenter.example.com/api/vcenter/vm/vm-42" \
  -X PATCH \
  -H "vmware-api-session-id: $SESSION" \
  -H "Content-Type: application/json" \
  -d '{
    "disks": [
      {"capacity": 107374182400, "datastore": "datastore-12", "type": "THIN_PROVISIONED"},
      {"capacity": 53687091200, "datastore": "datastore-12", "type": "THIN_PROVISIONED"}  # existing disk must be re-specified
    ]
  }'
```
## SOAP Examples (for vSphere 7.x Power Control)

Since vSphere 7.x often returns 404 for REST power operations, use the following Python approach.

> **Note for Skill Organization**: For skills that include executable scripts, store these script files in the same folder as this SKILL.md file (i.e., in `~/.openclaw/workspace/skills/vmware-operations/`). Reference implementations from this session are available as `vm_power_on.py`, `vm_power_off.py`, and `vm_reset.py` in this directory.

### Power Control Script Template
```python
import os
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def vm_power_action(vcenter_ip, user, password, vm_name, action="on"):
    context = ssl._create_unverified_context()
    try:
        si = SmartConnect(host=vcenter_ip, user=user, pwd=password, sslContext=context)
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        
        for vm in container.view:
            if vm.name == vm_name:
                if action == "on":
                    if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
                        vm.PowerOn()
                        print(f"Powering on {vm_name}...")
                elif action == "off":
                    if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                        vm.PowerOff()
                        print(f"Powering off {vm_name}...")
                elif action == "reset":
                    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                        vm.ResetVM_Task()
                        print(f"Resetting {vm_name}...")
                return True
        print(f"VM {vm_name} not found.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'si' in locals():
            Disconnect(si)

# Usage example
if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    vm_power_action(
        os.getenv("VMWARE_VCENTER_IP"),
        os.getenv("VMWARE_USER"),
        os.getenv("VMWARE_PASS"),
        "vm01",
        action="on"  # Change to "off" or "reset" as needed
    )
```

> **Usage**: Save the script as `vm_control.py` and run with `python3 vm_control.py`. Ensure `pyvmomi` and `python-dotenv` are installed:
> ```bash
> pip install pyvmomi python-dotenv
> ```

> **Note**: The `.env` file should contain:
> ```env
> VMWARE_VCENTER_IP=<your_vcenter_ip>
> VMWARE_USER=<your_username>
> VMWARE_PASS=<your_password>
> ```
