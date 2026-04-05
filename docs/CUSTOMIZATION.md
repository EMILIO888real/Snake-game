# Customization Guide

## ⚠️ Important Notes about Settings
- **Sector size and step** must be chosen so that sector size is divisible by step without remainder for correct movement and alignment.
- **Screen size** must be divisible by sector size without remainder to ensure proper grid alignment (width with sector width, height with sector height).
- **Step must be ≤ sector size** for proper movement within the grid.
- **If you change the color style or color scheme setting you must delete the .colors.txt file in the CWD, to apply changes.**
- **For project fonts, don't use bold/italic settings; instead, select the font variant with the desired style in its name.**
- **Compatibility mode on windows changes these settings**:
   - `slower key inputs` to `False`
   - `busy loop threshold` to `0.001`

> **These constraints are critical for proper game functionality. Incorrect values may cause visual glitches or movement issues.**

## Blit positioning

The game uses two positioning systems for blitting:

- **Top-left positioning**: Performance stats, settings menu items
- **Center positioning**: All other UI elements

Keep this distinction in mind when setting blit positions.


## How to add your own mouse cursor
To add a custom mouse cursor, create a folder with your cursor name in `.images/cursors`. There are 2 example cursors available—one static and one animated.

For **animated cursors**: Add each animation frame as a separate image and name them sequentially starting from `0` (e.g., `0.png`, `1.png`, `2.png`, etc.). The numbering must start at `0` and cannot begin at a higher index.

For **static cursors**: Add a single image to the folder and name it `0.png`.

After setting up your cursor folder, update the `mouse cursor` setting in `settings.json` to match your cursor folder's name.

## How to add your own snake images (skin)
To add a custom snake skin, create a folder with your skin name in `.assets/.images/snakes` and add the following images:
- 4 images for the snake's head facing up, left, down, and right, named `snake head 0.png`, `snake head 1.png`, `snake head 2.png`, and `snake head 3.png` respectively.
- 4 images for the snake's body facing up, left, down, and right, named `snake body 0.png`, `snake body 1.png`, `snake body 2.png`, and `snake body 3.png` respectively.

After setting up your snake skin folder, update the `snake images` setting in `settings.json` to match your skin folder's name.