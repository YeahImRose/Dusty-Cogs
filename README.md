# Dusty-Cogs
Various cogs for utility/fun

# V3 Rewrite in progress
As of July 25, 2018

## Installing cogs 
To use my cogs, you need to first add my repo:

`[p]cog repo add Dusty-Cogs https://github.com/Lunar-Dust/Dusty-Cogs`

To get a list of cogs in my repo, use:

`[p]cog list Dusty-Cogs`

You can install any of the cogs in my repo by doing:

`[p]cog install Dusty-Cogs cog-name-goes-here`


## Cogs
- autorole:       Automatically give members who join the server a specified role</li>
- greet:          Play a specified sound when a user joins a voice channel</li>
- moji:           Send an emoji from any server that the bot is in  </li>
- pathfinder:     Many utilities such as class/race lookup, die rolling, stat rolling, etc. for Pathfinder</li>

## More cog information
### Autorole
#### Note:
If you want the users to recieve the role immediately, do NOT set an agreement channel

This cog allows you to automatically assign new members of your server a role.
##### Usage:
- `[p]autorole` displays help for autorole commands and shows whether autorole is on or off.
- `[p]autorole role (the role's name [use quotes if the name has a space])` sets the role to be given to new users.
- `[p]autorole toggle` switches the state of automatic role assignment.
- `[p]autorole agreement (#channel_for_agreements) [agreement message]` Sets a terms of service/agreement before the role is given.
The agreement feature of this cog is a bit complicated. You need to give the bot a message that it sends the user.

This message can have a few different things to customize it:

- `{key}`- this is replaced with the key the user must input to recieve their role. This parameter IS NEEDED!</li>
- `{name}`- this is replaced with the username of the user who has joined.</li>
- `{mention}`- this is replaced with a mention for the user who has joined.</li>
- `{server}`- this is replaced with the name of the server the user has joined.</li>
- `{member}`- this is a slightly different parameter as it is a discord Member object. You likely won't need it unless you're an advanced user.

Here's an example of a message:

`Welcome to {server}, {name}! Please read the #rules and enter this key: {key} into #accept`.

### Greet
This cog will cause the bot to play a sound when a user joins the same voice channel as the bot.
#### Note: 
The bot will not play the join sound if the bot is playing music. Also, the owner can cause the bot to join their voice channel with the command `[p]joinvoice` in case the bot is not in a voice channel.

Usage:
- `[p]greetset sound "the-sound.extension"` sets the sound that plays when you join the voice channel.
- `[p]greetset toggle server/user (user mention if needed)` will toggle whether or not the bot will play a greeting sound for the server/a user.
- `[p]greetset` displays help for greet commands.

## Contacting me
If you want to contact me, my Discord name is Awoonar Dust#1273

If you need to contact me but can't contact me through Discord for various reasons, my email is on my github profile.

My support server: https://discord.gg/VsNYqDK
