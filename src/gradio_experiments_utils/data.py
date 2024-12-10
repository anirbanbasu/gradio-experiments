import copy
import datetime
import json
import random
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SomePydanticModel(BaseModel):
    """An example Pydantic model."""

    a: int = Field(..., description="An integer field.")
    b: str = Field(..., description="A string field.")
    c: Optional[List[int]] = Field(default=[], description="A list of integers.")


class SomeTask:
    """An example class that performs a task."""

    def __init__(self):
        """Create a new instance of the SomeTask class without performing the task."""
        self.task_output = "task-not-executed-in-this-session"

    def do_task(self):
        """Perform the task."""
        self.task_output = f"task-done at {datetime.datetime.now()}"


class StateData:
    """A class to hold the state data for the application."""

    def __init__(self, create_uninitialised: bool = False, an_object: SomeTask = None):
        """
        Create a new instance of the StateData class.

        Args:
            create_uninitialised (bool): Whether to create the object with uninitialised values. Defaults to False.
            an_object (SomeTask): An instance of the SomeTask class. Defaults to None. Specifying this has no effect if create_uninitialised is True.
        """

        if create_uninitialised:
            self.a_list: List[SomePydanticModel] = None
            self.a_dict: Dict[str, SomePydanticModel] = None
            self.a_pydantic_object = None
            self.an_object = None
        else:
            self.a_pydantic_object = SomePydanticModel(a=1, b="default", c=[1, 2, 3, 4])
            self.an_object = SomeTask() if an_object is None else an_object
            self.a_list: List[SomePydanticModel] = []
            self.a_dict: Dict[str, SomePydanticModel] = {}

    def __hash__(self) -> int:
        """
        A hash function to ensure that changes to the object data result in different hash values.

        Returns:
            int: The hash value of the object.
        """
        # This is absolutely necessary for gr.State to work, see: https://www.gradio.app/guides/state-in-blocks
        return hash(str(self))

    def __str__(self):
        """
        Nicely formatted JSON string of the dictionary representation of this class.

        Returns:
            str: A JSON string representation of the object.
        """
        # This is necessary to make an object of the class JSON serializable for gr.BrowserState, see: https://www.gradio.app/guides/state-in-blocks
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)

    def make_random_changes(self, caller: str = "unknown"):
        """
        Make random changes to the object data.

        Args:
            caller (str): The name of the caller. Defaults to "unknown".
        """
        now = datetime.datetime.now()
        self.a_list.append(
            SomePydanticModel(
                a=random.randint(0, 99),
                b=f"changed-{caller}@{now}",
                c=[i for i in range(random.randint(0, 9))],
            )
        )
        random_key = f"key-{random.randint(0, 9999)}"
        self.a_dict[random_key] = SomePydanticModel(
            a=random.randint(0, 999),
            b=f"changed-{caller}@{now}",
            c=[i for i in range(random.randint(0, 9))],
        )
        self.a_pydantic_object = SomePydanticModel(
            a=random.randint(0, 499),
            b=f"changed-{caller}@{now}",
            c=[i for i in range(random.randint(0, 9))],
        )
        self.an_object.do_task()

    def reset_from_json(self, json_data: dict):
        """
        Reset the object from a JSON dictionary. Ignores keys that are not present in the object.
        Also, ignores the 'an_object' key because the JSON serialized version contains a memory reference
        to a memory location that may no longer be available on the server. Besides, we want the `an_object`
        to point to the global reference only.

        Args:
            json_data (dict): The JSON dictionary to reset the object from.
        """
        if "a_pydantic_object" in json_data:
            self.a_pydantic_object = (
                SomePydanticModel(**json_data["a_pydantic_object"])
                if json_data["a_pydantic_object"]
                else None
            )
        if "a_list" in json_data:
            self.a_list = (
                [SomePydanticModel(**item) for item in json_data["a_list"]]
                if json_data["a_list"]
                else []
            )
        if "a_dict" in json_data:
            self.a_dict = (
                {k: SomePydanticModel(**v) for k, v in json_data["a_dict"].items()}
                if json_data["a_dict"]
                else {}
            )

    def reset_from_json_str(self, json_str: str):
        """
        Reset the object from a JSON string by calling `reset_from_json`.

        Args:
            json_str (str): The JSON string to reset the object from.
        """
        self.reset_from_json(json.loads(json_str))

    def to_dict(self):
        """
        Converts the object into a dictionary representation.

        Returns:
            dict: A dictionary representation of the object.
        """
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

    def __deepcopy__(self, memo):
        """
        A deep copy implementation for the class.

        Args:
            memo: A dictionary to keep track of the objects that have already been copied.

        Returns:
            StateData: A deep copy of the object.
        """
        cls = self.__class__
        newone = cls.__new__(cls)
        newone.a_pydantic_object = copy.deepcopy(self.a_pydantic_object, memo=memo)
        newone.a_list = copy.deepcopy(self.a_list, memo=memo)
        newone.a_dict = copy.deepcopy(self.a_dict, memo=memo)
        # Notice that newone.an_object is not created again and is shared between the original and the new object.
        newone.an_object = self.an_object
        return newone
