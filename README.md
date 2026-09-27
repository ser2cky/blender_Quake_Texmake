# Texmake for Blender
This a port of the in-house UV-mapper tool that ID Software wrote for the development of Quake1/2. I hope that the 2 people (including me)
that care about Quake 1/2's art process, will find this tool fun to use.

Pieces of code I referenced while making this:
* TEXMAKE.C (from https://github.com/id-Software/quake-tools)
* MODELGEN.C (from https://github.com/id-Software/quake-tools)
* models.c (from https://github.com/id-Software/Quake-2-Tools)

## How to use
1. Go into Edit-Mode
2. Press the N-Panel
3. Click the tab that says ***Texmake***
4. Click the button that says ***Generate UV Maps*** under ***Texmake Control Panel***
5. Take a gander at your newly generated Quake-style UV map, and texture -- if you chose to generate one.

## Texmake Control Panel Options

#### Generate Skin ( default: True )
- Checkbox for whether or not you would like to generate a skin for your mesh.
- Enabling this option will pop-up various skin options.
#### *Skin Options* -> Line Style ( default: Fat Lines )
- List of styles that Texmake can draw UV Lines in. The time it takes to generate a texture with UV Lines will increase dramactically, based on the complexity of your mesh.

  ```
    Options:
    1. No Lines (fastest)
    2. Thin Lines (slow)
    3. Fat Lines (slowest)
  ```

#### *Skin Options* -> Line Color ( default: (159, 91, 83) )
- What color lines drawn with Texmake will be.
- Please do not set color using hex values. Blender for some reason does gamma correction to colors, and I don't feel like
making a work-around!!!
- This option is only visible, if ***Line Style*** is not set to ***No Lines***.

#### *Skin Options* -> Fixed Size Skins ( default: False )
- Checkbox for whether or not Texmake skins will be generated at a fixed size.

#### *Skin Options* -> Skin Size ( default: (128, 256) )
- Adjust your skin's fixed width and height.
- This option is only visible, if ***Fixed Size Skins*** is enabled.

#### Forward/Side Axis ( default: Y/X Axis )
- Tells the UV Mapper code which axis corresponds to front/back, and left/right.
- This option is here, because Blender's X and Y axis is different from Quake's X and Y axis... 

## Advice
For UV mapping, I recommend you create a base pose, that exposes as much of the model as possible to the UV mapper. It's also helpful to 
look at Quake1/2 texture maps, to get an idea of how your base poses should look like. 

If my advice is a little unclear, read this article (https://dondeq2.com/2019/07/26/the-art-of-quake-2-by-paul-steed/) written by one of 
Quake 2's artists, and read the section that says ***Skinning Characters***. He explains Quake 1/2 styled UV mapping works a lot better than I can.