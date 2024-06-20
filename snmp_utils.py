import subprocess
import os

# Function to execute SNMP commands and save the output to files
def runSnmpCommands(device_hostname, output_directory):
    try:
        snmp_commands = {
            "descr": f"snmpwalk -v 2c -c public {device_hostname} IF-MIB::ifDescr | grep ethernet",
            "status": f"snmpwalk -v 2c -c public {device_hostname} IF-MIB::ifOperStatus",
            "alias": f"snmpwalk -v 2c -c public {device_hostname} IF-MIB::ifAlias"
        }

        for key, command in snmp_commands.items():
            output_file = os.path.join(output_directory, f"{device_hostname}_{key}.txt")
            with open(output_file, 'w') as f:
                subprocess.run(command, shell=True, stdout=f)

        print(f"Output written to files for {device_hostname} successfully.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error executing SNMP command for {device_hostname}: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred for {device_hostname}: {ex}")
