# Black Hole

This is a black hole simulation that I made in a couple days. It simulates how light bends and interacts with objects. I simulated the accretion disc by making a cloud around the black hole, adding a noise texture for varying density and spinning it. Maybe it isn't really realistic, but at least it looks cool. If you want to see it in action, you can download the code and run it. It uses python and some modules: `pygame`, `moderngl`, `pyglm` and `numpy`. There's also a record feature. For now, all of it is controlled in-code, but I'm planning to make more controls inside the program.

---

## Usage

Move around with WASD/Space/Shift, look around with mouse and rotate the camera around the Z axis (roll) with arrow keys.
To increase resolution, inside `settings.py` reduce `SCALING`. For better quality go to `shaders/post/raytracing.json` and reduce step size and increase max steps.

---

## Recording

I added a recording function using ffmpeg. I used it to render the video found there: [https://youtube.com/watch?v=Q1WT0efFTZ0](https://youtube.com/watch?v=Q1WT0efFTZ0).



