# 5 Nov 2025

- I was able to copy the data directory ./clean into the bundled application for mac. You need to detect if the system is frozen and then change the base path accordingly. I created a function in utilities.py for this.

- When creating an icon for Mac, you should leave about 10% blank space around the edge of the icon. The master icon is 1024x1024 but the final image is about 890x890px.
