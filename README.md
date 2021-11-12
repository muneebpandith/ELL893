# Smart Home Application using HTTP as Communication Protocol



> This work contains an Emulator and Client UI App, Device App that controls the emulator



## Process for running the application

**STEP 1**: Deploy the Device App on EC2 Instance on AWS (or similar infrastructure) using Python/Flask as backend. 

**STEP 2**: Open the TCP port (that will be used to make the Flask port public) in network/security policies of the instance settings.
> Usually Flask runs on port 5000, but it is reconfigurable

**STEP 3**: Open the ClientApp in any window (Make sure API_ROOT in client app is set as the IP:PORT of your EC2 instance and flask port)
> Example: muneebpandith.github.io/ELL893/client/index.html



**STEP 4**: Run the Emulator App in another tab/window:
> Example: muneebpandith.github.io/ELL893/emulator/index.html


**STEP 5**: Interact from client app and see changes in emulator 
## Work Flow Diagram

![HTTP based Work Flow](https://github.com/muneebpandith/ELL893/blob/main/flow.png)
