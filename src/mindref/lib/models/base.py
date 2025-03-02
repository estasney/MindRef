from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
    )
