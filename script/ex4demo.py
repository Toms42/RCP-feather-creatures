"""Demonstration script class for exercise4.py showing a self-contained process
for sequencing events over time.  The inputs and outputs are deliberately
constrained to message queues to preclude synchronization problems and maintain
compatibility with network communication.
"""

################################################################
# Written in 2019 by Garth Zeglin <garthz@cmu.edu>

# To the extent possible under law, the author has dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.

# You should have received a copy of the CC0 Public Domain Dedication along with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

################################################################

import time, queue
import rcp.script

class ScriptStopException(Exception):
    pass

class Ex4DemoScript(rcp.script.Script):
    
    def __init__(self):
        super().__init__()
        return
    
    def sleep_unless_stop(self, duration):
        """Sleep for a given duration unless the user issues a stop command."""
        start = time.time()
        now = start
        while True:
            try:
                timeout = (start+duration-now)
                if timeout < 0:
                    return
                command = self.input.get(block=True, timeout=timeout)
                # if a message is received, ignore it unless it is the stop command
                if command[0] == 'console' and command[1] == 'stop':
                    self.write("User requested stop.")
                    raise ScriptStopException
                self.write("sleep_unless_stop ignoring message " + repr(command))
                now = time.time()
                
            except queue.Empty:
                # if the queue get timed out, the sleep is over
                return
        
    def script_task(self):
        """Entry point for the script to run on a background thread."""
        self.write("Ex4Demo script thread waking up.")

        # top-level event loop to wait for a play or reset command
        while True:
            command = self.input.get()
            if command[0] == 'console':
                self.write("Script thread received command: %s" % command[1])
                if command[1] == 'reset':
                    self.send_reset_cue()
                    
                elif command[1] == 'play':
                    try:
                        while True:
                            self.sequence()
                    except ScriptStopException:
                        self.write('Script sequence stopped.')
                elif command[1][1] == 'r':
                    self.write('posing right arm')
                    self.send_pose_r(command[1][2:])
                elif command[1][1] == 'l':
                    self.left('posing left arm')
                    self.send_pose_l(command[2][2:])
                else:
                    self.send_pose(command[1])

    def send_cue(self, *args):
        self.output.put(('cue',) + args)
        self.write('Issuing cue: ' + repr(args))
        return

    def send_pose(self, name):
        self.send_cue('pose',name)

    def send_pose_r(self, name):
        self.send_cue('pose0',name)

    def send_pose_l(self, name):
        self.send_cue('pose1',name)
        
    def send_reset_cue(self):
        self.write("Sending reset cue.")
        self.send_cue('gains', 0.5, 1.0)
        self.send_cue('pose', 'reset')
        self.send_cue('random', False)
        self.send_cue('tempo', 60.0)
        self.send_cue('magnitude', 1.0)
        return
        
    def sequence(self):
        """Demonstration sequence.  This could be decomposed further into subroutines."""
        
        self.write("Script starting.")
        self.send_cue('gains', 0.5, 1.0)        
        self.send_pose('pose2')
        self.sleep_unless_stop(1)

        self.send_pose('pose1')
        self.sleep_unless_stop(1)

        self.send_pose('pose2')
        self.sleep_unless_stop(1)

        self.send_pose('pose3')
        self.sleep_unless_stop(1)

        self.send_pose('pose4')
        self.sleep_unless_stop(1)

        self.send_pose('pose5')
        self.sleep_unless_stop(1)
        
        self.send_pose('pose6')
        self.sleep_unless_stop(1)

        self.send_pose('pose7')
        self.sleep_unless_stop(1)

        self.send_pose('pose8')
        self.sleep_unless_stop(1)

        self.write("Script done.")
        return

################################################################
        
