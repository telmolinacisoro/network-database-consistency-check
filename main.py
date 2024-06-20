import os
from datetime import datetime
from database_utils import fetchData
from snmp_utils import runSnmpCommands
from email_utils import sendNotificationEmail
from file_processing import processFiles

# Main function to execute the script
def main():
    print('Starting execution\n')
    list_hostnames = ['SW-C100-SR']
    error_devices = False
    
    # Set up output directory
    current_dir = os.getcwd()
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_directory = os.path.join(current_dir, 'tmp', current_date)
    os.makedirs(output_directory, exist_ok=True)
    
    # SQL query to fetch device and port data
    query = ("SELECT fac_Device.Label, fac_Device.SerialNo, fac_Ports.Label, connected_device.Label, fac_Ports.ConnectedPort "
            "FROM fac_Device "
            "LEFT JOIN fac_Ports ON fac_Device.DeviceID = fac_Ports.DeviceID "
            "LEFT JOIN fac_Device AS connected_device ON fac_Ports.ConnectedDeviceID = connected_device.DeviceID "
            "WHERE fac_Device.DeviceType='Switch' AND fac_Device.Label IN ('SW-C100-SR')")

    # Fetch results from database
    results = fetchData(query)

    if not results:
        print("No results returned from SQL query.")
        return

    # Prepare email body
    body = "Hello,\n\nThe OpenDCIM database is not up to date. The following errors were found:\n\n"
    for device_hostname in list_hostnames:
        # Run SNMP commands and process the output files
        runSnmpCommands(device_hostname, output_directory)
        processFiles(device_hostname, output_directory, results)
        
        # Check for matched results and build email body
        matched_file = os.path.join(output_directory, f"{device_hostname}_matched.txt")
        if os.path.exists(matched_file):
            with open(matched_file, 'r') as f:
                matched_lines = f.readlines()
                for line in matched_lines:
                    try:
                        logical_port, physical_port, if_status_value, if_alias_value, matched_device_hostname, matched_connected_device_label, remote_port = line.strip().split('\t')
                        if (if_status_value == '1' and matched_connected_device_label == 'None'):
                            body += (f"The device is UP and NONE in OpenDCIM\n")
                        if (if_status_value == '2' and matched_connected_device_label != 'None'):
                            body += (f"The device is DOWN and NOT NONE in OpenDCIM\n")
                        if (if_alias_value != matched_connected_device_label):
                            body += (f"The device hostname is NOT EQUAL in OpenDCIM and CLI\n")
                        if (if_status_value == '1' and if_alias_value == 'None'):
                            body += (f"The device is UP and NONE with CLI\n")
                        if (if_status_value == '2' and if_alias_value != 'None'):
                            body += (f"The device is DOWN and NOT NONE with CLI\n")
                        if (if_status_value == '1' and matched_connected_device_label == 'None') or (if_status_value == '2' and matched_connected_device_label != 'None') or (if_alias_value != matched_connected_device_label) or (if_status_value == '1' and if_alias_value == 'None') or (if_status_value == '2' and if_alias_value != 'None'):
                            body += (f"- Device Hostname from OpenDCIM: {matched_device_hostname}\n"
                                    f"- Physical Port Number from OpenDCIM: {physical_port}\n"
                                    f"- Logical Port Number: {logical_port}\n"
                                    f"- Port Status from Switch CLI: {'up' if if_status_value == '1' else 'down'}\n"
                                    f"- Connected Device from OpenDCIM: {matched_connected_device_label}\n"
                                    f"- Connected Device from Switch CLI: {if_alias_value}\n"
                                    f"- Remote Port from OpenDCIM: {remote_port}\n\n")
                        error_devices = True
                    except ValueError:
                        continue

    body += "\nThank you,\n\nOperators"
    
    # Send email if errors were found
    if error_devices:
         sendNotificationEmail(body)

    print('\n\nEmail Body:\n', body)

if __name__ == "__main__":
    main()
