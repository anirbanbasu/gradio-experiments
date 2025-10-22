try:
    from gradio_experiments.data import StateData  # noqa: F401
except ImportError:
    from data import StateData  # noqa: F401


class TestDataModels:
    """Tests for data models."""

    # TODO: Very basic test, improve.
    def test_state_data_model(self):
        state_data = StateData()
        assert state_data.a_pydantic_object.a == 1
        assert state_data.a_pydantic_object.b == "default"
        assert state_data.a_pydantic_object.c == [1, 2, 3, 4]
