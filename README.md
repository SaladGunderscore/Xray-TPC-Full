
Twitch Chat Integration natively in the PDA using icons from ItsAnchorpoint's Chernobyl Chat Relay Rebirth mod

Twitch Bits Integration to allow users to pay Bits to reduce your in game wallet balance (potentially other options later on for people to use but this is mostly just a basic plugin to get people understanding how they CAN use this mod)

Twitch Subscriber Hit Squads - Every time someone subscribes it spawns a hostile monolith stalker near the player. WIP and plan on making the AI for them focus more on the player to behave more as an actual hit squad.


Super easy to install this, all you do is throw it in the ANOMALY gamedata folder. Not gamma's. And it cannot be installed by ModOrganizer.  VFS fucks with some stuff and ModOrganizer functions off of VFS. If the mod isn't working with twitch chat the first issue is you probably installed it with mod organizer.


I designed this to work with Anomaly and it works seamlessly with Gamma so it should for other Anomaly based modpacks, cannot be certain if it will work on original titles. It might, it probably won't?



To start the mod all you need is Python (latest build is sufficient)
and you open twitch_bridge_config.py in your text editor of choice.

Use the oauth code generator for twitch and plug it into the section with TWITCH_TOKEN with your oauth token in the format provided in the python file, then you just start the bridge_launcher.py 

If you want just the chat feature, you can just run the chat module. Each module has a window that has a couple of test functions (chat module doesn't you can just test in twitch chat to see if thats working, but if twitch chat is working your othe modules should also be working just fine)


INSTALLATION
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




