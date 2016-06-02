#!/usr/bin/python
import os
import commands
import datetime
import time
import sys

########################
### Setup constants  ###
########################

# Set the directories
gpsDir = "/home/lma/gps12"
dataDir = "/data"
dataLogDir = "/data/log"
lmaBinDir = "/home/lma/bin"
shmDir = "/dev/shm"
rootDir = "/root"

############################
### Function definitions ###
############################

# Check disk space
def check_disk():
    print '-' * 50
    print "Checking disk space..."
    print '-' * 50

    status, output = commands.getstatusoutput("df -h")

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)
    else:
        words = output.split()

        # Check root directory /
        i = words.index('/')
        percentIndex = i - 1

        percent = int(words[percentIndex][0:-1])

        if percent > 90:
            print "**\tWarning! Drive / is %3d%% full!" % percent
        else:
            print "/\tis\t%3d%%\tfull" % percent
    
        # Check /data directory
        i = words.index('/data')
        percentIndex = i - 1

        percent = int(words[percentIndex][0:-1])

        if percent > 90:
            print "**\tWarning! Drive /data is %3d%% full!" % percent
        else:
            print "/data\tis\t%3d%%\tfull" % percent
    
    
# Check running processes
def check_proc():
    print ''
    print '-' * 50
    print "Checking running processes..."
    print '-' * 50

    processes = ['./lma_ReadData', './lma_DataHandler', './lma_Decimate3', './lma_TrigLog', './lma_AutoThresh']
    status, output = commands.getstatusoutput("ps ax")

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)
    else:
        words = output.split()
    
        flag = True
        for process in processes:
            try:
                i = words.index(process)
            
            except ValueError:
                flag = False
                print "Process %s not running!" % process
    
        if flag:
            print "All processes are running."
        

# Set system time to GPS time 
def set_gps_time():
    print ''
    print '-' * 50
    print "Setting system time to GPS time..."
    print '-' * 50

    os.chdir(gpsDir)

    # Print the GPS status
    command = "timeout 5 ./read_gps /dev/ttyS1 | ./parse_12"

    flag = False
    i = 1

    while not(flag):
        print "Checking GPS signal. Trial #%d..." % i
        status, output = commands.getstatusoutput(command)

        if status:
            sys.stderr.write(output)
            print "\nEnding script..."
            sys.exit(1)
        else:
            words = output.split()
            print "  - Available satellites: %s" % words[-3]
            print "  - Locked satellites: %s" % words[-2]
            print "  - GPS Code: %s" % words[-1]
            
            # For reference, look up Motorola Binary Format codes for @@Hb
            
            if ('0x8' or '0x9') in words[-1]:
                print "  - GPS has locked its position."
                flag = True
                
            elif ('0xd' in words[-1] or '0xe' in words[-1] or '0xf' in words[-1]):
                print "  - GPS is reaveraging its position."
                flag = True
            
            elif ('0x6' in words[-1] or '0x7' in words[-1]):
                print "  - GPS is acquiring satellites."
                
            else:
                print "  - Unknown GPS Signal."
        i += 1
    
    print ""
    time.sleep(1)

    # Set the system clock from GPS time
    command = "./set_sys_clock_from_gps.pl"

    status, output = commands.getstatusoutput(command)

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)

    print output
    # time.sleep(5)

    # Set the hardware clock from the system clock
    command = "hwclock --systohc"

    status, output = commands.getstatusoutput(command)

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)
    else:
        print output

    time.sleep(1)

    # Check the hardware clock to check if the system time was set correctly.
    command = 'date "+%D %T %Z"'    # "hwclock"

    status, output = commands.getstatusoutput(command)

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)
    else:
        print "Current computer time: \n%s" % output


# Checking that data is being save correctly 
def check_data():
    print ''
    print '-' * 50
    print "Checking the data..."
    print '-' * 50

    # /data
    os.chdir(dataDir)

    date = datetime.date.today().strftime("%y%m%d")
    command = "ls -s %s" % date

    flag = False
    default = "N"

    while not(flag):
        for i in xrange(5):
            status, output = commands.getstatusoutput(command)
    
            if status:
                sys.stderr.write(output)
                print "\nEnding script..."
                sys.exit(1)
            else:
                lines = output.split('\n')
                print "%d of 5:" % (i+1)
                print "%s \n%s\n" % (lines[-2], lines[-1])
                time.sleep(1)

        user_input = raw_input("> Again?: [y/N] ")
    
        if not(user_input):
            user_input = default
        elif user_input.lower() == "n" or user_input.lower() == "n":
            user_input = default
        elif user_input.lower() == "y" or user_input.lower() == "yes":
            user_input = "Y"
        else:
            user_input = "-"
    
        if user_input == "N":
            flag = True
        elif user_input == "-":
            print "Unrecognized input. Try again."

    # /data/log
    os.chdir(dataLogDir)
    print ""

    command = "timeout 10 tail -f T%s%s" % (siteLetter, date)

    print "Running 'tail -f T%s%s' for 10 seconds:\n" % (siteLetter, date)
    os.system(command)
    
    # time.sleep(5)


# Setup cellular modem connection
def set_cell():
    print ''
    print '-' * 50
    print "Setting up cellular modem connection..."
    print '-' * 50

    status, output = commands.getstatusoutput("ifconfig eth1 down")

    print "Bringing the interface down..."
    if status:
        sys.stderr.write(output)
        sys.exit(1)

    time.sleep(2)

    status, output = commands.getstatusoutput("ifconfig eth1 up")

    print "Bringing the interface up..."
    if status:
        sys.stderr.write(output)
        sys.exit(1)

    time.sleep(2)

    print "Requesting an IP address..."
    os.system("dhcpcd -n")
#   status, output = commands.getstatusoutput("dhcpcd -n")
# 
#   if status:
#       sys.stderr.write(output)
#       sys.exit(1)

    time.sleep(2)

    print "\n"
    print "Testing the internet connection..."
    os.system("ping -c 3 www.google.com")
#   status, output = commands.getstatusoutput("ping -c 3 www.google.com")
# 
#   if status:
#       sys.stderr.write(output)
#       sys.exit(2)

    time.sleep(5)

def set_modem():
    # Sets the blastwall modem.
    
    print ''
    print '-' * 50
    print "Setting up Blastwall modem connection..."
    print '-' * 50

    # status, output = commands.getstatusoutput("ifconfig eth1 down")
# 
#   print "Bringing the interface down..."
#   if status:
#       sys.stderr.write(output)
#       sys.exit(1)
# 
#   time.sleep(2)
# 
#   status, output = commands.getstatusoutput("ifconfig eth1 up")
# 
#   print "Bringing the interface up..."
#   if status:
#       sys.stderr.write(output)
#       sys.exit(1)
# 
#   time.sleep(2)

#   print "Requesting an IP address..."
#   os.system("dhcpcd -n")
#   status, output = commands.getstatusoutput("dhcpcd -n")
# 
#   if status:
#       sys.stderr.write(output)
#       sys.exit(1)

#   time.sleep(2)

    print "\nTesting the internet connection..."
    os.system("ping -c 3 10.230.226.216")
#   status, output = commands.getstatusoutput("ping -c 3 www.google.com")
# 
#   if status:
#       sys.stderr.write(output)
#       sys.exit(2)

    time.sleep(5)
    
def done():
    print ""
    print "-" * 50
    print "Done!"
    print "-" * 50
    
def end_script():
    print ""
    print "-" * 50
    print "Quiting LMA Test..."
    print "-" * 50
    sys.exit(1)
    
def check_health():
    print ''
    print '-' * 50
    print "Running 'iclrt_check_health.pl'"
    print '-' * 50

    os.chdir(lmaBinDir)
    
    command = "./iclrt_check_health.pl"

    status, output = commands.getstatusoutput(command)

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)
    else:
        print "OK.\n"
    
    
    print "Check the generated file for correctness:\n"
    os.chdir(shmDir)
    fileName = "port-%s" % siteLetter.lower()
    
    fh = open(fileName)
    
    content = fh.readline()     # Line 1
    content += fh.readline()    # Line 2
    content += fh.readline()    # Line 3
    content += fh.readline()    # Line 4
    content += fh.readline()    # Line 5
    
    print content
    
    fh.close()
    
def send():
    print ''
    print '-' * 50
    print "Running 'send.pl'"
    print '-' * 50
    
    os.chdir(rootDir)
    
    command = "./send.pl"
    
    status, output = commands.getstatusoutput(command)

    if status:
        sys.stderr.write(output)
        print "\nEnding script..."
        sys.exit(1)
    else:
        print "OK."

def menu():
    print "LMA Test Menu:"
    print ""
    print "  1. Run all"
    print "  2. Resume previous run"
    print "  3. Check disks"
    print "  4. Check running processes"
    print "  5. Set system time from GPS"
    print "  6. Check data"
    print "  7. Setup modem"
    print "  8. Run 'check_health' script"
    print "  9. Send data to server"
    print "  q. Quit"
    print "\n"

####################
### Main Program ###
####################

# Clear the terminal screen
os.system("clear")

# Get the station letter
status, output = commands.getstatusoutput("hostname")

if status:
    sys.stderr.write(output)
    print "\nEnding script..."
    sys.exit(1)
else:
    words = output.split('-')
    siteLetter = words[-1].upper()
    
# Print out greeting
print "-" * 50
print "Starting LMA Test at Station %s..." % siteLetter
print "-" * 50

while True:
    print ""
    menu()

    default = "1"
    selection =raw_input('Selection (default = Run all): ')
    if not(selection):
        selection = default
            
    if selection == "1": # Run all
        os.system("clear")
        check_disk()
        check_proc()
        set_gps_time()

        default = "Y"
        flag = False

        while not(flag):
            user_input = raw_input('\n> Continue? : [Y/n] ')

            if not(user_input):
                user_input = default
            elif user_input.lower() == "y" or user_input.lower() == "yes":
                user_input = default
            elif user_input.lower() == "n" or user_input.lower() == "no":
                user_input = "N"
            else:
                user_input = "-"

            if user_input == "N":
                print "Stopping script..."
                sys.exit(1)
            elif user_input == "-":
                print "### Unrecognized input. Try again."
            else:
                flag = True 
    
        check_data()

        if siteLetter != "A":
            set_cell()
            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                    if status:
                        sys.stderr.write(output)
                        print "\nEnding script..."
                        sys.exit(1)
                    else:
                        words = output.split()
                        command = "kill -9 %s" % words[1]
                        
                        status, output = commands.getstatusoutput(command)

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)     
                                                
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 
                    
        else:
            set_modem()
            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                    if status:
                        sys.stderr.write(output)
                        print "\nEnding script..."
                        sys.exit(1)
                    else:
                        words = output.split()
                        command = "kill -9 %s" % words[1]
                        
                        status, output = commands.getstatusoutput(command)

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)     
                                                
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

        check_health()

        default = "Y"
        flag = False

        while not(flag):
            user_input = raw_input('\n> Continue? : [Y/n] ')

            if not(user_input):
                user_input = default
            elif user_input.lower() == "y" or user_input.lower() == "yes":
                user_input = default
            elif user_input.lower() == "n" or user_input.lower() == "no":
                user_input = "N"
            else:
                user_input = "-"

            if user_input == "N":
                print "Stopping script..."
                sys.exit(1)
            elif user_input == "-":
                print "### Unrecognized input. Try again."
            else:
                flag = True 

        send()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")
    
    elif selection == "2":  # Resume previous test
        os.system("clear")
        print "Select the previous stopping point:\n"
        print "1. Check disks"
        print "2. Check running processes"
        print "3. Set system time from GPS"
        print "4. Check data"
        print "5. Setup modem"
        print "6. Run 'check_health' script"
        print "7. Send data to server"
        print "8. Back to menu"
        print "\n"
    
        default = "8"
        selection = raw_input('Selection (default = Back to menu): ')
        if not(selection):
            selection = default
            
        if selection == "1":
            os.system("clear")
            check_disk()
            check_proc()
            set_gps_time()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 
    
            check_data()

            if siteLetter != "A":
                set_cell()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 
                
            else:
                set_modem()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 

            check_health()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
            
        elif selection == "2":
            os.system("clear")
            check_proc()
            set_gps_time()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 
    
            check_data()

            if siteLetter != "A":
                set_cell()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 
                
            else:
                set_modem()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 

            check_health()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")  
            
        elif selection == "3":
            os.system("clear")
            set_gps_time()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 
    
            check_data()

            if siteLetter != "A":
                set_cell()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 
                
            else:
                set_modem()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 

            check_health()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
        
        elif selection == "4":
            os.system("clear")
            check_data()

            if siteLetter != "A":
                set_cell()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True             
                
            else:
                set_modem()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 

            check_health()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
            
        elif selection == "5":
            os.system("clear")
            if siteLetter != "A":
                set_cell()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 
                
            else:
                set_modem()
                default = "Y"
                flag = False

                while not(flag):
                    user_input = raw_input('\n> Continue? : [Y/n] ')

                    if not(user_input):
                        user_input = default
                    elif user_input.lower() == "y" or user_input.lower() == "yes":
                        user_input = default
                    elif user_input.lower() == "n" or user_input.lower() == "no":
                        user_input = "N"
                    else:
                        user_input = "-"

                    if user_input == "N":
                        print "Stopping script..."
                        status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)
                        else:
                            words = output.split()
                            command = "kill -9 %s" % words[1]
                        
                            status, output = commands.getstatusoutput(command)

                            if status:
                                sys.stderr.write(output)
                                print "\nEnding script..."
                                sys.exit(1)     
                                                
                        sys.exit(1)
                    elif user_input == "-":
                        print "### Unrecognized input. Try again."
                    else:
                        flag = True 

            check_health()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
            
        elif selection == "6":
            os.system("clear")
            check_health()

            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Continue? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 

            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
        elif selection == "7":
            os.system("clear")
            send()
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
        elif selection == "8":
            os.system("clear")
        else:
            print "\n### Wrong input. Try again."
            
    elif selection == "3":  # Check disks
        os.system("clear")
        check_disk()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")

    elif selection == "4":  # Check running processes
        os.system("clear")
        check_proc()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")
        
    elif selection == "5":  # Set system time from GPS
        os.system("clear")
        set_gps_time()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")
    
    elif selection == "6":  # Check data
        os.system("clear")
        check_data()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")
    
    elif selection == "7":  # Setup cell modem
        if siteLetter != "A":
            os.system("clear")
            set_cell()
            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Everything OK? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                    if status:
                        sys.stderr.write(output)
                        print "\nEnding script..."
                        sys.exit(1)
                    else:
                        words = output.split()
                        command = "kill -9 %s" % words[1]
                        
                        status, output = commands.getstatusoutput(command)

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)     
                                                
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 
            
            done()
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
        else:
            os.system("clear")
            set_modem()
            default = "Y"
            flag = False

            while not(flag):
                user_input = raw_input('\n> Everything OK? : [Y/n] ')

                if not(user_input):
                    user_input = default
                elif user_input.lower() == "y" or user_input.lower() == "yes":
                    user_input = default
                elif user_input.lower() == "n" or user_input.lower() == "no":
                    user_input = "N"
                else:
                    user_input = "-"

                if user_input == "N":
                    print "Stopping script..."
                    status, output = commands.getstatusoutput("ps ax | grep dhcpcd")

                    if status:
                        sys.stderr.write(output)
                        print "\nEnding script..."
                        sys.exit(1)
                    else:
                        words = output.split()
                        command = "kill -9 %s" % words[1]
                    
                        status, output = commands.getstatusoutput(command)

                        if status:
                            sys.stderr.write(output)
                            print "\nEnding script..."
                            sys.exit(1)     
                                            
                    sys.exit(1)
                elif user_input == "-":
                    print "### Unrecognized input. Try again."
                else:
                    flag = True 
            
            raw_input("> Press ENTER to go to the menu")
            os.system("clear")
        
    elif selection == "8":  # Run check_health.pl
        os.system("clear")
        check_health()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")
    
    elif selection == "9":  # Run send.pl
        os.system("clear")
        send()
        done()
        raw_input("> Press ENTER to go to the menu")
        os.system("clear")
    
    elif selection == "q":  # Quit
        end_script()
    
    else:
        print "\n### Wrong input. Try again."
