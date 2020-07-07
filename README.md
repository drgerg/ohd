# ohd - (OverHeadDoor) Garage Door Monitor

For decades, I wanted a simple way to keep track of whether my garage door was open or closed.  
I started this project in 2015 and it does exactly what I need. The project eventually morphed into a component of
what I have come to call my PiNet, a network of Raspberry Pi's that perform various useful functions around my property.

**'ohd'** monitors specified GPIO pins on a Raspberry Pi and responds based on changes to
the status of those pins.  It sends email (or SMS) messages to numbers in its config file.

In November of 2019 I added a PIR motion detector to my front porch.  It was natural to let **ohd**
handle the monitoring of its status.  When that motion detector is tripped, **ohd** rings my doorbell rings three times,
then sends notification to the configured emails/SMS gateways, and [Zoneminder](https://zoneminder.com) is told to
record video for the configured length of time.

The Pi is a 3 Model B+, and the [schematic diagram](./SupportingFiles/GarageDoorMonitorRPi2020.pdf) details which pins do what.
I also added a real-time clock module and an Uninterruptable Power Supply to keep it online and
on time.  The UPS is a home-brew job with a 12V sealed battery that powers a DROK 12V to 5V buck converter.
That converter powers the Pi.  Works like a champ.

I use a typical magnetic reed switch for the door.

I re-used a square green pushbutton switch I salvaged off an old PC case as my ByPass button.  
This button has a built-in LED which lights up when the ByPass is engaged.  The ByPass function
allows me to keep the garage door open while I'm working in there without getting notified
every minute.

**ohd** uses Gmail to communicate with the outside world.  I created an account just for this Pi,
and it sends emails to a specified list of recipients when the status of the door or ByPass switch
changes.  Notifications can also be sent by SMS by using the SMS gateway address of the cell service
provider.  Mine is Verizon, and so **ohd** sends an email to 'mycellnumber@vzwpix.com'.  That gets
translated to SMS and shows up on my phone like any other text.

**ohd** also can receive instructions by email.  There have been times when the door was opened by
someone who then failed to press the bypass button.  Like when we had flooring contractors working at
our house.  We could not reach them, but I was able to send a "quiet" message to the Pi's Gmail address,
and ohd retrieved that and stopped sending 'door open' notifications.  Very handy.  Currently this is the
only command **ohd** acts on.

I provided some [instructions](./SetupRaspianForOhd.md) to go from a brand new Pi to a functioning **ohd** system.
The normal caveats apply . . . your mileage may vary.
