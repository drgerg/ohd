## ohd - (OverHeadDoor) Garage Door Monitor

####Python3, Raspbian learning project

**ohd** monitors two GPIO pins on a Raspberry Pi and responds based on changes to
the status of those pins.  It sends email (or SMS) messages to specific people.

I wanted a simple way to keep track of whether my garage door was open or closed.  
I've been using this now for a few years, and it does exactly what I need.

The Pi is a B+, and the schematic diagram (GarageDoorMonitorRPi2019.pdf) details which pins do what.
I also added a real-time clock module and an Uninterruptable Power Supply to keep it online and
on time.  The UPS is a home-brew job with a 12V gel cell battery that powers an automotive USB
12V to 5V converter.  That converter powers the Pi.  Works like a champ.

I use a typical magnetic reed switch for the door, and I have a red LED that lights up when the door is open.

I re-used a square green pushbutton switch I salvaged off an old PC case for a ByPass button.  
This button has a built-in LED which lights up when the ByPass is engaged.  The ByPass function
allows me to keep the garage door open while I'm working in there without getting notified
every minute.

**ohd** uses Gmail to communicate with the outside world.  I created an account just for this Pi,
and it sends emails to a specified list of recipients when the status of the door or ByPass switch
changes.  Notifications can also be sent by SMS by using the SMS gateway address of the cell service
provider.  Mine is Verizon, and so **ohd** sends an email to 'mycellnumber@vzwpix.com'.  That gets
translated to SMS and shows up on my phone like any other text.

**ohd** also can receive instructions by email or SMS text.  There have been times when the door was opened by
someone who then failed to press the bypass button.  Like when we had flooring contractors working at
our house.  We could not reach them, but I was able to send a "quiet" message to the Pi's Gmail address,
and ohd retrieved that and stopped sending 'door open' notifications.  Very handy.  Currently this is the
only command **ohd** acts on.
