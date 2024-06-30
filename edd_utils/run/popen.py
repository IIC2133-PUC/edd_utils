import subprocess
import os
import signal

try:
    os.wait4
except AttributeError:
    raise ImportError("`os.wait4` is not available on this platform. Use a Unix-like OS.")


def alarm_timeout_signaled(signum, frame):
    raise TimeoutError()


class PopenWithWait4(subprocess.Popen):
    def wait4(self, *, timeout: int | None = None, options=0):
        """Wait for child process to terminate; returns (return_code, resource_usage)."""
        prev_handler = signal.signal(signal.SIGALRM, alarm_timeout_signaled)

        # TODO: change alarm timeout to a busy loop and pass no-hang option to wait4

        try:
            _, self.returncode, resource_usage = os.wait4(self.pid, options)
            if timeout is not None:
                signal.alarm(timeout)
        except (TimeoutError, KeyboardInterrupt):
            self.kill()
            _, self.returncode, resource_usage = os.wait4(self.pid, options)
        finally:
            if timeout is not None:
                signal.alarm(0)

        signal.signal(signal.SIGALRM, prev_handler)
        return self.returncode, resource_usage
