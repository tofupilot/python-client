import types
from typing import Optional
from time import sleep
import threading
import asyncio

import json
from openhtf import Test
from openhtf.util import data

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from .upload import upload
from ..client import TofuPilotClient


def _get_executing_test():
    """Get the currently executing test and its state."""
    tests = list(Test.TEST_INSTANCES.values())

    if not tests:
        return None, None

    if len(tests) > 1:
        pass

    test = tests[0]
    test_state = test.state

    if test_state is None:
        return None, None

    return test, test_state


def _to_dict_with_event(test_state):
    """Process a test state into the format we want to send to the frontend."""
    original_dict, event = test_state.asdict_with_event()

    # This line may produce a 'dictionary changed size during iteration' error.
    test_state_dict = data.convert_to_base_types(original_dict)

    test_state_dict["execution_uid"] = test_state.execution_uid
    return test_state_dict, event


class SimpleStationWatcher(threading.Thread):
    """
    Simplified watcher that detects phase changes and sends test state updates.
    """

    def __init__(self, send_update_callback):
        super().__init__(daemon=True)
        self.send_update = send_update_callback
        self.last_phase = None
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            _, test_state = _get_executing_test()
            if test_state is not None:
                current_phase = (
                    test_state.running_phase_state.name
                    if test_state.running_phase_state
                    else None
                )
                if current_phase != self.last_phase:
                    test_state_dict, _ = _to_dict_with_event(test_state)
                    self.send_update(test_state_dict)
                    self.last_phase = current_phase
            sleep(0.1)  # Wait for 100 milliseconds

    def stop(self):
        self.stop_event.set()

def execute_with_graceful_exit(test, test_start=None):
    """Execute a test with graceful handling of KeyboardInterrupt.
    
    This is a helper function that wraps the OpenHTF test.execute method
    to ensure clean termination when Ctrl+C is pressed.
    
    Args:
        test: The OpenHTF test to execute
        test_start: The test_start parameter to pass to test.execute
        
    Returns:
        The test result from test.execute, or None if interrupted
    """
    try:
        # Set up Ctrl+C handler to show message immediately
        import signal
        
        def immediate_interrupt_handler(sig, frame):
            print("\nTest execution interrupted by user.")
            print("Test was interrupted. Exiting gracefully.")
            # Let the KeyboardInterrupt propagate
            raise KeyboardInterrupt()
            
        # Store the original handler to restore later
        original_handler = signal.getsignal(signal.SIGINT)
        # Set our immediate message handler
        signal.signal(signal.SIGINT, immediate_interrupt_handler)
        
        try:
            return test.execute(test_start=test_start)
        finally:
            # Restore the original handler
            signal.signal(signal.SIGINT, original_handler)
    except KeyboardInterrupt:
        # KeyboardInterrupt has already been handled with immediate message
        return None
    except AttributeError as e:
        if "'NoneType' object has no attribute 'name'" in str(e):
            # This happens when KeyboardInterrupt is caught by OpenHTF
            # but the test state isn't properly set
            return None
        raise  # Re-raise any other AttributeError


class TofuPilot:
    """
    Context manager to automatically add an output callback to the running OpenHTF test
    and live stream it's execution.


    ### Usage Example:

    ```python
    from openhtf import Test
    from tofupilot import TofuPilot

    #...

    def main():
        test = Test(*your_phases, procedure_id="FVT1")

        # Stream real-time test execution data to TofuPilot
        with TofuPilot(test):
            # For more reliable Ctrl+C handling, use the helper function:
            execute_with_graceful_exit(test, test_start=lambda: "SN15")
            
            # Or use the standard method (may show errors on Ctrl+C):
            # test.execute(lambda: "SN15")
    ```
    """

    def __init__(
        self,
        test: Test,
        stream: Optional[bool] = True,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self.test = test
        self.stream = stream
        self.client = TofuPilotClient(api_key=api_key, url=url)
        self.api_key = api_key
        self.url = url
        self.watcher = None
        self.shutdown_event = threading.Event()
        self.update_task = None
        self.mqttClient = None
        self.publishOptions = None
        self._logger = self.client._logger

    def __enter__(self):
        self.test.add_output_callbacks(
            upload(api_key=self.api_key, url=self.url, client=self.client)
        )

        if self.stream:
            try:
                cred = self.client.get_connection_credentials()

                if not cred:
                    self._logger.warning("Stream: Auth server connection failed")
                    return self

                # Since we control the server, we know these will be set
                token = cred["token"]
                operatorPage = cred["operatorPage"]
                clientOptions = cred["clientOptions"]
                willOptions = cred["willOptions"]
                connectOptions = cred["connectOptions"]
                self.publishOptions = cred["publishOptions"]
                subscribeOptions = cred["subscribeOptions"]

                self.mqttClient = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, **clientOptions)

                self.mqttClient.tls_set()

                self.mqttClient.will_set(**willOptions)
                
                self.mqttClient.username_pw_set("pythonClient", token)
                
                self.mqttClient.on_message = self._on_message
                self.mqttClient.on_disconnect = self._on_disconnect
                self.mqttClient.on_unsubscribe = self._on_unsubscribe

                connect_error_code = self.mqttClient.connect(**connectOptions)
                if(connect_error_code != mqtt.MQTT_ERR_SUCCESS):
                    self._logger.warning(f"Stream: Connect failed (code {connect_error_code})")
                    return self
                
                subscribe_error_code, messageId = self.mqttClient.subscribe(**subscribeOptions)
                if(subscribe_error_code != mqtt.MQTT_ERR_SUCCESS):
                    self._logger.warning(f"Stream: Subscribe failed (code {subscribe_error_code})")
                    return self

                self.mqttClient.loop_start()

                self.watcher = SimpleStationWatcher(self._send_update)
                self.watcher.start()
                
                # Create clickable URL similar to the prompt format
                import sys
                try:
                    # Use ANSI escape sequence for clickable link
                    clickable_url = f"\033]8;;{operatorPage}\033\\TofuPilot Operator UI\033]8;;\033\\"
                    sys.stdout.write(f"\033[0;32mConnected to {clickable_url}\033[0m\n")
                    sys.stdout.flush()
                except:
                    # Fallback for terminals that don't support ANSI
                    self._logger.success(f"Connected to TofuPilot: {operatorPage}")
                
            except Exception as e:
                self._logger.warning(f"Stream: Setup error - {e}")
            

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Clean up resources when exiting the context manager.
        
        This method handles proper cleanup even in the case of KeyboardInterrupt
        or other exceptions to ensure resources are released properly.
        """
        # Log the exit reason if it's due to an exception
        if exc_type is not None:
            self._logger.info(f"Exiting TofuPilot context due to {exc_type.__name__}")
            
            # Handle KeyboardInterrupt specifically
            if exc_type is KeyboardInterrupt:
                self._logger.info("Test execution interrupted by user (Ctrl+C)")
        
        # Stop the StationWatcher
        if self.watcher:
            try:
                self.watcher.stop()
                self.watcher.join(timeout=2.0)  # Add timeout to prevent hanging
            except Exception as e:
                self._logger.warning(f"Error stopping watcher: {e}")

        # Clean up MQTT connection
        if self.mqttClient:
            try:
                # Doesn't wait for publish operation to stop, this is fine since __exit__ is only called after the run was imported
                self.mqttClient.loop_stop()
                self.mqttClient.disconnect()
            except Exception as e:
                self._logger.warning(f"Error disconnecting MQTT client: {e}")
            finally:
                self.mqttClient = None
        
        # Return False to allow any exception to propagate, unless it's a KeyboardInterrupt
        # In case of KeyboardInterrupt, return True to suppress the exception
        return exc_type is KeyboardInterrupt

    def _send_update(self, message):
        self.mqttClient.publish(
            payload=json.dumps(
                {"action": "send", "source": "python", "message": message}
            ),
            **self.publishOptions
        )
        
    def _handle_answer(self, plug_name, method_name, args):
        _, test_state = _get_executing_test()

        if test_state is None:
            self._logger.warning("Stream: No running test found")
            return

        # Find the plug matching `plug_name`.
        plug = test_state.plug_manager.get_plug_by_class_path(plug_name)
        if plug is None:
            self._logger.warning(f"Stream: Plug not found - {plug_name}")
            return

        method = getattr(plug, method_name, None)

        if not (plug.enable_remote and isinstance(method, types.MethodType) and
                not method_name.startswith('_') and
                method_name not in plug.disable_remote_attrs):
            self._logger.warning(f"Stream: Method not found - {plug_name}.{method_name}")
            return

        try:
            # side-effecting !
            method(*args)
        except Exception as e:  # pylint: disable=broad-except
            self._logger.warning(f"Stream: Method call failed - {method_name}({', '.join(args)}) - {e}")
    
    def _on_message(self, client, userdata, message):
        parsed = json.loads(message.payload)
        
        if parsed["source"] == "web":
            self._handle_answer(**parsed["message"])

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        if reason_code != mqtt.MQTT_ERR_SUCCESS:
            self._logger.warning(f"Stream: Unexpected disconnect (code {reason_code})")

    def _on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        if any(reason_code != mqtt.MQTT_ERR_SUCCESS for reason_code in reason_code_list):
            self._logger.warning(f"Stream: Partial disconnect (codes {reason_code_list})")