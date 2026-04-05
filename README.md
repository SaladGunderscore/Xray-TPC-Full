REQUIRES PYTHON!!!!!!!!!!!!!!!!!!


Merge Gamedata into your Anomaly Main Directory for both Gamma and Anomaly (depending on your installation)

For GOG Users of Gamma: Right click the game in your GOG Launcher -> Right Click the game -> Manage Installation -> Show Folder and find the ANOMALY Folder -> Merge Gamedata folders. (Make a shortcut too to make your life easier)


To Get the Bridge Working:

Open ../Anomaly/Gamedata/ 
Right Click 'twitch-bridge-config.py'

Grab an OAuth Code : https://antiscuff.com/oauth/

And replace TWITCH_TOKEN: with your new token. Example Format: "oath:AUTHENTICATIONCODE"
Replace TWITCH_CHANNEL: with your Channel. Example Format: "#user8675309"

Start your "Bridge Launcher". By Default - Bridge Launcher launches all 3 scripts separately. This is intended for individual module bug testing and modification.

If you only wish to use one module that is available, launch it's individual .py file

Current Modules I have working:

'tpc_bits_bridge_test' - Sends bits to the PDA, The Player loses Rubles each time a bit is donated. (Bits * 10 is the default. This is changed in ../scripts/tpc_bits_actions.script)
'tpc_subs_bridge_test'- Subscriber functions (Spawns hostile monolith hit squad near the player)
'twitch_to_stalker' - Chat Functions in PDA, plans to exclude bots soon. 

PLEASE USE THIS HOWEVER YOU WISH




