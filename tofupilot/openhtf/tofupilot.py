import types
from typing import Optional
from time import sleep
import threading

import json
from openhtf import Test
from openhtf.util import data

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from openhtf.core.test_record import TestRecord
from openhtf.core.test_state import TestState

from .upload import upload
from .custom_prompt import patch_openhtf_prompts
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


def _to_dict_with_event(test_state: TestState):
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


class TofuPilot:
    """
    Context manager to automatically add an output callback to the running OpenHTF test
    and live stream it's execution to the Operator UI.


    ### Usage Example:

    ```python
    from openhtf import Test
    from tofupilot import TofuPilot

    #...

    def main():
        test = Test(*your_phases, procedure_id="FVT1")

        # Stream real-time test execution data to TofuPilot Operator UI
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
        stream: Optional[bool] = True,  # Controls connection to Operator UI
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
        self._streaming_setup_thread = None

    def __enter__(self):
        # Add upload callback without pausing the logger yet
        self.test.add_output_callbacks(
            upload(api_key=self.api_key, url=self.url, client=self.client),
            self._final_update,
        )

        # Start streaming setup before pausing the logger
        if self.stream:
            self.connection_completed = False

            # Start connection in a separate thread with 1s timeout
            self._streaming_setup_thread = threading.Thread(
                target=self._setup_streaming_with_state, daemon=True
            )
            self._streaming_setup_thread.start()
            self._streaming_setup_thread.join(1.0)

        # Pause logger after connection attempt is either completed or timed out
        self._logger.pause()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Clean up resources when exiting the context manager.

        This method handles proper cleanup even in the case of KeyboardInterrupt
        or other exceptions to ensure resources are released properly.
        """
        self._logger.resume()

        # Handle ongoing connection attempt
        if self._streaming_setup_thread and self._streaming_setup_thread.is_alive():
            if (
                not hasattr(self, "connection_completed")
                or not self.connection_completed
            ):
                self._logger.warning(f"Operator UI: Connection still in progress")
            self._streaming_setup_thread.join(timeout=3.0)
            if self._streaming_setup_thread.is_alive():
                self._logger.warning(f"Operator UI: Connection timed out")

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

    # Operator UI-related methods

    def _setup_streaming_with_state(self):
        """Run the streaming setup and track connection completion state."""
        self._setup_streaming()
        self.connection_completed = True

    def _setup_streaming(self):
        try:
            try:
                cred = self.client.get_connection_credentials()
            except Exception as e:
                self._logger.warning(f"Operator UI: JWT error: {e}")
                # Print with yellow color for consistency with warnings
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(
                    f"{yellow}To disable Operator UI streaming, use Test(..., stream=False) in your script{reset}"
                )
                self.stream = False  # Disable streaming on auth failure
                return

            if not cred:
                self._logger.warning("Operator UI: Auth server connection failed")
                # Print with yellow color for consistency with warnings
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(
                    f"{yellow}To disable Operator UI streaming, use Test(..., stream=False) in your script{reset}"
                )
                self.stream = False  # Disable streaming on auth failure
                return self

            # Since we control the server, we know these will be set
            token = cred["token"]
            operatorPage = cred["operatorPage"]
            clientOptions = cred["clientOptions"]
            willOptions = cred["willOptions"]
            connectOptions = cred["connectOptions"]
            self.publishOptions = cred["publishOptions"]
            subscribeOptions = cred["subscribeOptions"]

            self.mqttClient = mqtt.Client(
                callback_api_version=CallbackAPIVersion.VERSION2, **clientOptions
            )

            # This is not 100% reliable, hence the need to put the setup in the background
            # See https://github.com/eclipse-paho/paho.mqtt.python/issues/890
            self.mqttClient.connect_timeout = 1.0

            self.mqttClient.tls_set()

            self.mqttClient.will_set(**willOptions)

            self.mqttClient.username_pw_set("pythonClient", token)

            self.mqttClient.on_message = self._on_message
            self.mqttClient.on_disconnect = self._on_disconnect
            self.mqttClient.on_unsubscribe = self._on_unsubscribe

            try:
                connect_error_code = self.mqttClient.connect(**connectOptions)
            except Exception as e:
                self._logger.warning(
                    f"Operator UI: Failed to connect with server (exception): {e}"
                )
                # Print with yellow color for consistency with warnings
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(
                    f"{yellow}To disable Operator UI streaming, use Test(..., stream=False) in your script{reset}"
                )
                self.stream = False  # Disable streaming on connection failure
                return

            if connect_error_code != mqtt.MQTT_ERR_SUCCESS:
                self._logger.warning(
                    f"Operator UI: Failed to connect with server (error code): {connect_error_code}"
                )
                # Print with yellow color for consistency with warnings
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(
                    f"{yellow}To disable Operator UI streaming, use Test(..., stream=False) in your script{reset}"
                )
                self.stream = False  # Disable streaming on connection failure
                return self

            try:
                subscribe_error_code, messageId = self.mqttClient.subscribe(
                    **subscribeOptions
                )
            except Exception as e:
                self._logger.warning(
                    f"Operator UI: Failed to subscribe to server (exception): {e}"
                )
                # Print with yellow color for consistency with warnings
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(
                    f"{yellow}To disable Operator UI streaming, use Test(..., stream=False) in your script{reset}"
                )
                self.stream = False  # Disable streaming on subscription failure
                return

            if subscribe_error_code != mqtt.MQTT_ERR_SUCCESS:
                self._logger.warning(
                    f"Operator UI: Failed to subscribe to server (error code): {subscribe_error_code}"
                )
                # Print with yellow color for consistency with warnings
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(
                    f"{yellow}To disable Operator UI streaming, use Test(..., stream=False) in your script{reset}"
                )
                self.stream = False  # Disable streaming on subscription failure
                return self

            self.mqttClient.loop_start()

            self.watcher = SimpleStationWatcher(self._send_update)
            self.watcher.start()

            # Apply the patch to OpenHTF prompts to include the TofuPilot URL
            patch_openhtf_prompts(operatorPage)

            # Show connection status message with URL
            try:
                # Use ANSI escape sequence for clickable link
                green = "\033[0;32m"
                reset = "\033[0m"

                # Create clickable URL
                clickable_url = (
                    f"\033]8;;{operatorPage}\033\\{operatorPage}\033]8;;\033\\"
                )

                # Print single line connection message with URL
                print(f"\n{green}Connected to TofuPilot real-time server{reset}")
                print(f"{green}Access Operator UI: {clickable_url}{reset}\n")
            except:
                # Fallback for terminals that don't support ANSI
                self._logger.success(f"Connected to TofuPilot real-time server")
                self._logger.success(f"Access Operator UI: {operatorPage}")

        except Exception as e:
            self._logger.warning(f"Operator UI: Setup error - {e}")
            print(
                "To disable Operator UI streaming, use Test(..., stream=False) in your script"
            )
            self.stream = False  # Disable streaming on any setup error

    def _send_update(self, message):
        # Skip publishing if streaming is disabled or client is None
        if not self.stream or self.mqttClient is None:
            return

        try:
            self.mqttClient.publish(
                payload=json.dumps(
                    {"action": "send", "source": "python", "message": message}
                ),
                **self.publishOptions,
            )
        except Exception as e:
            self._logger.warning(
                f"Operator UI: Failed to publish to server (exception): {e}"
            )
            self.stream = False  # Disable streaming on publish failure
            return

    def _handle_answer(self, plug_name, method_name, args):
        _, test_state = _get_executing_test()

        if test_state is None:
            self._logger.warning("Operator UI: No running test found")
            return

        # Find the plug matching `plug_name`.
        plug = test_state.plug_manager.get_plug_by_class_path(plug_name)
        if plug is None:
            self._logger.warning(f"Operator UI: Plug not found - {plug_name}")
            return

        method = getattr(plug, method_name, None)

        if not (
            plug.enable_remote
            and isinstance(method, types.MethodType)
            and not method_name.startswith("_")
            and method_name not in plug.disable_remote_attrs
        ):
            self._logger.warning(
                f"Operator UI: Method not found - {plug_name}.{method_name}"
            )
            return

        try:
            # side-effecting !
            method(*args)
        except Exception as e:  # pylint: disable=broad-except
            self._logger.warning(
                f"Operator UI: Method call failed - {method_name}({', '.join(args)}) - {e}"
            )

    def _final_update(self, testRecord: TestRecord):
        """
        If the test is fast enough, the watcher never triggers, to avoid the UI being out of sync,
        we force send at least once at the very end of the test
        """

        # Skip if streaming is disabled or MQTT client doesn't exist
        if not self.stream or self.mqttClient is None:
            return

        test_record_dict = testRecord.as_base_types()

        test_state_dict = {
            "status": "COMPLETED",
            "test_record": test_record_dict,
            "plugs": {"plug_states": {}},
            "running_phase_state": {},
        }

        self._send_update(test_state_dict)

    # Operator UI-related callbacks

    def _on_message(self, client, userdata, message):
        parsed = json.loads(message.payload)

        if parsed["source"] == "web":
            self._handle_answer(**parsed["message"])

    def _on_disconnect(
        self, client, userdata, disconnect_flags, reason_code, properties
    ):
        if reason_code != mqtt.MQTT_ERR_SUCCESS:
            self._logger.warning(
                f"Operator UI: Unexpected disconnect (code {reason_code})"
            )

    def _on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        if any(
            reason_code != mqtt.MQTT_ERR_SUCCESS for reason_code in reason_code_list
        ):
            self._logger.warning(
                f"Operator UI: Partial disconnect (codes {reason_code_list})"
            )
