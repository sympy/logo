from threading import RLock

from plot_object import PlotObject
from plot_axes import PlotAxes
from plot_window import PlotWindow
from plot_mode import PlotMode
import plot_modes

from time import sleep
from util import parse_option_string

class Plot(object):
    """
    Plot Examples
    =============
    
    See examples/plotting.py for many more examples.

    
    >>> from sympy import symbols, Plot
    >>> x,y,z = symbols('xyz')
    
    >>> Plot(x*y**3-y*x**3)
    
    >>> p = Plot()
    >>> p[1] = x*y
    >>> p[1].color = z, (0.4,0.4,0.9), (0.9,0.4,0.4)
    
    >>> p = Plot()
    >>> p[1] =  x**2+y**2
    >>> p[2] = -x**2-y**2


    Variable Intervals
    ==================
    
    The basic format is [var, min, max, steps], but the
    syntax is flexible and arguments left out are taken
    from the defaults for the current coordinate mode:
    
    >>> Plot(x**2) # implies [x,-5,5,100]
    >>> Plot(x**2, [], []) # [x,-1,1,40], [y,-1,1,40]
    >>> Plot(x**2-y**2, [100], [100]) # [x,-1,1,100], [y,-1,1,100]
    >>> Plot(x**2, [x,-13,13,100])
    >>> Plot(x**2, [-13,13]) # [x,-13,13,100]
    >>> Plot(x**2, [x,-13,13]) # [x,-13,13,100]
    >>> Plot(1*x, [], [x], mode='cylindrical')
    ... # [unbound_theta,0,2*Pi,40], [x,-1,1,20]


    Coordinate Modes
    ================
    
    Plot supports several curvilinear coordinate modes, and
    they independent for each plotted function. You can specify
    a coordinate mode explicitly with the 'mode' named argument,
    but it can be automatically determined for cartesian or
    parametric plots, and therefore must only be specified for
    polar, cylindrical, and spherical modes.
    
    Specifically, Plot(function arguments) and Plot[n] =
    (function arguments) will interpret your arguments as a
    cartesian plot if you provide one function and a parametric
    plot if you provide two or three functions. Similarly, the
    arguments will be interpreted as a curve is one variable is
    used, and a surface if two are used.
    
    Supported mode names by number of variables:
        
    1: parametric, cartesian, polar
    2: parametric, cartesian, cylindrical = polar, spherical
    
    >>> Plot(1, mode='spherical')


    Calculator-like Interface
    =========================
    
    >>> p = Plot(visible=False)
    >>> f = x**2
    >>> p[1] = f
    >>> p[2] = f.diff(x)
    >>> p[3] = f.diff(x).diff(x)
    >>> p
    [1]: x**2, 'mode=cartesian'
    [2]: 2*x, 'mode=cartesian'
    [3]: 2, 'mode=cartesian'
    >>> p.show()
    >>> p.clear()
    >>> p
    <blank plot>
    >>> p[1] =  x**2+y**2
    >>> p[1].style = 'solid'
    >>> p[2] = -x**2-y**2
    >>> p[2].style = 'wireframe'
    >>> p[1].color = z, (0.4,0.4,0.9), (0.9,0.4,0.4)
    >>> p[1].style = 'both'
    >>> p[2].style = 'both'
    >>> p.close()


    Plot Window Keyboard Controls
    =============================

    Screen Rotation:
        X,Y axis      Arrow Keys, A,S,D,W, Numpad 4,6,8,2
        Z axis        Q,E, Numpad 7,9
        
    Model Rotation:
        Z axis        Z,C, Numpad 1,3
        
    Zoom:             R,F, PgUp,PgDn, Numpad +,-
                        
    Reset Camera:     X, Numpad 5
    
    Camera Presets:
        XY            F1
        XZ            F2
        YZ            F3
        Perspective   F4
        
    Sensitivity Modifier: SHIFT
    
    Axes Toggle:
        Visible       F5
        Colors        F6
    
    Close Window:     ESCAPE

    =============================
    """

    def __init__(self, *fargs, **win_args):
        """
        Positional Arguments
        ====================

        Any given positional arguments are used to
        initialize a plot function at index 1. In
        other words...

        >>> from sympy.core import Symbol
        >>> x = Symbol('x')
        >>> p = Plot(x**2, visible=False)

        ...is equivalent to...

        >>> p = Plot(visible=False)
        >>> p[1] = x**2

        Note that in earlier versions of the plotting
        module, you were able to specify multiple
        functions in the initializer. This functionality
        has been dropped in favor of better automatic
        plot plot_mode detection.
        
        
        Named Arguments
        ===============

        axes
            An option string of the form
            "key1=value1; key2 = value2" which
            can use the following options:
        
            style = ordinate
                none OR frame OR box OR ordinate
                
            stride = 0.25
                val OR (val_x, val_y, val_z)
                
            overlay = True (draw on top of plot)
                True OR False
                
            colored = False (False uses Black,
                             True uses colors
                             R,G,B = X,Y,Z)
                True OR False
                
            label_axes = False (display axis names
                                at endpoints)
                True OR False

        visible = True (show immediately
            True OR False


        The following named arguments are passed as
        arguments to window initialization:

        antialiasing = True
            True OR False

        ortho = False
            True OR False

        invert_mouse_zoom = False
            True OR False

        """
        self._win_args = win_args
        self._window = None

        self._render_lock = RLock()

        self._functions = {}
        self._pobjects = []

        axe_options = parse_option_string(win_args.pop('axes', ''))
        self.axes = PlotAxes(**axe_options)
        self._pobjects.append(self.axes)

        self[1] = fargs
        if win_args.get('visible', True):
            self.show()

    ## Window Interfaces

    def show(self):
        """
        Creates and displays a plot window, or activates it
        (gives it focus) if it has already been created.
        """
        if self._window and not self._window.has_exit:
            self._window.activate()
        else:
            self._win_args['visible'] = True
            self.axes.reset_resources()
            self._window = PlotWindow(self, **self._win_args)

    def close(self):
        """
        Closes the plot window.
        """
        if self._window:
            self._window.close()

    def saveimage(self, filepath, **kwargs):
        """
        Saves a screen capture of the plot window to an
        image file. Not implemented yet.
        """
        raise NotImplementedError()

    ## Function List Interfaces

    def clear(self):
        """
        Clears the function list of this plot.
        """
        self._render_lock.acquire()
        self._functions = {}
        self.adjust_all_bounds()
        self._render_lock.release()

    def __getitem__(self, i):
        """
        Returns the function at position i in the
        function list.
        """
        return self._functions[i]

    def __setitem__(self, i, args):
        """
        Parses and adds a PlotMode to the function
        list.
        """
        if not (isinstance(i, int) and i > 0):
            raise ValueError("Function index must "
                             "be a positive integer.")

        if isinstance(args, PlotObject):
            f = args
        else:
            if not isinstance(args, (list, tuple)):
                args = [args]
            if len(args) == 0:
                return # no arguments given
            kwargs = dict(bounds_callback=self.adjust_all_bounds)
            f = PlotMode(*args, **kwargs)

        if f:
            self._render_lock.acquire()
            self._functions[i] = f
            self._render_lock.release()
        else:
            raise ValueError("Failed to parse '%s'."
                    % ', '.join(str(a) for a in args))

    def __delitem__(self, i):
        """
        Removes the function in the function list at
        position i.
        """
        self._render_lock.acquire()
        del self._functions[i]
        self.adjust_all_bounds()
        self._render_lock.release()

    def firstavailableindex(self):
        """
        Returns the first unused index in the function list.
        """
        i = 1
        self._render_lock.acquire()
        while i in self._functions: i += 1
        self._render_lock.release()
        return i

    def append(self, *args):
        """
        Parses and adds a PlotMode to the function
        list at the first available index.
        """
        self.__setitem__(self.firstavailableindex(), args)

    def __len__(self):
        """
        Returns the number of functions in the function list.
        """
        return len(self._functions)

    def __iter__(self):
        """
        Allows iteration of the function list.
        """
        return self._functions.itervalues()

    def __repr__(self):
        return str(self)

    def __str__(self):
        """
        Returns a string containing a new-line separated
        list of the functions in the function list.
        """
        s = ""
        if len(self._functions) == 0:
            s += "<blank plot>"
        else:
            self._render_lock.acquire()
            s += "\n".join(["%s[%i]: %s" % ("", i, str(self._functions[i]))
                              for i in self._functions])
            self._render_lock.release()
        return s

    def adjust_all_bounds(self):
        self._render_lock.acquire()
        self.axes.reset_bounding_box()
        for f in self._functions:
            self.axes.adjust_bounds(self._functions[f].bounds)
        self._render_lock.release()

    def wait_for_calculations(self):
        sleep(0)
        self._render_lock.acquire()
        for f in self._functions:
            a = self._functions[f]._get_calculating_verts
            b = self._functions[f]._get_calculating_cverts
            while a() or b(): sleep(0)
        self._render_lock.release()