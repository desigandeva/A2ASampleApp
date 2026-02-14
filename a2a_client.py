import asyncio
from typing import Any
from uuid import uuid4
import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import MessageSendParams, SendMessageRequest


async def main():
    base_url = 'http://127.0.0.1:9999'
    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )
        final_agent_card_to_use = await resolver.get_agent_card()
        print(final_agent_card_to_use)

        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )

        # non-streamable
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'how much is 10 USD in INR?'}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        print(response.model_dump(mode='json', exclude_none=True))


if __name__ == "__main__":
    asyncio.run(main())


# streamable
# streaming_request = SendStreamingMessageRequest(
#     id=str(uuid4()), params=MessageSendParams(**send_message_payload)
# )

# stream_response = client.send_message_streaming(streaming_request)

# async for chunk in stream_response:
#     print(chunk.model_dump(mode='json', exclude_none=True))