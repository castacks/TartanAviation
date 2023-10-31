import rospy
import roslaunch
import subprocess

is_running = True
LAUNCH_FILE = "/home/mhi/saa_ws/src/deepstream_ros/launch/kagc.launch"
ARGUS_RESTART_SLEEP_SECS = 5
LAUNCH_SHUTDOWN_SLEEP_SECS = 15

def restart_argus_daemon():
    command = ['sudo', '-S', 'service', 'nvargus-daemon', 'restart']
    subprocess.Popen(command, 
                     stdin=subprocess.PIPE, 
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE).communicate(input=b'passme24\n')


class ProcessListener(roslaunch.pmon.ProcessListener):
    global is_running

    def process_died(self, name, exit_code):
        global is_running
        is_running = False
        rospy.logwarn("%s died with code %s", name, exit_code)


class IMXCameraLogging:
    def __init__(self, launch_file=LAUNCH_FILE):
        self.launch_file = launch_file
        self.launch = None
        self.recording = False
    
    def start_recording(self):
        if not self.recording:
            restart_argus_daemon()
            rospy.sleep(ARGUS_RESTART_SLEEP_SECS)
            self.launch = self.init_launch(self.launch_file, ProcessListener())
            self.launch.start()
            self.recording = True

    def stop_recording(self):
        if self.recording:
            self.launch.shutdown()
            rospy.sleep(LAUNCH_SHUTDOWN_SLEEP_SECS)
            self.recording = False

    def init_launch(self, launchfile, process_listener):
        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)
        launch = roslaunch.parent.ROSLaunchParent(
            uuid,
            [launchfile],
            process_listeners=[process_listener],
        )
        return launch


if __name__ == "__main__":
    camera_recorder = IMXCameraLogging()
    camera_recorder.start_recording()

    rospy.sleep(10)

    camera_recorder.stop_recording()