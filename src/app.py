# gradio-experiments: A collection of feature experiments with Gradio
# Copyright (C) 2024 Anirban Basu

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
import platform
import gradio as gr

from dotenv import load_dotenv
from data import StateData
from utils import EnvironmentVariables, parse_env

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


class GradioApp:
    """The main Gradio application class."""

    BROWSER_STATE_UNINITIALISED_MSG = (
        "uninitialised, click 'Change browser state' to initialise"
    )

    def __init__(self):
        # This is a safe global variable because it remains the same for all users and is never modified.
        self.app_name = "gradio-experiments"
        self.state_key = f"{self.app_name}-local-state"

        self.global_state = StateData()

    def component_text_transformation(self) -> gr.Group:
        """This is a placeholder component for text transformation."""
        with gr.Group() as component:
            with gr.Row(equal_height=True):
                with gr.Column():
                    input_text = gr.Textbox(
                        lines=5,
                        label="Input text",
                        info="Enter the text here to see it transformed in the output.",
                    )
                    gr.Examples(
                        label="Choose an example or type your own input text above.",
                        examples=[
                            "Hello, World!",
                            "This is a test.",
                            "This is a slightly longer sentence: how does the weather seem like today?",
                        ],
                        example_labels=[
                            "The usual hello world.",
                            "A test sentence.",
                            "A longer sentence.",
                        ],
                        inputs=[input_text],
                    )
                output_text = gr.Textbox(
                    lines=8,
                    label="Output text",
                    info="The transformed text will be displayed here. Current transformation: uppercase.",
                )

            @input_text.change(
                inputs=[input_text],
                outputs=[output_text],
                trigger_mode="always_last",
                api_name="text_to_titlecase",
            )
            def text_to_uppercase(text: str) -> str:
                return text.upper()

        return component

    def component_state_management(self) -> gr.Group:
        """This is a component to demonstrate state management."""
        with gr.Group() as component:
            session_state = gr.State(
                StateData(an_object=self.global_state.an_object),
            )
            browser_state = gr.BrowserState(
                # default_value=StateData(an_object=self.global_state.an_object),
                storage_key=self.state_key,
                secret=parse_env(EnvironmentVariables.LOCAL_STORAGE_ENCRYPTION_KEY),
            )
            with gr.Row(equal_height=True):
                json_global_state = gr.JSON(
                    value=self.global_state.__dict__,
                    label="Global state",
                    max_height=300,
                )
                json_session_state = gr.JSON(
                    value=session_state.value.__dict__,
                    label="Session state",
                    max_height=300,
                )
                json_browser_state = gr.JSON(
                    value=None,
                    label="Browser state",
                    max_height=300,
                )
            label_task_output = gr.Label(
                label="Task output",
            )
            with gr.Row(equal_height=True):
                btn_change_global_state = gr.Button(
                    value="Change global state",
                    variant="primary",
                )
                btn_change_session_state = gr.Button(
                    value="Change session state",
                    variant="secondary",
                )
                btn_change_browser_state = gr.Button(
                    value="Change browser state",
                    variant="huggingface",
                )
                btn_refresh_states = gr.Button(
                    value="Refresh states",
                    variant="stop",
                )

        @btn_change_global_state.click(
            inputs=[browser_state],
            outputs=[json_global_state, label_task_output],
            api_name="change_global_state",
        )
        def change_global_state(browser_state_value: str):
            self.global_state.make_random_changes("global")
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            return (
                self.global_state.__dict__,
                {
                    f"global: {self.global_state.an_object.task_output}": 1.0,
                    f"session: {session_state.value.an_object.task_output}": 1.0,
                    f"browser: {browser_state_obj.an_object.task_output if browser_state_value else GradioApp.BROWSER_STATE_UNINITIALISED_MSG}": 1.0,
                },
            )

        @btn_change_session_state.click(
            inputs=[session_state],
            outputs=[session_state],
            api_name="change_session_state",
        )
        def change_session_state(session_state_value: StateData):
            session_state_value.make_random_changes("session")
            return gr.update(value=session_state_value)

        @session_state.change(
            inputs=[session_state, browser_state],
            outputs=[json_session_state, label_task_output],
            api_name=False,
        )
        def session_state_change_event(
            session_state_value: StateData, browser_state_value: str
        ):
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            return (
                session_state_value.__dict__,
                {
                    f"global: {self.global_state.an_object.task_output}": 1.0,
                    f"session: {session_state_value.an_object.task_output}": 1.0,
                    f"browser: {browser_state_obj.an_object.task_output if browser_state_value else GradioApp.BROWSER_STATE_UNINITIALISED_MSG}": 1.0,
                },
            )

        @btn_change_browser_state.click(
            inputs=[browser_state],
            outputs=[browser_state, json_browser_state, label_task_output],
            api_name="change_browser_state",
        )
        def change_browser_state(browser_state_value: str):
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            browser_state_obj.make_random_changes("browser")
            return (
                gr.update(value=browser_state_obj),
                browser_state_obj.__dict__,
                {
                    f"global: {self.global_state.an_object.task_output}": 1.0,
                    f"session: {session_state.value.an_object.task_output}": 1.0,
                    f"browser: {browser_state_obj.an_object.task_output if browser_state_value else GradioApp.BROWSER_STATE_UNINITIALISED_MSG}": 1.0,
                },
            )

        @btn_refresh_states.click(
            inputs=[session_state, browser_state],
            outputs=[
                json_global_state,
                json_session_state,
                json_browser_state,
                label_task_output,
            ],
            api_name="refresh_states",
        )
        def refresh_states(session_state_value: StateData, browser_state_value: str):
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            return (
                self.global_state.__dict__,
                session_state_value.__dict__,
                (browser_state_obj.__dict__ if browser_state_value else None),
                {
                    f"global: {self.global_state.an_object.task_output}": 1.0,
                    f"session: {session_state_value.an_object.task_output}": 1.0,
                    f"browser: {browser_state_obj.an_object.task_output if browser_state_value else GradioApp.BROWSER_STATE_UNINITIALISED_MSG}": 1.0,
                },
            )

        return component

    def construct_ui(self) -> gr.Blocks:
        with gr.Blocks(
            title=self.app_name,
            fill_height=True,
            fill_width=True,
            analytics_enabled=False,
        ) as ui:
            gr.Markdown(
                f"""
                # gradio-experiments

                A collection of feature experiments with Gradio.

                 - Gradio version: _{gr.get_package_version()}_
                 - Python version: _{sys.version}_
                 - Platform: _{platform.version()}_
                 - GitHub repository: _[gradio-experiments](https://github.com/anirbanbasu/gradio-experiments)_
                """
            )
            with gr.Tab(label="State management"):
                with gr.Accordion(label="Explanation", open=True):
                    gr.Markdown(
                        f"""
                        This component demonstrates the management of global state, session state (using `gr.State`) and browser state (using `gr.BrowserState`).

                        ## Expected behaviour

                        - **Global state**: The global state is shared across all web sessions. Modifications to the global state are reflected in all sessions.
                        - **Session state**: The session state is specific to the user's browser session. The session state is not shared across different browser sessions and lost when the browser window is closed or the page is refreshed.
                        - **Browser state**: The browser state is stored in the browser's local storage. It is not shared across different browsers but shared across multiple windows of the same browser. The browser state persists even when the browser window is closed or the page is refreshed.

                        **Note**: If you want the browser state to be cleared, you must clear the key named `{self.state_key}` from the browser's local storage.

                        ## Try it out
                        1. Open this page in two different browsers, not just browser tabs.
                        2. Change the global state in one browser (by clicking the 'Change global state' button) and see the changes reflected in the other browser (by clicking the 'Refresh states' button).
                        3. Change the session state in one browser (by clicking the 'Change session state' button) and see that the changes are **not** reflected in the other browser (by clicking the 'Refresh states' button). It **will be lost** if the browser window is closed or the page is refreshed.
                        4. Change the browser state in one browser (by clicking the 'Change browser state' button) and see that the changes are **not** reflected in the other browser (by clicking the 'Refresh states' button). Close one browser and re-open it, click the 'Refresh states' button to see that the browser state has been persisted.

                        Notice that the 'Task output' is the result of a task performed by an object, which is maintained as a reference in the global and session and browser states. Thus, the task output is shared across all sessions even whether it is triggered by a global state change or a session state change or a browser state change.
                        """
                    )
                self.component_state_management()

            with gr.Tab(label="Text transformations"):
                self.component_text_transformation()

        return ui


if __name__ == "__main__":
    app = GradioApp()
    ic(load_dotenv())
    app.construct_ui().queue().launch(server_name="0.0.0.0", share=False)
