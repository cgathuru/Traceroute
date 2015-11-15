# Traceroute
This project performs a traceroute from the computer to a destination that's supplied via command
line arguments. The traceroute is performed by the operating systems implementation to get around
firewall issues and permission issues that may arise from trying to open a socket or trying to
receive an  ICMP packet.

Usage: 
download and save the python file 
make the python file excecutable by :
chmod + x traceroute.py 
takes for command line parameters 

- --domains &nbsp;Specify a domain or a list orf domains
- --day &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify that you want traceroute to occur every day
- --hr &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify that you want traceroute to occur every hour
- --min &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify that you want traceroute to occur every min
- --rep &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Number of times to run traceroute at the given frequency

**Note**: --day, --hr and --min are mutually exclusive. Default values are rep=1 and --min

Example usage: <br>

    python traceroute.py --min --rep 1 www.google.ca

This will run traceroute once on <a href="https://www.google.ca">www.google.ca</a>.
