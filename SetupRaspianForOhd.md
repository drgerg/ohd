## Initial Instructions

This is the initial set of instructions on how to get from 'nothing but a Pi' to a fully functional
garage door monitor using **ohd**.

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

#### 1. Download Raspbian (I prefer the one without the graphical interface)
#### 2. Burn to SD card
#### 3. Insert the SD card into the Pi hardware
#### 4. Boot
#### 5. Login - username: pi, password: raspberry
#### 6. Run "sudo raspi-config" at a command prompt
        6a. Select Network
        6b. Select Hostname - give your Pi a name.
        6c. Select wifi: SSID and password - provide the SSID and password to connect to your network.
        6d. Select localization option: set to your area (en_US_utf-8)
        6e. Select localization option: set timezone
        6f. Select Interfacing options: enable SSH

#### 7. Install pip3:
```$ sudo apt-get update```
```$ sudo apt-get python3-pip```

#### 8. Get the RPi.GPIO module for python3
```$ sudo apt-get install python-rpi.gpio python3-rpi.gpio```

#### 9. Change default user/password:

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

#### 10. Get ssmtp and set up mail

```$ sudo apt-get install mailutils```
```$ sudo apt-get install ssmtp```

#### 11. Edit /etc/ssmtp.conf

By the way: the brackets "<>" should not be typed around the "gmail-user" text. They are there to help delineate the example text as example text.  Nor should they be typed around the password.

```$ nano /etc/ssmtp/ssmtp.conf```

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

#### 12. Set ohd to run on boot

We're using the "systemd" method for running things as a service.  I don't understand exactly how it works, I just know it does.  That's enough for me at this point.  It's not that hard.  Don't be afraid.

We need to create a file in the /etc/systemd/system/ folder called "ohd.service".

```$ sudo nano /etc/systemd/system/ohd.service```

That file tells the system different things about ohd.py.  It tells it where it lives, and how and when to run it.

```
[Unit]
Description=Garage door monitor, 2019 update. ohd.service
After=network.target

[Service]
ExecStart=put_the_path_here/ohd/ohd.py  # the full path to ohd.py
WorkingDirectory=put_the_path_here/ohd/ # the full path to the ohd folder
StandardOutput=syslog
StandardError=syslog
User=put_the_user_name_here             # usually your name as the user
ExecStop = /bin/kill -2 $MAINPID

[Install]
WantedBy=multi-user.target
```

For example, my ExecStart line is: ```ExecStart=/home/greg/ohd/ohd.py```
and my User line is: ```User=greg```

Save the file, and then we need to make sure it has the proper ownership.

```$ sudo chown root:root /etc/systemd/system/ohd.service```

I always list the directory to verify things are as they should be.

```$ ls -la /etc/systemd/system```

Now there are two commands that we need to run in order to get this file recognized and incorporated into the system's boot processes:

```$ sudo systemctl daemon-reload```

```$ sudo systemctl enable ohd.service```

At this point ohd.py should be run when your Pi reboots.  You can also control it by using the "service" command set:
```$ sudo service ohd start```

```$ sudo service ohd stop```

```$ sudo service ohd restart```

```$ sudo service ohd status```

You can always learn more about commands by typing something like:
```$ man service```

At this point, things should be working as expected.  If not, well . . . something's wrong.  We'll have to figure it out.  But I'm pretty sure we've covered all the bases here.  

