# Network Database Consistency Check

This project is a tool for verifying network device configurations by comparing OpenDCIM database records with SQL query results and real-time SNMP data for switches in HPC clusters. The result is printed to stdout and can be sent as an email if necessary. Moreover, a number of files are created for matching to avoid having to use long loops, which are stored in the tmp folder. My recommendation is to use crontab for scheduling.

**Features**

1. Database Querying: Device information fetching from the OpenDCIM database using SQL queries. For patch pannels a query is performed iteratively until we reach a final end switch. Bear in mind that this part may vary for different database designs.
2. SNMP Commands Execution: SNMP commands on specified devices to gather real-time data using the ifDescr, ifOperStatus and ifAlias values.
3. Data Matching and Analysis: Compares database entries with SNMP command results to identify mismatches.
4. Email Notification: Prepares and sends an email report detailing any discrepancies found.

**Prerequisites**

1. Python 3
2. MySQL Connector (mysql-connector-python)
3. SNMP tools (snmpwalk)
4. SMTP server for sending emails

Update the user, password, and database parameters in the getDataOpenDCIM function as well as the From and To addresses in sendEmail, and to run the script do *python3 main.py* in CLI.
