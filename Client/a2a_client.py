import asyncio
import json
from typing import Any
from uuid import uuid4
import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import MessageSendParams, SendMessageRequest
import os

EXITLIST = ["exit", "quit", "q", "stop", "kill"]

class AgentDiscovery:
    def __init__(self):
        self.base_urls = self.get_remote_agents()

    def get_remote_agents(self):
        config_path = os.path.expanduser('~/a2asampleapp/Client/a2a_config.json')
        with open(config_path, 'r') as f:
            remote_agents = json.load(f)
        base_urls = remote_agents["servers"]
        print(base_urls)
        return base_urls


async def main():

    remote_agents = AgentDiscovery()
    base_url = remote_agents.base_urls[1]

    while True:
        user_query = input("Enter Your Query : ")

        if user_query.lower() in EXITLIST:
            print("Bye..")
            break

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
                        {'kind': 'text', 'text': user_query}
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
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")