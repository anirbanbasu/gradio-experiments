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
from typing import Dict, List, Optional
import gradio as gr
from pydantic import BaseModel, Field
import datetime
import random
import copy

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


class SomePydanticModel(BaseModel):
    """An example Pydantic model."""

    a: int = Field(..., description="An integer field.")
    b: str = Field(..., description="A string field.")
    c: Optional[List[int]] = Field(default=[], description="A list of integers.")


class SomeTask:
    """An example class that performs a task."""

    def __init__(self):
        self.task_output = "task-not-executed"

    def do_task(self):
        self.task_output = f"task-done: {datetime.datetime.now()}"


class StateData:
    """A class to hold the state data for the application."""

    def __init__(self, create_uninitialised: bool = False, an_object: SomeTask = None):
        """
        Create a new instance of the StateData class.

        Args:
            create_uninitialised (bool): Whether to create the object with uninitialised values. Defaults to False.
            an_object (SomeTask): An instance of the SomeTask class. Defaults to None. Specifying this has no effect if create_uninitialised is True.
        """

        if not create_uninitialised:
            self.a_pydantic_object = SomePydanticModel(a=1, b="default", c=[1, 2, 3, 4])
            self.an_object = SomeTask() if an_object is None else an_object
            self.a_list: List[SomePydanticModel] = []
            self.a_dict: Dict[str, SomePydanticModel] = {}
        else:
            self.a_list: List[SomePydanticModel] = None
            self.a_dict: Dict[str, SomePydanticModel] = None
            self.a_pydantic_object = None
            self.an_object = None

    def __iter__(self):
        """Make the object JSON serializable by converting it into a dictionary."""
        return iter(self.to_dict().items())

    def to_dict(self):
        """Converts the object into a dictionary representation."""
        return {
            "a_pydantic_object": (
                self.a_pydantic_object.model_dump() if self.a_pydantic_object else None
            ),
            "an_object": str(self.an_object) if self.an_object else None,
            "a_list": (
                [item.model_dump() for item in self.a_list] if self.a_list else None
            ),
            "a_dict": (
                {k: v.model_dump() for k, v in self.a_dict.items()}
                if self.a_dict
                else None
            ),
        }

    def __getitem__(self, key):
        """Allow dictionary-style access."""
        return self.to_dict()[key]

    def __str__(self):
        """String representation."""
        return str(self.to_dict())

    def __repr__(self):
        """Representation."""
        return repr(self.to_dict())

    def __deepcopy__(self, memo):
        cls = self.__class__
        newone = cls.__new__(cls)
        newone.a_pydantic_object = copy.deepcopy(self.a_pydantic_object, memo=memo)
        newone.a_list = copy.deepcopy(self.a_list, memo=memo)
        newone.a_dict = copy.deepcopy(self.a_dict, memo=memo)
        # Notice that newone.an_object is not created again and is shared between the original and the new object.
        newone.an_object = self.an_object
        return newone


class GradioApp:
    def __init__(self):
        # This is a safe global variable because it remains the same for all users and is never modified.
        self.app_name = "gradio-experiments"

        self.global_state = StateData()

    def component_text_transformation(self) -> gr.Group:
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
        with gr.Group() as component:
            session_state = gr.State(
                StateData(an_object=self.global_state.an_object),
            )
            browser_state = gr.BrowserState(
                # default_value=json.dumps(self.global_state, indent=2, default=vars),
                storage_key="gradio-experiments-user-state",
            )
            with gr.Row(equal_height=True):
                json_global_state = gr.JSON(
                    value=self.global_state.__dict__, label="Global state"
                )
                json_session_state = gr.JSON(
                    value=session_state.value.__dict__, label="Session state"
                )
                json_browser_state = gr.JSON(
                    value=None,
                    label="Browser state",
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
            inputs=[],
            outputs=[json_global_state, label_task_output],
            api_name="change_global_state",
        )
        def change_global_state():
            self.global_state.a_list.append(
                SomePydanticModel(
                    a=random.randint(0, 99),
                    b="changed-global",
                    c=[i for i in range(random.randint(0, 9))],
                )
            )
            random_key = f"key-{random.randint(0, 9999)}"
            self.global_state.a_dict[random_key] = SomePydanticModel(
                a=random.randint(0, 999),
                b="changed-global",
                c=[i for i in range(random.randint(0, 9))],
            )
            self.global_state.a_pydantic_object = SomePydanticModel(
                a=random.randint(0, 499),
                b="changed-global",
                c=[i for i in range(random.randint(0, 9))],
            )
            self.global_state.an_object.do_task()
            return self.global_state.__dict__, {
                f"global: {self.global_state.an_object.task_output}": 1.0,
                f"session: {session_state.value.an_object.task_output}": 1.0,
                f"browser: {browser_state.value.an_object.task_output if browser_state.value else 'uninitialised'}": 1.0,
            }

        @btn_change_session_state.click(
            inputs=[],
            outputs=[json_session_state, label_task_output],
            api_name="change_session_state",
        )
        def change_session_state():
            session_state.value.a_list.append(
                SomePydanticModel(
                    a=random.randint(0, 99),
                    b="changed-session",
                    c=[i for i in range(random.randint(0, 9))],
                )
            )
            random_key = f"key-{random.randint(0, 9999)}"
            session_state.value.a_dict[random_key] = SomePydanticModel(
                a=random.randint(0, 999),
                b="changed-session",
                c=[i for i in range(random.randint(0, 9))],
            )
            session_state.value.a_pydantic_object = SomePydanticModel(
                a=random.randint(0, 499),
                b="changed-session",
                c=[i for i in range(random.randint(0, 9))],
            )
            session_state.value.an_object.do_task()
            return session_state.value.__dict__, {
                f"global: {self.global_state.an_object.task_output}": 1.0,
                f"session: {session_state.value.an_object.task_output}": 1.0,
                f"browser: {browser_state.value.an_object.task_output if browser_state.value else 'uninitialised'}": 1.0,
            }

        @btn_change_browser_state.click(
            inputs=[],
            outputs=[json_browser_state, label_task_output],
            api_name="change_browser_state",
        )
        def change_browser_state():
            if browser_state.value is None:
                browser_state.value = StateData(an_object=self.global_state.an_object)
            browser_state.value.a_list.append(
                SomePydanticModel(
                    a=random.randint(0, 99),
                    b="changed-browser",
                    c=[i for i in range(random.randint(0, 5))],
                )
            )
            random_key = f"key-{random.randint(0, 9999)}"
            browser_state.value.a_dict[random_key] = SomePydanticModel(
                a=random.randint(0, 999),
                b="changed-browser",
                c=[i for i in range(random.randint(0, 5))],
            )
            browser_state.value.a_pydantic_object = SomePydanticModel(
                a=random.randint(0, 499),
                b="changed-browser",
                c=[i for i in range(random.randint(0, 5))],
            )
            browser_state.value.an_object.do_task()
            return browser_state.value.__dict__, {
                f"global: {self.global_state.an_object.task_output}": 1.0,
                f"session: {session_state.value.an_object.task_output}": 1.0,
                f"browser: {browser_state.value.an_object.task_output if browser_state.value else 'uninitialised'}": 1.0,
            }

        @btn_refresh_states.click(
            outputs=[
                json_global_state,
                json_session_state,
                json_browser_state,
                label_task_output,
            ],
            api_name="refresh_states",
        )
        def refresh_states():
            ic(session_state.value.__dict__)
            return (
                self.global_state.__dict__,
                session_state.value.__dict__,
                (browser_state.value.__dict__ if browser_state.value else None),
                {
                    f"global: {self.global_state.an_object.task_output}": 1.0,
                    f"session: {session_state.value.an_object.task_output}": 1.0,
                    f"browser: {browser_state.value.an_object.task_output if browser_state.value else 'uninitialised'}": 1.0,
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
                 - GitHub repository: _[gradio-experiments](https://github.com/anirbanbasu/gradio-experiments)_
                """
            )
            with gr.Tab(label="State management"):
                with gr.Accordion(label="Explanation", open=True):
                    gr.Markdown(
                        """
                        This component demonstrates the management of global state, session state (using `gr.State`) and browser state (using `gr.BrowserState`).

                        ## Expected behaviour

                        - **Global state**: The global state is shared across all web sessions. Modifications to the global state are reflected in all sessions.
                        - **Session state**: The session state is specific to the user's browser session. The session state is not shared across different browser sessions and lost when the browser window is closed or the page is refreshed.
                        - **Browser state**: The browser state is stored in the browser's local storage. It is not shared across different browsers but shared across multiple windows of the same browser. The browser state persists even when the browser window is closed or the page is refreshed.

                        ## Try it out
                        1. Open this page in two different browsers, not just browser tabs.
                        2. Change the global state in one browser (by clicking the 'Change global state' button) and see the changes reflected in the other browser (by clicking the 'Refresh states' button).
                        3. Change the session state in one browser (by clicking the 'Change session state' button) and see that the changes are **not** reflected in the other browser (by clicking the 'Refresh states' button).
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
    app.construct_ui().queue().launch(
        server_name="0.0.0.0", show_error=True, show_api=True, debug=True, share=False
    )
