---
name: switch-config
description: Configure network switches (Cisco IOS, Juniper EX/JunOS, ArubaOS-CX, Allied Telesis etc.) for access ports, VLANs, trunk ports, and basic Layer 2 settings. Use when the user wants to apply switch configuration commands via CLI.
---

# Switch Configuration Skill

This skill provides example CLI commands for configuring common Layer 2 features on network switches. It covers access ports, VLAN creation, trunk ports, and basic verification.

## Supported Platforms (examples)

- Cisco 3750G 48PS & WS-C2960X-24TS (Cisco IOS)
- Juniper EX Series (JunOS)
- Aruba 2930F-24G-4SFP (ArubaOS-Switch/ProVision)
- ArubaOS-CX
- Avaya 4548GT (Avaya ERS)
- Generic concepts applicable to many vendors

## Cisco 3750G 48PS & WS-C2960X-24TS Specific Notes

Both the Cisco 3750G 48PS and WS-C2960X-24TS run Cisco IOS. Use the standard Cisco IOS commands provided in this skill.

Key points:
- **Interface Type**: Gigabit Ethernet ports.
- **Cisco 3750G**: Supports PoE (PS model) and StackWise.
- **Cisco 2960X**: High-performance fixed-configuration switch, follows standard IOS syntax for VLANs and trunking.
- **Configuration**: VLAN and port configuration follow standard Cisco IOS syntax.

When configuring these specific models, you can use the Cisco IOS examples directly.

## General Workflow

1. **Identify switch OS** – ask the user which switch vendor/model/OS they are using.
2. **Verify login and mode** – ensure the user has successfully logged in and is in the appropriate mode:
   - For most configuration changes, you need to be in **Privileged EXEC mode** (enable mode). If not, enter `enable` and provide the password if required.
   - For interface or VLAN configuration, you need to be in **Global Configuration mode**. Enter `configure terminal` (or `configure`) from privileged EXEC mode.
   - Some platform-specific modes (e.g., interface configuration, VLAN configuration) are entered from global configuration mode as needed.
3. **Enter configuration mode** – varies per platform (e.g., `configure terminal` for Cisco IOS, `configure` for JunOS/ArubaOS-CX).
4. **Apply configuration** – use the appropriate commands for the task.
5. **Verify** – show commands to confirm the configuration.

## Cisco Legacy SSH Configuration (Old Protocol Support)

For legacy Cisco switches that require obsolete SSH v1.5 or insecure cryptographic suites (e.g., SI-PRD-SW-Cluster3), standard `ssh` commands will fail. Use the following robust pattern:

### Legacy SSH Execution Pattern
```bash
printf "enable\n<ENABLE_PASSWORD>\nconfigure terminal\ninterface <INTERFACE>\n<COMMAND>\nend\nwrite memory\n" | sshpass -p '<LOGIN_PASSWORD>' ssh -tt \
  -o KexAlgorithms=+diffie-hellman-group14-sha1 \
  -o HostKeyAlgorithms=+ssh-rsa \
  -o Ciphers=aes128-cbc,3des-cbc,aes192-cbc,aes256-cbc \
  -o ConnectTimeout=10 \
  -o StrictHostKeyChecking=no \
  <USER>@<IP>
```

**Key components:**
1. **`sshpass`**: Automates the login password.
2. **`-tt`**: Forces pseudo-terminal allocation (essential for switches to accept interactive-like configuration commands).
3. **`KexAlgorithms` / `HostKeyAlgorithms` / `Ciphers`**: Injects legacy cryptography required by outdated Cisco IOS versions.
4. **`printf` pipe**: Sequences the commands (login -> enable -> config) reliably.


### Enter global configuration mode
```
configure terminal
```

### Create a VLAN (if not exists)
```
vlan 10
 name SALES
 exit
```

### Configure an access port
```
interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
 exit
```

### Configure a trunk port
```
interface GigabitEthernet1/0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport trunk native vlan 99
 spanning-tree portfast trunk
 no shutdown
 exit
```

### Modify allowed VLANs on an existing trunk
```
interface GigabitEthernet1/0/24
 switchport trunk allowed vlan add 40
```

### Remove a VLAN from trunk
```
interface GigabitEthernet1/0/24
 switchport trunk allowed vlan remove 20
```

### Configure port description
```
interface GigabitEthernet1/0/1
 description Link to Server Room
 exit
```

### Configure interface speed and duplex
```
interface GigabitEthernet1/0/1
 speed 100
 duplex full
 exit
```

### Enable port security (limit MAC addresses)
```
interface GigabitEthernet1/0/1
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit
```

### Configure EtherChannel (LACP)
```
interface range GigabitEthernet1/0/1 - 2
 channel-group 1 mode active
 exit
interface port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 exit
```

### Configure SPAN (Switched Port Analyzer) session
```
monitor session 1 source interface GigabitEthernet1/0/1
monitor session 1 destination interface GigabitEthernet1/0/24
```

### Configure SNMP (v2c and v3)
#### SNMPv2c Configuration
```
snmp-server community <community_string> RO
snmp-server community <community_string> RW
snmp-server contact <contact_info>
snmp-server location <location_info>
```

#### SNMPv3 Configuration (User & Group)
```
# 1. Create an SNMPv3 group
snmp-server group <group_name> v3 priv

# 2. Create an SNMPv3 user with authentication and privacy
# Example with SHA and AES:
snmp-server user <username> <group_name> v3 auth sha <auth_password> priv aes 128 <priv_password>
```

### User Management (SSH/Console Access)
#### Create/Modify a user
```
username <username> privilege <privilege_level> secret <password>
```
*(Note: `privilege 15` is full admin)*

#### Delete a user
```
no username <username>
```

#### Enable SSH (Required for SSH access)
```
ip domain-name <your_domain_name>
crypto key generate rsa
ip ssh version 2
```

### Configuration Management
```
write memory
copy running-config startup-config
show running-config
show startup-config
reload
```

## Execution Mode (Direct Configuration)
This mode allows the agent to directly apply configuration changes to a switch via SSH.

### Process
1. **Retrieve Credentials**: The agent reads switch details from `~/.openclaw/workspace/.switch_credentials` (Format: `switch_name,ip,username,password`).
2. **Construct Command**: The agent builds a secure command using `sshpass` and `ssh`.
3. **Approval (Dry Run)**: The agent MUST present the full command string to the user for approval using `ask="always"`.
4. **Execute**: Upon approval, the agent executes the command on the target switch.
5. **Verification**: After execution, the agent runs relevant `show` commands to verify the change. The agent does NOT automatically save the configuration (e.g., `write memory` or `copy running-config startup-config`); saving must be explicitly requested by the user.
6. **Log**: The agent logs the activity (command, target, status) to a local audit file.

## Juniper EX (JunOS) Examples

### Enter configuration mode
```
configure
```

### Create VLAN
```
set vlans SALES vlan-id 10
set vlans SALES description "Sales VLAN"
```

### Configure access port (interface as access)
```
set interfaces ge-0/0/1 unit 0 family ethernet-switching port-mode access
set interfaces ge-0/0/1 unit 0 family ethernet-switching vlan members SALES
```

### Configure trunk port
```
set interfaces ge-0/0/24 unit 0 family ethernet-switching port-mode trunk
set interfaces ge-0/0/24 unit 0 family ethernet-switching vlan members [10 20 30]
set interfaces ge-0/0/24 unit 0 family ethernet-switching native-vlan-id 99
```

### Verify
```
show vlans
show interfaces terse
show interfaces ge-0/0/24 extensive
```

## ArubaOS-CX Examples

### Enter configuration mode
```
configure
```

### Create VLAN
```
vlan 10
   name SALES
   exit
```

### Access port
```
interface 1/1/1
   no shutdown
   vlan access 10
   exit
```

### Trunk port
```
interface 1/1/24
   no shutdown
   vlan trunk native 99
   vlan trunk allowed 10,20,30
   exit
```

### Verify
```
show vlan
show interface brief
show interface trunk
```

## ArubaOS-Switch (ProVision) Examples
*Used by Aruba 2930F-24G-4SFP and other ProCurve-based switches.*

### Enter configuration mode
```
configure
```

### Create a VLAN
```
vlan 10
   name "SALES"
   exit
```

### Configure an access port (Untagged)
*Note: In ProVision, you assign ports inside the VLAN context.*
```
vlan 10
   untagged 1
   exit
```

### Configure a trunk port (Tagged)
```
vlan 10
   tagged 24
   exit
```

### Remove a port from VLAN
```
vlan 10
   no untagged 1
   no tagged 24
   exit
```

### Verify
```
show vlan
show interfaces brief
```

## Avaya ERS Examples
*Used by Avaya 4548GT and other Ethernet Routing Switches.*

### Enter configuration mode
```
config
```

### Create a VLAN
```
vlan 10
vlan 10 name "SALES"
```

### Configure an access port (Untagged)
```
vlan 10 add port 1
```

### Configure a trunk port (Tagged)
```
vlan 10 add tagged 24
```

### Remove a port from VLAN
```
vlan 10 remove port 1
vlan 10 remove tagged 24
```

### Verify
```
show vlan
show port vlan
```

## Safety & Best Practices

- Always verify current configuration before making changes.
- Use change control or maintenance windows when applicable.
- Save configuration after changes (e.g., `write memory` on Cisco, `commit` on Juniper).
- Be cautious with `no shutdown` / `shutdown` on production ports.
- When pruning VLANs on trunks, ensure you don't disconnect needed traffic.

## Handling Uncertainty

If Cốt con is unsure about any command, configuration detail, or potential impact, it must ask the user for clarification before proceeding. Never guess or assume when configuring network devices.

## Allied Telesis (AlliedWare Plus) Examples

### Enter configuration mode
```
awplus# configure terminal
```

### Create a VLAN
```
awplus(config)# vlan 10
awplus(config-vlan)# exit
```

### Configure an access port
```
awplus(config)# interface port1.0.1
awplus(config-if)# switchport mode access
awplus(config-if)# switchport access vlan 10
awplus(config-if)# no shutdown
awplus(config-if)# exit
```

### Configure a trunk port
```
awplus(config)# interface port1.0.24
awplus(config-if)# switchport mode trunk
awplus(config-if)# switchport trunk allowed vlan add 10,20,30
awplus(config-if)# switchport trunk native vlan 99
awplus(config-if)# no shutdown
awplus(config-if)# exit
```

### Configure port description
```
awplus(config)# interface port1.0.1
awplus(config-if)# description Link to Server Room
awplus(config-if)# exit
```

### Configure interface speed and duplex
```
awplus(config)# interface port1.0.1
awplus(config-if)# speed 100
awplus(config-if)# duplex full
awplus(config-if)# exit
```

### Configure EtherChannel (LACP)
```
awplus(config)# interface range port1.0.1-2
awplus(config-if)# channel-group 1 mode active
awplus(config-if)# exit
```

### Verify
```
awplus# show vlan
awplus# show vlan 10
awplus# show interface brief
awplus# show interface port1.0.1
awplus# show running-config
```

---
