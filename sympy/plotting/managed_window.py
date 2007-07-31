from pyglet.gl import *
from pyglet.window import Window
from pyglet.clock import Clock

from threading import Thread, Lock, Event

gl_lock = Lock()

class ManagedWindow(Window):
    """
    A pyglet window with an event loop which executes automatically
    in a separate thread. Behavior is added by creating a subclass
    which overrides setup, update, and/or draw.
    """
    fps_limit = 40
    default_win_args = dict(width=600,
                            height=500,
                            vsync=False,
                            resizable=True)

    def __init__(self, **win_args):
        """
        It is best not to override this function in the child
        class, unless you need to take additional arguments.
        Do any OpenGL initialization calls in setup().
        """
        self.win_args = dict(self.default_win_args, **win_args)
        Thread(target=self.__event_loop__).start()

    def __event_loop__(self, **win_args):
        """
        The event loop thread function. Do not override or call
        directly (it is called by __init__).
        """
        gl_lock.acquire()
        try:
            try:
                super(ManagedWindow, self).__init__(**self.win_args)
                self.switch_to()
                self.setup()
            except Exception, e:
                print "Window initialization failed: %s" % (str(e))
                self.has_exit = True
        finally:
            gl_lock.release()

        clock = Clock()
        clock.set_fps_limit(self.fps_limit)
        while not self.has_exit:
            dt = clock.tick()
            gl_lock.acquire()
            try:
                try:
                    self.switch_to()
                    self.dispatch_events()
                    self.clear()
                    self.update(dt)
                    self.draw()
                    self.flip()
                except Exception, e:
                    print "Uncaught exception in event loop: %s" % str(e)
                    self.has_exit = True
            finally:
                gl_lock.release()
        super(ManagedWindow, self).close()

    def close(self):
        """
        Closes the window.
        """
        self.has_exit = True

    def setup(self):
        """
        Called once before the event loop begins.
        Override this method in a child class. This
        is the best place to put things like OpenGL
        initialization calls.
        """
        pass

    def update(self, dt):
        """
        Called before draw during each iteration of
        the event loop. dt is the elapsed time in
        seconds since the last update. OpenGL rendering
        calls are best put in draw() rather than here.
        """
        pass

    def draw(self):
        """
        Called after update during each iteration of
        the event loop. Put OpenGL rendering calls
        here.
        """
        pass

if __name__ == '__main__':
    ManagedWindow()