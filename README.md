# EA_Power_Supply_Control
 
This app generates a .csv file to be used to program an EA 9080-1A power supply.

To access this app, you can run it on your own computer or access the Streamlit instance at this [link](https://ea-powersupplycontrol-hugroup.streamlit.app/).

Below is a step by step guide on how to use the program.

# Step 0 -- Downloading the requisite software
This app makes a .csv file to be read by the **EA Power Control** application. This can be downloaded [here](https://elektroautomatik.com/en/software/ea-power-control/).

# Step 1 -- Creating a Voltage Sequence
On the left panel, define the sequence that you want to run by adding voltage steps. The graph will automatically update to show your program as you build it.

Note: *After the last step, the voltage will automatically be set to zero, so this does not need to be added to a program*

The procedure can be saved to your computer and you can upload past saved programs to load them in.

# Step 2 -- Generating the control sequence
Once the program is complete, click on the **"Generate UHS Sequence"** button, which will download it to your computer under the name *"uhs_sequence.csv"*.

# Step 3 -- EA Power Control
Connect your laptop to the power supply with the USB cable and open the EA Power Control software. Under devices, you should see **EA-9080-1A**.
Then, click on **SeqLog** and select this power supply.

# Step 4 -- Setting up the file paths
In SeqLog, click on options and a panel will pop-up. Under the **Sequencing** tab, click on the folder icon and, in the file selection panel, find and select the *"uhs_sequence.csv"* in your downloads folder.
In the **Logging** tab, you can select a folder and file name to save the data from each run to. Make sure the selections for *"Start logging automatically with sequencing"* and  *"Stop logging automatically with sequencing"* are selected.

# Step 5 -- Running your sequence
Click "OK" to close out of the panel. In the main panel, click **"Start Sequencing"** to run your program. The program will start to run and the voltage will be displayed on the control panel and on the front panel of the power supply.

# Step 6 -- Running another sequence
If you wish to run the same procedure again, you can simply click **"Start Sequencing"** again.
If you wish to make changes, delete the *"uhs_sequence.csv"* in your download folder, make a new script with the web program, download this, and click **"Start Sequencing"**. 

Note: *If you want the logged data from the previous to not be overwritten, you will need to create a new savepath for the data.*
