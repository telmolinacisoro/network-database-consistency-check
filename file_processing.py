import os
from .string_utils import swapParts
from .database_utils import fetchData

# Function to match data from files with SQL results
def processFiles(device_hostname, output_directory, sql_results):
    try:
        descr_file = os.path.join(output_directory, f"{device_hostname}_ifDescr.txt")
        status_file = os.path.join(output_directory, f"{device_hostname}_ifOperStatus.txt")
        alias_file = os.path.join(output_directory, f"{device_hostname}_ifAlias.txt")
        output_file = os.path.join(output_directory, f"{device_hostname}_matched.txt")

        if not sql_results:
            print(f"No SQL results for {device_hostname}")
            return

        with open(descr_file, 'r') as descr, open(alias_file, 'r') as alias:
            descr_lines = descr.readlines()[1:-1]
            alias_lines = alias.readlines()[1:-1]

            with open(status_file, 'r') as status, open(output_file, 'w') as output:
                status_lines = status.readlines()[1:-1]
                for descr_line in descr_lines:
                    ifDescr_split = descr_line.split()
                    if len(ifDescr_split) < 2:
                        continue

                    index = descr_line.split('.')[1].split()[0] if '.' in descr_line else descr_line.split()[0]
                    descr_value = descr_line.split(' ', 1)[1].strip()
                    physical_port_number = descr_value.split('/')[-1]

                    status_line = next((line for line in status_lines if f".{index} " in line), None)
                    alias_line = next((line for line in alias_lines if f".{index} " in line), None)

                    if status_line and alias_line:
                        status_value = status_line.split()[-1]
                        status_value = '1' if status_value == 'up(1)' else '2' if status_value == 'down(2)' else 'unknown'
                        alias_value = alias_line.split('STRING: ')[-1].strip().replace('*', '').replace(' ', '-').strip('-')
                        alias_value = alias_value or 'None'

                        sql_data = next((row for row in sql_results if row[2] and row[2].endswith(physical_port_number) and row[0] == device_hostname), None)
                        if sql_data:
                            device_hostname_sql, device_serial_no, port_hostname_sql, connected_device_label_sql, remote_port_sql = sql_data

                            while connected_device_label_sql and ("SM-" in connected_device_label_sql or "MM-" in connected_device_label_sql):
                                patch_panel_hostname = swapParts(connected_device_label_sql)
                                next_query = (f"SELECT fac_Device.Label, fac_Device.SerialNo, fac_Ports.Label, connected_device.Label, fac_Ports.ConnectedPort "
                                              f"FROM fac_Device "
                                              f"LEFT JOIN fac_Ports ON fac_Device.DeviceID = fac_Ports.DeviceID "
                                              f"LEFT JOIN fac_Device AS connected_device ON fac_Ports.ConnectedDeviceID = connected_device.DeviceID "
                                              f"WHERE fac_Device.Label = '{patch_panel_hostname}' AND fac_Ports.PortNumber = '{remote_port_sql}'")
                                next_results = fetchData(next_query)

                                if next_results:
                                    next_result = next_results[0]
                                    connected_device_label_sql = next_result[3]
                                    remote_port_sql = next_result[4]
                                else:
                                    connected_device_label_sql = None

                            output.write(f"{index}\t{physical_port_number}\t{status_value}\t{alias_value}\t{device_hostname_sql}\t{connected_device_label_sql}\t{remote_port_sql}\n")
                        else:
                            print(f"No matching SQL data found for {physical_port_number} and {device_hostname}")

        print(f"Matched results written to {output_file} for device {device_hostname}")

    except Exception as ex:
        print(f"An error occurred while matching files for device {device_hostname}: {ex}")
