# Dusty-Cogs
Various cogs for utility/fun

## Installing cogs 
<p>To use my cogs, you need to first add my repo:</p>
<p><code>[p]cog repo add Dusty-Cogs https://github.com/Lunar-Dust/Dusty-Cogs</code></p>
<p>To get a list of cogs in my repo, use:</p>
<p><code>[p]cog list Dusty-Cogs</code></p>
<p>You can install any of the cogs in my repo by doing:</p>
<p><code>[p]cog install Dusty-Cogs cog-name-goes-here</code></p>


## Cogs
<ul>
<li>autorole:       Automatically give members who join the server a specified role</li>
<li>greet:          Play a specified sound when a user joins a voice channel</li>
<li>moji:           Send an emoji from any server that the bot is in  </li>
<li>pathfinder:     Many utilities such as class/race lookup, die rolling, stat rolling, etc. for Pathfinder</li>
</ul>

## More cog information
### Autorole
#### Note:
<p> If you want the users to recieve the role immediately, do NOT set an agreement channel</p>
This cog allows you to automatically assign new members of your server a role.
<ul>Usage:
 <li><code>[p]autorole</code> displays help for autorole commands and shows whether autorole is on or off.</li>
 <li><code>[p]autorole role (the role's name [use quotes if the name has a space])</code> sets the role to be given to new users.</li>
 <li><code>[p]autorole toggle</code> switches the state of automatic role assignment.</li>
 <li><code>[p]autorole agreement (#channel_for_agreements) [agreement message] </code> Sets a terms of service/agreement before the role is given.</li>
 <p> The agreement feature of this cog is a bit complicated. You need to give the bot a message that it sends the user. This message can have a few different things to customize it:</p>
 <ul>
 <li><code>{key}</code>- this is replaced with the key the user must input to recieve their role. This parameter IS NEEDED!</li>
 <li><code>{name}</code>- this is replaced with the username of the user who has joined.</li>
 <li><code>{mention}</code>- this is replaced with a mention for the user who has joined.</li>
 <li><code>{server}</code>- this is replaced with the name of the server the user has joined.</li>
 <li><code>{member}</code>- this is a slightly different parameter as it is a discord Member object. You likely won't need it unless you're an advanced user.</li>
</ul>
<p> Here's an example of a message:
<code> Welcome to {server}, {name}! Please read the #rules and enter this key: {key} into #accept </code>.
When this is formatted, it will look similar to this:
<code> Welcome to Lunar's Land, Awoonar Dust! Please read the #rules and enter this key: 83S16I into #accept </code>.</p>
### Greet
This cog will cause the bot to play a sound when a user joins the same voice channel as the bot.
#### Note: 
<p>The bot will not play the join sound if the bot is playing music. Also, the owner can cause the bot to join their voice channel with the command <code>[p]joinvoice</code> in case the bot is not in a voice channel.</p>
<ul>
Usage:
 <li><code>[p]greetset sound "the-sound.extension"</code> sets the sound that plays when you join the voice channel.</li>
 <li><code>[p]greetset toggle server/user user-mention-if-needed</code> will toggle whether or not the bot will play a greeting sound for the server/a user.</li>
 <li><code>[p]greetset</code> displays help for greet commands.</li>
</ul>
## Contacting me
  
If you want to contact me, my Discord name is Awoonar Dust#0233

If you need to contact me but can't contact me through Discord for various reasons, my email is on my github profile.
