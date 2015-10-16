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
1- frequency which can be any integer 
2- frequency unit which can be any of s, m , h , d standing for second, minute, hour, day respectively 
3- duration which can be any integer 
4- duration unit which has the same options as the frequency unit

example usage: 
python traceroute.py 1 m 10 d 
This will run traceroute every minute for 10 days 
