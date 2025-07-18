import base64
import io
import os
import subprocess
import sys
import platform
import PIL
import PIL.Image
import gradio as gr

# See why we are doing this with the local package: https://discuss.huggingface.co/t/custom-python-packages-at-spaces/17250/6
# try:
from dotenv import load_dotenv

# except ImportError:
#     os.system("pip install -e .")
#     from dotenv import load_dotenv

from utils import (
    AppConstants,
    EnvironmentVariables,
    parse_env,
    ic,
)
from data import (
    ProfileImage,
    StateData,
    EntityProfile,
    PydanticEncapsulator,
)

import polars as pl


class GradioApp:
    """The main Gradio application class."""

    BROWSER_STATE_UNINITIALISED_MSG = (
        "uninitialised, click 'Change browser state' to initialise"
    )

    def __init__(self):
        # This is a safe global variable because it remains the same for all users and is never modified.
        self.app_name = "gradio-experiments"
        self.state_key = f"{self.app_name}-local-state"
        self.profile_key = f"{self.app_name}-entity-profile"

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
                api_name="text_transform_to_uppercase",
            )
            def text_to_uppercase(text: str) -> str:
                return text.upper()

        return component

    def component_state_management(self) -> gr.Group:
        """This is a component to demonstrate state management."""

        def state_task_dictionary(
            session_state_value: StateData,
            browser_state_value: StateData,
        ) -> dict:
            return {
                "global": self.global_state.an_object.task_output,
                "session": session_state_value.an_object.task_output,
                "browser": (
                    browser_state_value.an_object.task_output
                    if browser_state_value
                    else GradioApp.BROWSER_STATE_UNINITIALISED_MSG
                ),
            }

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
            json_task_output = gr.JSON(
                value=None,
                label="Task output",
                max_height=200,
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
            inputs=[session_state, browser_state],
            outputs=[json_global_state, json_task_output],
            api_name="state_management_change_global_state",
        )
        def change_global_state(
            session_state_value: StateData, browser_state_value: str
        ):
            self.global_state.make_random_changes("global")
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            return (
                self.global_state.__dict__,
                state_task_dictionary(
                    session_state_value,
                    browser_state_obj if browser_state_value else None,
                ),
            )

        @btn_change_session_state.click(
            inputs=[session_state],
            outputs=[session_state],
            api_name="state_management_change_session_state",
        )
        def change_session_state(session_state_value: StateData):
            session_state_value.make_random_changes("session")
            return gr.update(value=session_state_value)

        @session_state.change(
            inputs=[session_state, browser_state],
            outputs=[json_session_state, json_task_output],
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
                state_task_dictionary(
                    session_state_value,
                    browser_state_obj if browser_state_value else None,
                ),
            )

        @btn_change_browser_state.click(
            inputs=[session_state, browser_state],
            outputs=[browser_state, json_browser_state, json_task_output],
            api_name="state_management_change_browser_state",
        )
        def change_browser_state(
            session_state_value: StateData, browser_state_value: str
        ):
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            browser_state_obj.make_random_changes("browser")
            return (
                gr.update(value=browser_state_obj),
                browser_state_obj.__dict__,
                state_task_dictionary(
                    session_state_value,
                    browser_state_obj,
                ),
            )

        @btn_refresh_states.click(
            inputs=[session_state, browser_state],
            outputs=[
                json_global_state,
                json_session_state,
                json_browser_state,
                json_task_output,
            ],
            api_name="state_management_refresh",
        )
        def refresh_states(session_state_value: StateData, browser_state_value: str):
            browser_state_obj = StateData(an_object=self.global_state.an_object)
            if browser_state_value is not None:
                browser_state_obj.reset_from_json_str(browser_state_value)
            return (
                self.global_state.__dict__,
                session_state_value.__dict__,
                (browser_state_obj.__dict__ if browser_state_value else None),
                state_task_dictionary(
                    session_state_value,
                    browser_state_obj if browser_state_value else None,
                ),
            )

        return component

    def component_datasets(self) -> gr.Group:
        """This is a component to experiment with datasets."""
        with gr.Group() as component:
            session_pl_dataframe = gr.State(None)
            session_pl_dataframe_display = gr.State(None)
            file_dataset = gr.File(
                label="Dataset file",
                visible=True,
                interactive=True,
                file_count="single",
                file_types=AppConstants.ALLOWED_DATASET_FILE_EXTENSIONS,
            )
            dataframe_data_preview = gr.Dataframe(
                value=None,
                type="polars",
                label="Dataframe preview",
                max_height=300,
                interactive=False,
                visible=False,
            )

            json_selected_row = gr.JSON(
                label="Last selected row", value=None, max_height=300, visible=False
            )

        @file_dataset.upload(
            inputs=[file_dataset],
            outputs=[session_pl_dataframe],
            api_name="dataset_upload",
        )
        def upload_dataset_file(file):
            if file is None:
                return None
            _, extension = os.path.splitext(file.name)
            if extension.lower() == AppConstants.FILE_EXTENSION_CSV:
                result = pl.read_csv(
                    source=file.name,
                    ignore_errors=True,
                    use_pyarrow=True,
                    batch_size=16384,
                )
            elif extension.lower() == AppConstants.FILE_EXTENSION_JSON:
                result = pl.read_json(source=file.name)
            elif extension.lower() == AppConstants.FILE_EXTENSION_PARQUET:
                result = pl.read_parquet(source=file.name)
            else:
                raise gr.Error(
                    f"Unsupported dataset file extension: '{extension}'. Supported extensions: {AppConstants.ALLOWED_DATASET_FILE_EXTENSIONS}."
                )
            gr.Info(
                message=f"Loaded data frame: {result.shape[0]} rows and {result.shape[1]} columns.",
                duration=5,
            )
            return result

        @file_dataset.clear(
            outputs=[session_pl_dataframe],
            api_name="dataset_clear",
        )
        def clear_dataset_file():
            return None

        @session_pl_dataframe.change(
            inputs=[session_pl_dataframe],
            outputs=[session_pl_dataframe_display],
            api_name=False,
        )
        def session_pl_dataframe_changed(data: pl.DataFrame):
            return data

        @session_pl_dataframe_display.change(
            inputs=[session_pl_dataframe_display],
            outputs=[dataframe_data_preview, json_selected_row],
            api_name=False,
        )
        def session_pl_dataframe_display_changed(data: pl.DataFrame):
            if data is None or data.shape[0] == 0:
                return (
                    gr.update(value=None, visible=False),
                    gr.update(value=None, visible=False),
                )

            return (
                gr.update(
                    label=f"Rows {data.shape[0]}, columns {data.shape[1]}.",
                    value=data,
                    visible=True,
                ),
                gr.update(value=None, visible=False),
            )

        @dataframe_data_preview.select(
            inputs=[dataframe_data_preview],
            outputs=[json_selected_row],
            api_name=False,
        )
        def dataframe_data_preview_selected(
            data: pl.DataFrame, selected_event: gr.SelectData
        ):
            if selected_event is None or not selected_event.selected:
                return gr.update(value=None, visible=False)
            # FIXME: This selection will throw an error such as the following error if null values exist.
            # polars.exceptions.ComputeError: could not append value: "" of type: str to the builder; make sure that all rows have the same schema or consider increasing `infer_schema_length`
            # it might also be that a value overflows the data-type's capacity
            return gr.update(
                value=data.row(index=selected_event.index[0], named=True),
                visible=True,
            )

        return component

    def component_pydantic_profiles(
        self,
        profile_object_in_session: gr.State,
    ) -> gr.Group:
        with gr.Group() as component:
            with gr.Tab(label="View (decorative)") as tab_view_decorative:
                with gr.Row(equal_height=True):
                    with gr.Column():
                        image_profile = gr.Image(
                            label="Representative image",
                            type="pil",
                            height=256,
                            width=256,
                            show_label=False,
                            show_download_button=False,
                            show_fullscreen_button=False,
                            show_share_button=False,
                            container=False,
                            visible=False,
                        )
                        md_image_info = gr.Markdown()
                    md_profile = gr.Markdown()
            with gr.Tab(label="View (JSON)") as tab_json_view:
                json_view = gr.JSON()

            with gr.Tab(label="Edit") as tab_edit:
                with gr.Row(equal_height=True):
                    text_profile_name_namespace = gr.Textbox(
                        label="Namespace",
                        info="Enter the namespace of the profile.",
                        value=(
                            profile_object_in_session.value.name.namespace
                            if profile_object_in_session.value
                            else AppConstants.EMPTY_STRING
                        ),
                    )
                    text_profile_name_other_names = gr.TextArea(
                        label="Other names",
                        info="Enter the other names of the profile, one per line.",
                        max_lines=10,
                        interactive=True,
                    )
                with gr.Row(equal_height=True):
                    image_profile_preview = gr.Image(
                        label="Preview",
                        type="pil",
                        height=256,
                        width=256,
                        show_label=False,
                        show_download_button=False,
                        show_fullscreen_button=False,
                        show_share_button=False,
                        visible=False,
                    )
                    file_image_profile = gr.File(
                        type="binary",
                        file_types=[
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".gif",
                        ],
                        label="Profile image (upload to replace existing, if any): minimum 256x256 pixels",
                    )
                    with gr.Column():
                        text_image_caption = gr.Textbox(
                            label="Image caption",
                            info="Enter the caption of the image (optional).",
                            interactive=True,
                        )
                        text_image_credits = gr.Textbox(
                            label="Image credits",
                            info="Enter the credits for the image (optional).",
                            interactive=True,
                        )
                btn_update_profile = gr.Button("Update profile", variant="primary")

            @tab_edit.select(
                inputs=[
                    profile_object_in_session,
                ],
                outputs=[
                    text_profile_name_namespace,
                    text_profile_name_other_names,
                    file_image_profile,
                    image_profile_preview,
                    text_image_caption,
                    text_image_credits,
                ],
                api_name=False,
            )
            def tab_edit_selected(profile: EntityProfile) -> EntityProfile:
                if profile:
                    image_bytes = (
                        base64.b64decode(
                            profile.representative_image.data.encode("ascii")
                        )
                        if profile.representative_image
                        else None
                    )
                    return [
                        profile.name.namespace,
                        (
                            gr.update(
                                value=AppConstants.CRLF.join(profile.name.other_names),
                                lines=len(profile.name.other_names),
                            )
                            if profile.name.other_names
                            else AppConstants.EMPTY_STRING
                        ),
                        None,
                        gr.update(
                            visible=True if profile.representative_image else False,
                            value=(
                                PIL.Image.open(io.BytesIO(image_bytes))
                                if image_bytes
                                else None
                            ),
                        ),
                        (
                            profile.representative_image.caption
                            if profile.representative_image
                            else AppConstants.EMPTY_STRING
                        ),
                        (
                            profile.representative_image.credits
                            if profile.representative_image
                            else AppConstants.EMPTY_STRING
                        ),
                    ]
                else:
                    return [
                        AppConstants.EMPTY_STRING,
                        AppConstants.EMPTY_STRING,
                        None,
                        gr.update(
                            visible=False,
                            value=None,
                        ),
                        AppConstants.EMPTY_STRING,
                        AppConstants.EMPTY_STRING,
                    ]

            @tab_json_view.select(
                inputs=[profile_object_in_session],
                outputs=[json_view],
                api_name=False,
            )
            def tab_json_view_selected(profile: EntityProfile) -> EntityProfile:
                return profile.model_dump() if profile else None

            @tab_view_decorative.select(
                inputs=[profile_object_in_session],
                outputs=[image_profile, md_image_info, md_profile],
            )
            def tab_view_decorative_selected(profile: EntityProfile):
                if profile:
                    if profile.representative_image:
                        image_bytes = base64.b64decode(
                            profile.representative_image.data.encode("ascii")
                        )
                        return [
                            gr.update(
                                value=PIL.Image.open(io.BytesIO(image_bytes)),
                                visible=True,
                            ),
                            (
                                f"""**{profile.representative_image.caption}**

                                _Credits: {profile.representative_image.credits}_"""
                                if profile.representative_image.caption
                                or profile.representative_image.credits
                                else None
                            ),
                            f"""## {profile.name.namespace}

                            {" ".join(profile.name.other_names)}""",
                        ]
                    else:
                        return [
                            gr.update(value=None, visible=False),
                            None,
                            f"""## {profile.name.namespace}

                            {" ".join(profile.name.other_names)}""",
                        ]
                return [gr.update(value=None, visible=False), None, None]

            @btn_update_profile.click(
                inputs=[
                    text_profile_name_namespace,
                    text_profile_name_other_names,
                    file_image_profile,
                    text_image_caption,
                    text_image_credits,
                    profile_object_in_session,
                ],
                outputs=[profile_object_in_session],
                api_name=False,
            )
            def btn_update_profile_clicked(
                namespace: str,
                other_names: str,
                image_data: bytes,
                caption: str,
                credits: str,
                profile_object_in_session_value: EntityProfile,
            ):
                if profile_object_in_session_value:
                    profile_object_in_session_value.name.namespace = namespace
                    profile_object_in_session_value.name.other_names = (
                        other_names.split()
                    )
                    if image_data:
                        profile_object_in_session_value.representative_image = (
                            ProfileImage(
                                data=base64.b64encode(image_data).decode("ascii"),
                                caption=caption,
                                credits=credits,
                            )
                        )
                    else:
                        if (
                            profile_object_in_session_value.representative_image is None
                            and (
                                caption is not AppConstants.EMPTY_STRING
                                or credits is not AppConstants.EMPTY_STRING
                            )
                        ):
                            gr.Warning(
                                "A representative image is required if you want to add its caption or credits."
                            )
                        elif (
                            profile_object_in_session_value.representative_image
                            is not None
                        ):
                            profile_object_in_session_value.representative_image.caption = caption
                            profile_object_in_session_value.representative_image.credits = credits
                return profile_object_in_session_value

            @file_image_profile.upload(
                inputs=[file_image_profile],
                outputs=[image_profile_preview],
                api_name=False,
            )
            def image_profile_uploaded(image_data: bytes):
                return gr.update(
                    visible=True if image_data else False,
                    value=(
                        PIL.Image.open(io.BytesIO(image_data)) if image_data else None
                    ),
                )

        return component

    def component_json_formatting(self) -> gr.Group:
        with gr.Group() as component:
            encapsulated_pydantic_state_obj = gr.State(None)
            json_input = gr.JSON()
            btn_load_encapsulated_object = gr.Button(
                value="Load encapsulated Pydantic object for this session",
                variant="primary",
            )

            @btn_load_encapsulated_object.click(
                inputs=[encapsulated_pydantic_state_obj],
                outputs=[encapsulated_pydantic_state_obj],
                api_name=False,
            )
            def load_encapsulated_object(
                encapsulated_pydantic_obj: PydanticEncapsulator,
            ):
                """Load the encapsulated Pydantic object."""
                if encapsulated_pydantic_obj is None:
                    encapsulated_pydantic_obj = PydanticEncapsulator()
                return encapsulated_pydantic_obj

            @encapsulated_pydantic_state_obj.change(
                inputs=[encapsulated_pydantic_state_obj],
                outputs=[json_input],
                api_name=False,
            )
            def encapsulated_pydantic_state_obj_changed(
                encapsulated_pydantic_obj: PydanticEncapsulator,
            ):
                """Update the JSON input with the encapsulated Pydantic object."""
                return encapsulated_pydantic_obj

        return component

    def construct_ui(self) -> gr.Blocks:
        with gr.Blocks(
            title=self.app_name,
            fill_height=True,
            fill_width=True,
            analytics_enabled=False,
            theme=gr.themes.Ocean(
                radius_size="md",
                font=gr.themes.GoogleFont("Lato", weights=(100, 300)),
                font_mono=gr.themes.GoogleFont("IBM Plex Mono", weights=(100, 300)),
            ),
        ) as ui:
            gr.Markdown(
                f"""
                # gradio-experiments

                A collection of feature experiments with Gradio.

                 - Gradio version: _{gr.get_package_version()}_
                 - Python version: _{sys.version}_
                 - Platform: _{platform.uname()._asdict()}_
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

            with gr.Tab(label="Dataset"):
                with gr.Accordion(label="Explanation", open=True):
                    gr.Markdown(
                        """
                        This component experiments with datasets. _More explanation will be added._
                        """
                    )
                self.component_datasets()

            with gr.Tab(label="Pydantic entity profiles") as tab_pydantic_profiles:
                profile_object_in_session = gr.State()
                profile_object_in_browser_storage = gr.BrowserState(
                    storage_key=self.profile_key,
                    secret=parse_env(EnvironmentVariables.LOCAL_STORAGE_ENCRYPTION_KEY),
                )
                with gr.Accordion(label="Explanation", open=True):
                    gr.Markdown(
                        """
                        This component experiments with profile information backed by Pydantic models. _More explanation will be added._
                        """
                    )
                self.component_pydantic_profiles(profile_object_in_session)

            @tab_pydantic_profiles.select(
                inputs=[
                    profile_object_in_session,
                    profile_object_in_browser_storage,
                ],
                outputs=[
                    profile_object_in_session,
                    profile_object_in_browser_storage,
                ],
                api_name=False,
            )
            def tab_pydantic_profiles_selected(
                profile: EntityProfile, profile_object_in_browser_storage_value
            ) -> EntityProfile:
                if profile_object_in_browser_storage_value is not None:
                    profile = EntityProfile.model_validate(
                        profile_object_in_browser_storage_value
                    )
                    gr.Info(
                        message=f"Profile '{profile.name.namespace.upper()}, {' '.join(profile.name.other_names)}' loaded from browser storage.",
                    )
                else:
                    profile = EntityProfile.create_random_profile()
                    gr.Info(
                        message=f"Using randomly generated profile '{profile.name.namespace.upper()}, {' '.join(profile.name.other_names)}' since none found in browser storage.",
                    )
                return (
                    profile,
                    gr.update(value=profile) if profile else None,
                )

            @profile_object_in_session.change(
                inputs=[profile_object_in_session],
                outputs=[
                    profile_object_in_browser_storage,
                ],
                api_name=False,
            )
            def profile_object_in_session_changed(profile: EntityProfile):
                return gr.update(value=profile)

            with gr.Tab(label="JSON formatting"):
                with gr.Accordion(label="Explanation", open=True):
                    gr.Markdown(
                        """
                        This component experiments with JSON formatting. As of version 5.38.0, Gradio's JSON component is unable to correctly display a pretty-printed JSON string.
                        """
                    )
                self.component_json_formatting()

            with gr.Tab(label="Text transformations"):
                self.component_text_transformation()

        return ui


def main():
    ic(load_dotenv())
    app = GradioApp()
    print(subprocess.check_output(["gradio", "environment"]).decode())
    app.construct_ui().queue().launch(
        server_name="0.0.0.0", share=False, ssr_mode=False
    )


if __name__ == "__main__":
    main()
