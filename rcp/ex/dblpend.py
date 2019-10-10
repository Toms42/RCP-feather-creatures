"""Python 3 GUI application module to support the 16-375 double-pendulum control exercises."""

################################################################
# Written in 2018-2019 by Garth Zeglin <garthz@cmu.edu>

# To the extent possible under law, the author has dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.

# You should have received a copy of the CC0 Public Domain Dedication along with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

################################################################
# standard Python libraries
import os, sys, logging, functools
import numpy as np

# documentation on the PyQt5 API: http://pyqt.sourceforge.net/Docs/PyQt5/index.html
from PyQt5 import QtCore, QtWidgets, QtGui

# documentation on pyqtgraph:  http://pyqtgraph.org/documentation/plotting.html
import pyqtgraph

# This uses several modules from the course library.
import rcp.QtConfig
import rcp.QtLog
import rcp.QtDoublePendulum

import rcp.app
import rcp.doublependulum

# set up logger for module
log = logging.getLogger(__file__)

################################################################
class AppWindow(QtWidgets.QMainWindow):
    """A custom main window which provides all GUI controls.  This generally follows
    a model-view-controller convention in which this window provides the views,
    passing events to the application controller via callbacks.
    """

    def __init__(self, main):
        super().__init__()

        # This GUI controller assumes it has access to an application controller with the methods of app.MainApp.
        self.main = main

        # create the GUI elements
        self._setupUi()

        # finish initialization
        self.show()

        return

    def connect_callbacks(self):
        """Finish initializing the GUI by connecting all callbacks from GUI elements to
        application controller methods.  This allows the log window to be set up
        early to capture any messages from the initialization of other object.
        """
        return

    # ------------------------------------------------------------------------------------------------
    def _setupUi(self):

        # basic window setup
        self.setWindowTitle("Double Pendulum Exercise")
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        # set up tabbed page structure
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self._tab_changed)

        # set up the main tab with the system state display
        self.mainTab = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainTab)
        self.graphicsLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.graphicsLayout)
        
        # cartoon graphics using a custom widget
        # self.cartoon = QtDoublePendulum.QtDoublePendulum()
        # self.cartoon.setMinimumSize(QtCore.QSize(400, 400))
        # self.mainLayout.addWidget(self.cartoon)

        # cartoon graphics using a QGraphicsScene and an optional OpenGL view
        self.scene = QtWidgets.QGraphicsScene(-700, -700, 1400, 1400)
        self.view = QtWidgets.QGraphicsView(self.scene)
        # self.view.setViewport(QtWidgets.QOpenGLWidget())
        self.view.fitInView(QtCore.QRectF(-700, -700, 1400, 1400), QtCore.Qt.KeepAspectRatio)
        self.view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.graphicsLayout.addWidget(self.view)

        self.pendulum = rcp.QtDoublePendulum.QtDoublePendulumItem()
        self.scene.addItem(self.pendulum)

        self.state_display = QtWidgets.QGraphicsSimpleTextItem("Angles: 0 0", self.pendulum)
        self.state_display.setPos(-600, 600)
        self.state_display.setFont(QtGui.QFont("Sans Serif", 30))

        # plotting area with phase plot
        self.configPlot = pyqtgraph.PlotWidget()        
        self.graphicsLayout.addWidget(self.configPlot)
        self.config_data = np.zeros((300, 2))
        self.config_plot = pyqtgraph.ScatterPlotItem(size=len(self.config_data), brush=pyqtgraph.mkBrush(0, 255, 0, 255))
        self.config_plot.setSize(2)
        self.configPlot.addItem(self.config_plot)
        self.configPlot.getPlotItem().setTitle(title='Configuration Space Plot')
        self.configPlot.getPlotItem().setLabel(axis='left', text='q1')
        self.configPlot.getPlotItem().setLabel(axis='bottom', text='q0')
        self.configPlot.getPlotItem().setYRange(-3.16, 3.16)
        self.configPlot.getPlotItem().setXRange(-3.16, 3.16)
        
        # scrolling text box for controller messages
        self.mainText = QtWidgets.QPlainTextEdit()
        # self.mainText.appendPlainText("Hello, world.")

        # array of general-purpose horizontal sliders
        self.sliderLayout = QtWidgets.QVBoxLayout()
        self.sliderLayout.setContentsMargins(-1, -1, -1, 9)
        self.sliders = list()
        for i in range(8):
            box = QtWidgets.QHBoxLayout() # box for label and slider
            slider = QtWidgets.QSlider()
            slider.setMinimumSize(QtCore.QSize(60, 20))
            slider.setMaximum(1000)
            slider.setOrientation(QtCore.Qt.Horizontal)
            slider.valueChanged['int'].connect(functools.partial(self.sliderMoved, i))
            self.sliders.append(slider)
            label = QtWidgets.QLabel()
            label.setText("%d: " % (i))
            box.addWidget(label)            
            box.addWidget(slider)
            self.sliderLayout.addLayout(box)

        # add a final empty widget to soak up space
        self.sliderLayout.addWidget(QtWidgets.QWidget())
        
        # put the sliders and console box side by side
        console_slider_box = QtWidgets.QHBoxLayout()
        console_slider_box.addWidget(self.mainText)
        console_slider_box.addLayout(self.sliderLayout)
        self.mainLayout.addLayout(console_slider_box)
        self.tabs.addTab(self.mainTab, 'Main')
        
        # set up the configuration tab
        self.configForm = rcp.QtConfig.QtConfigForm()
        self.tabs.addTab(self.configForm, 'Config')

        self.configFileButtons = rcp.QtConfig.QtConfigFileButtons(delegate=self.main, path=self.main.configuration_file_path)
        self.configForm.addField("Configuration file:", self.configFileButtons)

        # set up the logging tab
        self.logDisplay = rcp.QtLog.QtLog(level=logging.INFO)
        self.tabs.addTab(self.logDisplay, 'Log')

        return

    # --- window and Qt event processing -------------------------------------------------------------
    def set_status(self, string):
        """Update the status bar at the bottom of the display to show the provided string."""
        self.statusbar.showMessage(string)
        return

    def _tab_changed(self, index):
        log.debug("Tab changed to %d", index)
        return

    def closeEvent(self, event):
        """Qt callback received before windows closes."""
        log.info("Received window close event.")
        self.main.app_is_exiting()
        super().closeEvent(event)
        return

    def write(self, string):
        """Write output to the console text area."""
        self.mainText.appendPlainText(string)
        return

    def sliderMoved(self, slider, value):
        # send a message to the user controller object; this is really reaching across abstraction boundaries
        self.main.controller.user_parameter_change(slider, 0.001*value)
        return
    
    # ---- configuration management --------------------------------------------------------------------
    def apply_user_configuration(self, config):
        """Apply the persistent configuration values from a configparser section proxy object."""
        self.logDisplay.set_logging_level(config['log'].get('logging_level', fallback='Verbose'))

        #
        # Other GUI object with persistent state should be updated from the configuration here.
        #
        return

    def gather_configuration(self, config):
        """Update the persistent configuration values in a configparser section proxy object."""
        config['log']['logging_level'] = self.logDisplay.get_logging_level()

        #
        # Other GUI object with persistent state should update the configuration object here.
        # 
        return
    # --------------------------------------------------------------------------------------------------

################################################################
class MainApp(rcp.app.MainApp):
    """Main application controller object holding any non-GUI related state.

    :param custom_controller_class: a class object instanced once per double-pendulum model to create a motion controller
    """

    def __init__(self, custom_controller_class):
        log.debug("Entering MainApp.__init__")

        # rcp.app.MainApp initialization, including the creation of the self.config object.
        super().__init__()

        # Load the configuration if available; this allows basic window setup to be specified.
        self.load_configuration()

        # Create the interface window.
        self.window = AppWindow(self)

        # Create and initialize top-level objects.
        self.controller = custom_controller_class()
        self.simulator = rcp.doublependulum.DoublePendulumSimulator()
        self.simulator.connect_controller(self.controller)
        self.controller.connect_console(self.window)
        
        # self.simulator.state[0] = 3.14
        # self.simulator.state[0] = 3.14
        
        # Finish connecting the window callbacks.
        self.window.connect_callbacks()

        # Finish preparing the user controller object.
        self.controller.setup()
        
        # Start the graphics animation timer.
        self.frame_interval = 0.040
        self.frame_timer = QtCore.QTimer()
        self.frame_timer.start(1000*self.frame_interval)  # units are milliseconds
        self.frame_timer.timeout.connect(self.frame_timer_tick)

        return

    # ---- configuration management -------------------------------------------------
    def initialize_default_configuration(self):
        # Extend the default implementation to add application-specific defaults.
        super().initialize_default_configuration()
        self.config['log'] = {}
        return

    def save_configuration(self, path=None):
        # Extend the default implementation to gather up configuration values.
        self.window.gather_configuration(self.config)
        self.controller.gather_configuration(self.config)        
        try:
            super().save_configuration(path)
        except PermissionError:
            log.warning("Unable to write configuration to %s", self.configuration_file_path)

    def apply_configuration(self):
        self.window.apply_user_configuration(self.config)
        self.controller.apply_configuration(self.config)
        
    # ---- application event handlers -----------------------------------------------
    def app_has_started(self):
        super().app_has_started()
        self.apply_configuration()

    def app_is_exiting(self):
        #
        # hardware and network connections should be closed here
        #
        super().app_is_exiting()

    #--- generate graphics animation updates ---------------------------------------------------
    def frame_timer_tick(self):
        # Method called at intervals by the animation timer to update the model and graphics.
        self.simulator.timer_tick(self.frame_interval)
        # self.window.mainText.appendPlainText("Time: %f  State: %s" % (self.simulator.t, str(self.simulator.state)))

        self.window.pendulum.update_positions(self.simulator.state)
        self.window.state_display.setText("Angles: %5.2f %5.2f" % tuple(self.simulator.state[0:2]))
        self.window.view.repaint()

        self.window.config_data[0:-1] = self.window.config_data[1:]

        # map the configuration space location to [-pi, pi] on each axis
        self.window.config_data[-1,:] = np.mod(np.pi + self.simulator.state[0:2], 2*np.pi) - np.pi

        # update the most recent point of the configuration space plot
        # self.window.config_curve.setData(self.window.config_data)
        self.window.config_plot.setData(x=self.window.config_data[:,0], y=self.window.config_data[:,1])
        
        # self.window.cartoon.update_positions(self.simulator.state)        
        # self.window.cartoon.repaint()
        return


################################################################
def main(custom_controller_class):
    # temporary increase in debugging output
    # rcp.app.add_console_log_handler()

    # capture log messages generated before the window opens
    mem_log_handler = rcp.app.add_memory_log_handler()

    # initialize the Qt system itself
    app = QtWidgets.QApplication(sys.argv)

    # create the main application controller
    main = MainApp(custom_controller_class)

    # finish the memory handler
    main.window.logDisplay.flush_and_remove_memory_handler(mem_log_handler)

    # Send a signal to be received after the application event loop starts.
    QtCore.QTimer.singleShot(0, main.app_has_started)

    # run the event loop until the user is done
    log.info("Starting event loop.")
    sys.exit(app.exec_())


################################################################
