# Brocoli

Mandelbrot set explorer and generator written in [python](python.org) and [kivy](kivy.org).

![](assets/screenshot.png)

### Install

You will need python 3.6+ and you can install and run
Brocoli this way:

    git clone https://gitlab.com/ddorn/brocoli.git
    cd brocoli
    pip install -r requirements.txt

And run it with:

    python main.py

### Thanks

First of all, thanks to Benoit Mandelbrot for revealing
beauty od fractals to the world and then to Gaston Julia and Pierre Fatou
for their discovery of the Mandelbrot set.
Thanks also to Numpy and [Numba](https://github.com/numba/numba)
that compiles (JIT) the python code to compute the Mandelbrot set and
make it run two orders of magnitude faster.
Big thanks to [Kivy](kivy.org) and [KivyMD](github.com/HeaTTheatR/KivyMD).
I would not be able to create a graphical interface this nice in such a
short time without them.
