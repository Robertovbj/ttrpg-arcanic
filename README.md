
# Apocalypse World TTRPG Discord bot

This project was done as a commission requested via Discord. The idea is a bot that can serve as a support for playing the TTRPG system "Apocalypse World". With it you can create your character sheet, adjust your status, the damage you receive (harms), your relationships to other characters (HX), your inventory and money, and you can trade items with other characters.


## Installation

The project runs using python 3.11, using SQLite3 as database.

Clone the project and create a python 3.11 virtual environment inside its directory. You can then install the requirements by using:

```bash
pip install -r requirements.txt
```

You will also need to create a Discord bot application on Discord Developer Portal, and create a file named `config.py` in the main directory with the bot token inside it.
The file will look like this:

```python
TOKEN = "YOUR_TOKEN_HERE"
```

You can finally run by using:

```bash
python main.py
```


## Commands

Here is a list with all the bot commands.

| Command | Description |
| :- | :- |
| `!checksheet [name]` | Check your character's full sheet. If a name is passed as argument, will show the named character's sheet instead.<br>Examples:<br>`!checksheet` - Shows your character's full sheet<br>`!checksheet "Will Smith"` - Shows Will Smith's full sheet |
| `!createsheet <name>` | Create a new character with the specified name. To use two or more names, encase them with quotes. Only **ONE** character is allowed per server.<br>Example:<br>`!createsheet "Will Smith" |
| `!deletesheet` | Delete your character **FOREVER**. Will ask for confirmation to avoid accidents. |
| `!highlight <stat1> <stat2>` | Highlights the two specified stats. Must inform both by name.<br>Example:<br>`!highlight Cool Weird` - Highlights Cool and Weird stats. |
| `!adjuststats <name> <value> [\| <name> <value>]...` | Adjust stats to specified number. Can specify multiple stats at once by separating the "stat, value" pair with "\|".<br>Example:<br>`!adjuststats Cool 1` - Set Cool to 1.<br>`!adjuststats Cool 1 | Hot 3` - Set Cool to 1 and Hot to 3. |
| `!image <imgur_link>` | Changes your character image to a new one provided by the user. The link should be a imgur link like the following: <https://i.imgur.com/JOf48jt.jpeg> |
| `!resetimage` | Resets your character's image. Will ask for confirmation. |
| `!moves` | Lists all moves available. |
| `!mymoves` | Lists your character's moves. |
| `!learnmoves <move> [\| <move>]...` | Learns named moves. To specify the move to learn, use `!moves`, copy it's name and paste it between double quotes. Can specify multiple moves at once by separating their names with "\|".<br>Examples:<br>`!learnmoves "Sixth sense"` - Adds the move Sixth sense to your sheet.<br>`!learnmoves "Sixth sense" \| "Reality's fraying edge"` - Adds the moves Sixth sense and Reality's fraying edge to your sheet. |
| `!removemoves <move> [\| <move>]...` | Removes named moves from your sheet. To specify the move to remove, use `/moves`, copy it's name and paste it between double quotes. Can specify multiple moves at once by separating their names with "\|".<br>Examples:<br>`!removemoves "Sixth sense"` - Removes the move Sixth sense from your sheet.<br>`!removemoves "Sixth sense" \| "Reality's fraying edge"` - Removes the moves Sixth sense and Reality's fraying edge from your sheet. |
| `!harminfo` | Shows your character's harms and conditions. |
| `!takeharm <amount>` | Add specified amount of harm to your character. Also calculates and gives you a warning if you're going to die. |
| `!stabilize` | Adds or removes the _stabilized_ status from your character. |
| `!takedebility <name>` | Marks a debility for your character. Remember, debilities are **PERMANENT**. Valid options are: `shattered` `crippled` `disfigured` `broken` |
| `!healharm <amount>` | Heal specified amount of harm on your character. |
| `!noharm` | Fully heals your character. |
| `!fullheal` | Fully heals your character, including debilities. |
| `!hxinfo [name]` | Lists all HX info from your character. If a character's name is used as argument, it lists only the HX towards that character.<br>Examples:<br>`!hxinfo` - Shows all HX info<br>`!hxinfo "Will Smith"` - Shows the HX towards Will Smith |
| `!hxadjust <name> <amount> [\| <name> <amount>]...` | Adjusts HX towards other characters. Can specify multiple characters at once by separating the "character name, value" pair with "\|". If the amount is -4 or 4, it will set to -1 and 1 respectively, and _warn_ you that you can get exp points for that (it will not give you exp automatically).<br>Example:<br>`!hxadjust "Will Smith" 1` - Set HX towards Will Smith to 1.<br>`!hxadjust "Will Smith" 1 \| "Leonardo Dicaprio" 3` - Set HX towards Will Smith to 1 and 3 towards Leonardo Dicaprio. |
| `!addexp <amount>` | Add specified amount of exp to your character. Also calculates and shows the amount of improvement points. |
| `!myimprovements` | Lists your character's improvements. |
| `!improve <number> [\| <number>]...` | Get the specified improvement. Can specify multiple improvements at once by separating the "value" with "\|". The number must be between 1 and 16 (both included) and can't be 12, 13 and 14 (check `finaladvance` and `newtype` commands). It will **_NOT_** add the stats to your sheet if the improvement says you should, it must be done manually.<br>Example:<br>`!improve 1` - Get the first improvement.<br>`!improve 1 \| 3` - Get the first and the third improvements. |
| `!removeimprovement <number> [\| <number>]...` | Remove the specified improvement. Can specify multiple improvements at once by separating the "value" with "\|". The number must be between 1 and 16 (both included) and can't be 12, 13 and 14 (check `finaladvance` and `newtype` commands). It will **_NOT_** remove the stats from your sheet if the improvement was about adding it, it must be done manually.<br>Example:<br>`!removeimprovement 1` - Remove the first improvement.<br>`!removeimprovement 1 \| 3` - Remove the first and the third improvements. |
| `!inventory` | Lists your character's the inventory. |
| `!addbarter <amount>` | Adds specified amount of barter to your character. |
| `!usebarter <amount>` | Spends specified amount of barter. |
| `!givebarter <name> <amount>` | Gives the named character specified amount of barter. |
| `!additem <amount> <name> <description> [\| <amount> <name> <description>]...` | Adds items to your inventory. Can specify multiple items at once by separating the "amount, name, description" group with "\|". If the item already exists on your inventory, it will add it's amount and **keep** the old description (meaning it's good to keep item's names unique for each description).<br>Example:<br>`!additem 1 "Potion 1" "Heals 1 harm"` - Adds 1 "Potion 1" that "Heals 1 harm" to your inventory.<br>`!additem 2 "Potion 1" "Heals 1 harm" \| 1 "Potion 2" "Heals 2 harm"` - Adds 2 "Potion 1" that "Heals 1 harm" and 1 "Potion 2" that "Heals 2 harm" to your inventory. |
| `!removeitem <amount> <name> [\| <amount> <name>]...` | Removes items from your inventory. Can specify multiple items at once by separating the "amount, name" group with "\|".<br>Example:<br>`!removeitem 1 "Potion 1"` - Removes 1 "Potion 1" from your inventory.<br>`!removeitem 2 "Potion 1" \| 1 "Potion 2"` - Removes 2 "Potion 1" and 1 "Potion 2" from your inventory. |
| `!itemdescription <name> <description> [\| <name> <description>]...` | Edits the description of items on your inventory. Can specify multiple items at once by separating the "name, description" pair with "\|".<br>Example:<br>`!itemdescription "Potion 1" "Heals 2 harm"` - Changes the description of "Potion 1" to "Heals 2 harm".<br>`!itemdescription "Potion 1" "Heals 2 harm" \| "Potion 2" "Heals 3 harms"` - Changes the description of "Potion 1" to "Heals 2 harm" and of "Potion 2" to "Heals 3 harms". |
| `!equip <name>` | Equips or unequips specified item. |
| `!give <name> <amount> <item> [\| <amount> <item>]...` | Gives the named character specified amount of some item. Can specify multiple items at once by separating the "amount, item name" pair with "\|".<br>Example:<br>`!give "Will Smith" 1 "Potion"` - Gives Will Smith 1 Potion.<br>`!give "Will Smith" 1 "Potion" \| 2 "Potion 2"` - Gives Will Smith 1 Potion and 2 "Potion 2". |
| `!allcharacters` | Lists all active characters. |
| `!retired` | Lists all retired characters. |
| `!finaladvance` | Will **DELETE** your sheet but will save it's name, playbook and stats for consulting. It's the equivalent of getting the 'create a second character to play' and 'retire your character (to safety)' improvements. |
| `!newtype <playbook>` | Change your character to a new type. It's the equivalent of getting the 'change your character to a new type' improvement. Valid options are: `Angel` `Battlebabe` `Brainer` `Chopper` `Driver` `Gunlugger` `Hardholder` `Hocus` `Operator` `Savyhead` `Skinner` `Child-thing` `Faceless` `News` `Quarantine` `Show` `Waterbearer` `Landfall Marine` |
 
## What I learned from it

Doing this project, I learned a lot of new things and practiced old ones, such as:
  - **Manage time:** Setting a deadline for the client accounting with potential problems correctly went fine, but I really thought I would have completed the project earlier than the deadline I gave to it, and the reality is that I finished it on the last day. I also learned that I just can't go on a coding spree for hours straight, and taking some breaks is important too.
  - **New techs:** I have never worked with Discord API or Vultr, and had very little experience with Linux and GitHub. Doing this project, I learn how easy is to create a Discord App, and how challenging it can be to host my project online, using a Ubuntu server on Vultr. I also had a bit of practice with SSH, it's keys and also with firewall configuration. And, most of all, I used Github a lot, and it was really nice to finally use it properly.
  - **Even more english practice:** English is not my main language, and even having a advanced level, It's never too much practice. Since it was a full english project, I used english even when documenting or for personal files to keep track of what I needed to do.
  - **Python list comprehension:** Python can be a bit different from the other languages with its list comprehension, and since I dont use it that much usually, it was quite challenging to understand the Python way to do some stuff.
  - **I still have stuff to learn!:** Even having experience with MVC and OOP, this project showed me I still need to learn how to encapsulate and abstract my classes better, and I should have created a Controller for my MVC (the controller function stayed on the main file, which can be improved), but I decided to not create them because when I noticed something was missing, I was way too far on the project and refactoring it would take way more time than I had. It would also be good to separate the views better, which are on the models files.
  
Overall, this project was a great experince to learn and develop myself as a developer, and I'm aiming to learn even more.
