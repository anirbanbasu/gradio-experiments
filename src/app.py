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

    def __init__(self, create_uninitialised: bool = False):
        """
        Create a new instance of the StateData class.

        Args:
            create_uninitialised (bool): Whether to create the object with uninitialised values. Defaults to False.
        """
        if not create_uninitialised:
            self.a_pydantic_object = SomePydanticModel(a=1, b="default", c=[1, 2, 3, 4])
            self.an_object = SomeTask()
        else:
            self.a_pydantic_object = None
            self.an_object = None
        self.a_list: List[SomePydanticModel] = []
        self.a_dict: Dict[str, SomePydanticModel] = {}
        # And so on

    def __deepcopy__(self, memo):
        newone = type(self)(create_uninitialised=True)
        newone.__dict__.update(self.__dict__)
        newone.a_list = []
        newone.a_dict = {}
        # Notice that self.an_object is not created again and is shared between the original and the new object.
        # ic(self.__dict__, newone.__dict__)
        return newone


class GradioApp:
    def __init__(self):
        # This is a safe global variable because it remains the same for all users and is never modified.
        self.app_name = "gradio-experiments"

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
            global_state = gr.State(
                StateData(),
            )
            user_state = gr.BrowserState(
                storage_key="gradio-experiments-user-state",
            )
            with gr.Row(equal_height=True):
                json_global_state = gr.JSON(
                    value=global_state.value.__dict__, label="Global state"
                )
                json_user_state = gr.JSON(
                    value=(user_state.value.__dict__ if user_state.value else None),
                    label="User local state",
                )
                with gr.Column():
                    btn_change_global_state = gr.Button(
                        value="Change global state",
                        variant="primary",
                    )
                    btn_change_user_state = gr.Button(
                        value="Change user state",
                        variant="secondary",
                    )
                    btn_refresh_states = gr.Button(
                        value="Refresh states",
                        variant="huggingface",
                    )
            label_task_output = gr.Label(
                label="Task output",
                value={
                    f"global: {global_state.value.an_object.task_output}": 1.0,
                    f"user: {user_state.value.an_object.task_output if user_state.value else "uninitialised"}": 1.0,
                },
            )

        @btn_change_global_state.click(
            inputs=[],
            outputs=[json_global_state, label_task_output],
            api_name="change_global_state",
        )
        def change_global_state():
            global_state.value.a_list.append(
                SomePydanticModel(
                    a=random.randint(0, 99),
                    b="changed-global",
                    c=[i for i in range(random.randint(0, 9))],
                )
            )
            random_key = f"key-{random.randint(0, 9999)}"
            global_state.value.a_dict[random_key] = SomePydanticModel(
                a=random.randint(0, 999),
                b="changed-global",
                c=[i for i in range(random.randint(0, 9))],
            )
            global_state.value.a_pydantic_object = SomePydanticModel(
                a=random.randint(0, 499),
                b="changed-global",
                c=[i for i in range(random.randint(0, 9))],
            )
            global_state.value.an_object.do_task()
            ic(global_state)
            return global_state.value.__dict__, {
                f"global: {global_state.value.an_object.task_output}": 1.0,
                f"user: {user_state.value.an_object.task_output if user_state.value else "uninitialised"}": 1.0,
            }

        @btn_change_user_state.click(
            inputs=[],
            outputs=[json_user_state, label_task_output],
            api_name="change_user_state",
        )
        def change_user_state():
            if user_state.value is None:
                user_state.value = copy.deepcopy(global_state.value)
            user_state.value.a_list.append(
                SomePydanticModel(
                    a=random.randint(0, 99),
                    b="changed-user",
                    c=[i for i in range(random.randint(0, 5))],
                )
            )
            random_key = f"key-{random.randint(0, 9999)}"
            user_state.value.a_dict[random_key] = SomePydanticModel(
                a=random.randint(0, 999),
                b="changed-user",
                c=[i for i in range(random.randint(0, 5))],
            )
            user_state.value.a_pydantic_object = SomePydanticModel(
                a=random.randint(0, 499),
                b="changed-user",
                c=[i for i in range(random.randint(0, 5))],
            )
            user_state.value.an_object.do_task()
            ic(user_state)
            return user_state.value.__dict__, {
                f"global: {global_state.value.an_object.task_output}": 1.0,
                f"user: {user_state.value.an_object.task_output if user_state.value else "uninitialised"}": 1.0,
            }

        @btn_refresh_states.click(
            outputs=[json_global_state, json_user_state, label_task_output],
            api_name="refresh_states",
        )
        def refresh_states():
            ic(global_state.value.__dict__)
            return (
                global_state.value.__dict__,
                (user_state.value.__dict__ if user_state.value else None),
                {
                    f"global: {global_state.value.an_object.task_output}": 1.0,
                    f"user: {user_state.value.an_object.task_output if user_state.value else "uninitialised"}": 1.0,
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
                """
                # gradio-experiments

                A collection of feature experiments with Gradio.
                """
            )
            with gr.Tab(label="State management"):
                gr.Markdown(
                    """
                    This component demonstrates the management of global state (using `gr.State`) and user state (using `gr.BrowserState`).

                    ## Expected behaviour

                    The global state is shared across all web sessions. Modifications to the global state are reflected in all sessions. On the other hand,
                    the user state is specific to the user's browser session. The user state is not shared across different browser sessions.

                    ## Instructions
                    1. Open this page in two different browsers, not just browser tabs.
                    2. Change the global state in one browser (by clicking the 'Change global state' button) and see the changes reflected in the other browser (by clicking the 'Refresh states' button).
                    3. Change the user state in one browser (by clicking the 'Change user state' button) and see that the changes are **not** reflected in the other browser (by clicking the 'Refresh states' button).

                    Notice that the 'Task output' is is the result of a task performed by an object, which is maintained as a reference in the global and user states. Thus, the task output is shared across all sessions even if it is triggered by a user state change.
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
