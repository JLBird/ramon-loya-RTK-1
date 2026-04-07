"""
LangChainAnthropicTarget — bridges LangChain ChatAnthropic into PyRIT's PromptChatTarget interface.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pyrit.models.message import Message, MessagePiece
from pyrit.prompt_target.common.prompt_chat_target import PromptChatTarget
from pyrit.prompt_target.common.target_capabilities import TargetCapabilities


class LangChainAnthropicTarget(PromptChatTarget):
    """
    A PyRIT PromptChatTarget that uses LangChain's ChatAnthropic under the hood.
    Bypasses OpenAI-compatible endpoint JSON response_format incompatibility.
    """

    _DEFAULT_CAPABILITIES = TargetCapabilities(
        supports_multi_turn=True,
        supports_multi_message_pieces=True,
        supports_json_output=True,
    )

    def __init__(self, llm: ChatAnthropic) -> None:
        super().__init__(
            endpoint="https://api.anthropic.com",
            model_name=llm.model,
        )
        self._llm = llm

    async def send_prompt_async(self, *, message: Message) -> list[Message]:
        conversation_id = message.conversation_id

        # Pull full conversation history from PyRIT memory
        history = self._memory.get_conversation(conversation_id=conversation_id)

        # Convert PyRIT memory history to LangChain message format
        lc_messages = []
        for mem_msg in history:
            for piece in mem_msg.message_pieces:
                role = piece._role
                text = piece.converted_value or piece.original_value
                if role == "system":
                    lc_messages.append(SystemMessage(content=text))
                elif role == "user":
                    lc_messages.append(HumanMessage(content=text))
                elif role in ("assistant", "simulated_assistant"):
                    lc_messages.append(AIMessage(content=text))

        # Add the current incoming message if not already in history
        incoming_text = message.get_value(0)
        incoming_role = message.message_pieces[0]._role
        if incoming_role == "user":
            lc_messages.append(HumanMessage(content=incoming_text))
        elif incoming_role == "system":
            lc_messages.append(SystemMessage(content=incoming_text))

        # Invoke Claude via LangChain
        lc_response = await self._llm.ainvoke(lc_messages)
        response_text = lc_response.content

        # Build PyRIT response MessagePiece
        # DO NOT write to memory here — PyRIT's PromptNormalizer handles that
        response_piece = MessagePiece(
            role="assistant",
            original_value=response_text,
            converted_value=response_text,
            conversation_id=conversation_id,
            sequence=message.message_pieces[0].sequence,
            prompt_target_identifier=self.get_identifier(),
        )

        return [Message(message_pieces=[response_piece])]
