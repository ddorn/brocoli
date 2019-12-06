# Brocoli

Mandelbrot set explorer and generator written in [python](python.org) and [kivy](kivy.org).

![](assets/screenshot.png)

### Install

You will need python 3.6+ and you can install and run 
Brocoli this way:

    git clone gitlab.com/ddorn/brocoli.git
    cd brocoli
    pip install -e requirements.txt
    
And run it with:
    
    python main.py
    
### Thanks

First of all, thanks to Benoit Mandelbrot for revealing 
this beauty to the world. 
Thanks also to Numpy and [Numba](https://github.com/numba/numba)
that compiles (JIT) the python code to compute the Mandelbrot set and
make it run two orders of magnitude faster.
Big thanks to [Kivy](kivy.org) and [KivyMD](github.com/HeaTTheatR/KivyMD).
I would not be able to create a graphical interface this nice in such a 
short time without them.