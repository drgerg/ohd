## Initial Instructions

This is the initial set of instructions on how to get from 'nothing but a Pi' to a fully functional
garage door monitor using ohd.

**ohd** is a program that tells me when the status of my garage door changes.  It monitors the status of a 
reed switch on the door, and also a pushbutton switch on the housing of the Pi.  It also monitors the time
and writes everything to a log file.  If the ByPass button is left on past a specified time (9PM at my house), 
I get notified.

Notifications happen by way of a Gmail account created for this particular Raspberry Pi.  It sends emails, and 
also can notify by SMS through the cell carrier's email-to-SMS gateway.  They all have one, you can find it easily.

I found it's best to buy a Realtime Clock module.  Follow the instructions for that hardware to get it set up.
I also found it necessary to put my Pi on a UPS.  Otherwise, if the power blips, it reboots.  
Not a huge deal, but it's not good, and it's easy to fix with a small cheap UPS.

Next get the OS and get it set up:

###1. Download Raspbian (I prefer the one without the graphical interface)
###2. Burn to SD card
###3. Insert the SD card into the Pi hardware
###4. Boot
###5. Login - username: pi, password: raspberry
###6. Run "sudo raspi-config" at a command prompt
        6a. Select Network
        6b. Select Hostname - give your Pi a name.
        6c. Select wifi: SSID and password - provide the SSID and password to connect to your network.
        6d. Select localization option: set to your area (en_US_utf-8)
        6e. Select localization option: set timezone
        6f. Select Interfacing options: enable SSH

###7. Install pip3:
```$ sudo apt-get update```
```$ sudo apt-get python3-pip```

###8. Get the RPi.GPIO module for python3
```$ sudo apt-get install python-rpi.gpio python3-rpi.gpio```

###9. Change default user/password:

By default your raspberry pi pi comes with an account 'pi' with the password 'raspberry'. 
For security reasons it's probably a good idea to change the password, but you may also wish to change the 
username as well. There are a couple of different ways to change the default username but I found the 
following method the easiest. 

In order to change the username 'pi' we will have to log in a the root user since it's not possible 
to rename an account while your logged into it. To log in as root user first we have to enable it, 
to do so type the following command whilst logged in as the default pi user:

```$ sudo passwd root```

Choose a secure password for the root user. You can disable the root account later if you wish. 
Now logout of the user pi using the command:

```$ logout```

And then logout back in as the user 'root' using the password you just created. 
Now we can rename the the default pi user name. The following method renames the user 'pi' to 'newname', 
replace this with whatever you want. Type the command:

```$ usermod -l newname pi```

Now the user name has been changed the user's home directory name should also be changed to reflect the 
new login name:

```$ usermod -m -d /home/newname newname```

Now logout and login back in as newname. You can change the default password from raspberry to something 
more secure by typing following command and entering a new password when prompted:

```$ passwd```

If you wish you can disable the root user account again but first double check newname still has 'sudo' privileges. 
Check the following update command works:

```$ sudo apt-get update```

If it works then you can disable the root account by locking the password:

```$ sudo passwd -l root```

And that's it.

*Attribution: https://www.modmypi.com/blog/how-to-change-the-default-account-username-and-password*

###10. Get ssmtp and set up mail

        $ sudo apt-get install mailutils
        $ sudo apt-get install ssmtp

###11. Edit /etc/ssmtp.conf

$ nano /etc/ssmtp/ssmtp.conf

        root=<gmail-user>@gmail.com
        mailhub=smtp.gmail.com:587

        FromLineOverride=YES
        AuthUser=<gmail-user>@gmail.com  # This is the same as MyEmailAdd: in ohd.conf
        AuthPass=<gmail-password>        # This is the same as MyPasswd: in ohd.conf
        UseSTARTTLS=YES
        UseTLS=YES

        # Debug=Yes

CTRL-X  Y  Enter

*Attribution: https://www.algissalys.com/network-security/send-email-from-raspberry-pi-command-line*
