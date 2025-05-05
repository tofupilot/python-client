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
            test.execute(lambda: "SN15")
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
                
                self._logger.success(f"Stream: Started at:\n{operatorPage}")
                
            except Exception as e:
                self._logger.warning(f"Stream: Setup error - {e}")
            

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Stop the StationWatcher
        if self.watcher:
            self.watcher.stop()
            self.watcher.join()

        if self.mqttClient:
            # Doesn't wait for publish operation to stop, this is fine since __exit__ is only called after the run was imported
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            self.mqttClient = None

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