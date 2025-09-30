![[Pasted image 20230703140125.png]]
This happened when there was a change of IP in the signal generator and the Keysight Connection Expert was not able to find the device.

I think is also related to the fact that I already opened a session before and the instrument is busy.

looks like so, close the resource like this every time you want to create a new instance:

![[Code_ANOQS4xmBi.png]]
![[InkedCode_ARhBJWd8GD.jpg]]
Don-t do this, it breaks (an instance of the class inside the class definition). I think it tries to open the resource several times.