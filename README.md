# ohd - (OverHeadDoor) Garage Door Monitor

It is now June, 2023.  DoorPi, which runs **ohd**, has been chugging along out there in the garage since 2015 with minimal intervention.  It's still running Raspbian Buster, and quite frankly, I'm taking a 'if it ain't broke, don't fix it' approach at this point.

v2.2.0 adds camera recording when the door opens, which I should have done some time ago.  It was the addition of another Pi cam in the garage that prompted it.  Works great. The cameras are running into AgentDVR on a Ubuntu machine, and have no real connection to **ohd** other than the fact that we turn recording on and off under certain circumstances.

### History

For decades, I wanted a simple way to keep track of whether my garage door was open or closed.  
I started this project in 2015 and it does exactly what I need. The project eventually morphed into a component of
what I have come to call my [PiNet](https://github.com/casspop/PiNet), a network of Raspberry Pi's that perform various useful functions around my property.

### Primarily monitors and notifies me of the open/close status of the Garage Door.

**'ohd'** monitors specified GPIO pins on a Raspberry Pi and responds based on changes to
the status of those pins.  It sends email (or SMS) messages to numbers in its config file.

### Added a standard motion detector to the front porch.  **'ohd'** monitors that now.

In November of 2019 I added a PIR motion detector to my front porch.  It was natural to let **ohd**
handle the monitoring of its status.  When that motion detector is tripped, **ohd** rings my doorbell rings three times,
then sends notification to the configured emails/SMS gateways, and **Agent DVR** (used to be Zoneminder) is told to
record video for the configured length of time.

In 2022 I replaced **Zoneminder** with another open source program called [**Agent DVR**](https://www.ispyconnect.com/download.aspx).  It significantly simplifies things.

### Simple hardware requirements

The Pi is a 3 Model B+, and the [schematic diagram](./SupportingFiles/GarageDoorMonitorRPi2020.pdf) details which pins do what.
I also added a real-time clock module and an Uninterruptable Power Supply to keep it online and
on time.  The UPS is a home-brew job with a 12V sealed battery that powers a DROK 12V to 5V buck converter.
That converter powers the Pi.  Works like a champ.

I use a typical magnetic reed switch for the door.

I re-used a square green pushbutton switch I salvaged off an old PC case as my ByPass button.  
This button has a built-in LED which lights up when the ByPass is engaged.  The ByPass function
allows me to keep the garage door open while I'm working in there without getting notified
every minute.

### Soft Bypass function

The Soft Bypass function allows me to over-ride the status of the hardware bypass switch when needed.
When Soft Bypass is engaged, the bypass button's LED flashes to remind me Soft Bypass mode is enabled.

Soft Bypass is enabled and disabled through the browser interface provided by [all.py](https://github.com/casspop/Pi-based-weather-station/tree/master/Code/all), which runs on Brilliant, a i3 Ubuntu machine in my office.  None of this is required to use **ohd**, but it is nice.

### Email and SMS notifications

**ohd** uses Gmail to communicate with the outside world.  I created an account just for this Pi,
and it sends emails to a specified list of recipients when the status of the door or ByPass switch
changes.  Notifications can also be sent by SMS by using the SMS gateway address of the cell service
provider.  On Verizon, for example, **ohd** would send an email to 'mycellnumber@vzwpix.com'.  That gets
translated to SMS and shows up on my phone like any other text.

**ohd** also can receive instructions by email.  There have been times when the door was opened by
someone who then failed to press the bypass button.  Like when we had flooring contractors working at
our house.  We could not reach them, but I was able to send a "quiet" message to the Pi's Gmail address,
and ohd retrieved that and stopped sending 'door open' notifications.  Very handy.  Currently this is the
only command **ohd** acts on.

I provided some [instructions](./SetupRaspianForOhd.md) to go from a brand new Pi to a functioning **ohd** system.
The normal caveats apply . . . your mileage may vary.
