
from pydantic import BaseModel
from typing import List, Optional
from typing_extensions import Literal

class ChatCompletionAudio(BaseModel):
    id: str
    """Unique identifier for this audio response."""

    data: str
    """
    Base64 encoded audio bytes generated by the model, in the format specified in
    the request.
    """

    expires_at: int
    """
    The Unix timestamp (in seconds) for when this audio response will no longer be
    accessible on the server for use in multi-turn conversations.
    """

    transcript: str
    """Transcript of the audio generated by the model."""


class Function(BaseModel):
    arguments: str
    """
    The arguments to call the function with, as generated by the model in JSON
    format. Note that the model does not always generate valid JSON, and may
    hallucinate parameters not defined by your function schema. Validate the
    arguments in your code before calling your function.
    """

    name: str
    """The name of the function to call."""


class ChatCompletionMessageToolCall(BaseModel):
    id: str
    """The ID of the tool call."""

    function: Function
    """The function that the model called."""

    type: Literal["function"]


class FunctionCall(BaseModel):
    arguments: str
    """
    The arguments to call the function with, as generated by the model in JSON
    format. Note that the model does not always generate valid JSON, and may
    hallucinate parameters not defined by your function schema. Validate the
    arguments in your code before calling your function.
    """

    name: str
    """The name of the function to call."""


class ChatCompletionMessage(BaseModel):
    content: Optional[str] = None
    """The contents of the message."""

    refusal: Optional[str] = None
    """The refusal message generated by the model."""

    role: Literal["assistant"]
    """The role of the author of this message."""

    audio: Optional[ChatCompletionAudio] = None
    """
    If the audio output modality is requested, this object contains data about the
    audio response from the model.
    [Learn more](https://platform.openai.com/docs/guides/audio).
    """

    function_call: Optional[FunctionCall] = None
    """Deprecated and replaced by `tool_calls`.

    The name and arguments of a function that should be called, as generated by the
    model.
    """

    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None
    """The tool calls generated by the model, such as function calls."""