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
    Summary
    =======

    A flexible interface for plotting sympy functions
    and parametric equations.
    """
    def __init__(self, *fargs, **win_args):
        """
        Positional Arguments
        ====================

        Any given positional arguments are used to initialize
        a plot function at index 1. In other words...

        >>> from sympy.core import Symbol
        >>> x = Symbol('x')
        >>> p = Plot(x**2, visible=False)

        ...is equivalent to...

        >>> p = Plot(visible=False)
        >>> p[1] = x**2

        Note that in earlier versions of the plotting module,
        you were able to specify multiple functions in the
        initializer. This functionality has been dropped in
        favor of better automatic plot plot_mode detection.

        Named Arguments
        ===============

        Any given named arguments are passed as arguments to
        window initialization. There is one default argument,
        visible=True. This means show() will be called at the
        end of initialization. If visible=False, show() is not
        called, and must be called explicitly to create and
        display the window.

        See PlotWindow.__init__ for information about other
        valid arguments.
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