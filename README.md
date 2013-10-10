SublimeSnipe
============

This is an **experimental** Sublime Text plugin to execute code in your active view.

I say "experimental" because it may be wiser to just customize Sublime's build system and use that. I'll continue to evaluate that as I work on this.

With no selection, it will execute everything in the view:

![Screenshot](https://raw.github.com/harveyr/SublimeSnipe/master/snipe1.jpg)


With an active selection, it will execute only the selected code:

![Screenshot](https://raw.github.com/harveyr/SublimeSnipe/master/snipe2.jpg)


Also supports **Haskell**, **Javascript** (via node.js), and **PHP**.

Half-baked support for **Go** just added. It works on my system, but maybe not on yours.

I threw this together in a hurry. I'll try to make it a little more sophisticated shortly.

For example, I'm not sure what happens when your code hangs. My guess is Sublime goes nighty-night.
