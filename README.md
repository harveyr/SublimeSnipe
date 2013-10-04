SublimeSnipe
============

This is a Sublime Text plugin to execute code in your active view.

It's meant to replace [CodeRunner](http://krillapps.com/coderunner/) in my workflow. (I like CodeRunner, but I'd rather not have to leave my editor.)

With no selection, it will execute everything in the view:

![Screenshot](https://raw.github.com/harveyr/SublimeSnipe/master/snipe1.jpg)


With an active selection, it will execute only the selected code:

![Screenshot](https://raw.github.com/harveyr/SublimeSnipe/master/snipe2.jpg)


Also supports **Javascript** (via node.js) and **PHP**.

I threw this together in a hurry. I'll try to make it a little more sophisticated shortly.

For example, I'm not sure what happens when your code hangs. My guess is Sublime goes nighty-night.


#### Vs. Build System

Yeah, you can use the Sublime build system to basically do the same thing (except for executing only your selection). However, then you have to save your file somewhere. If you're just quickly testing out a few lines of code, that bugs.
