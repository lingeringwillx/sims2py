One annoying aspect of the game is that it randomizes the names of created sims when adding a new sub-neighborhood, and so far the only solution to this was to rename all of the sims manually. This script is an attempt at creating a tool that automates this process and restores the names of sims to their original names, as found in the sub-neighborhood template files.

This script is experimental. Only use it on neighborhoods that you don't mind breaking, or at least make a backup of your neighborhood before using it.
You're expected to know how to run a Python script to be able to use this.

The script uses the sim's hair, skin color, and default outfits to recognize the sim. If you changed any of those. The script might not work on the sim.

How to use (Instructions for Windows 10):
1- Install Python. The script requires Python 3.7 or higher. Make sure to check the "Add to PATH" checkbox if it appears in the installer.
2- Backup your neighborhood. This doesn't have to take a lot of effort, just go to your My Documents/EA Games, click on The Sims folder, and press Ctrl+C, Ctrl+V.
3- Open the folder that contains this script.
4- In the file explorer, press Shift + Right Click, and choose "Open Powershell Window here".
5- To run the script, enter the following format: python autorename.py neighborhood_folder template_folder1 template_folder2 template_folder3...
6- "neighborhood_folder" is the path to your neighborhood folder, and the "template_folder" entries are the paths to the original templates that you've added to your neighborhood. These can be easily entered by going to the neighborhood or template folder and dragging and dropping it to the shell.
7- Press Enter.
8- A folder named "New Character Files" will be generated. Copy all the files from that folder, and paste them in your neighborhood's characters folder, overwriting the old files.