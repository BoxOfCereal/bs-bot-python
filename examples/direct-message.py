from atproto import Client, IdResolver, models
import os
from dotenv import load_dotenv

# If you get errors try to Install from Github
# pip install git+https://github.com/MarshalX/atproto.git

# Load environment variables
load_dotenv()

# Bluesky credentials
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# The handle of the user you want to send a message to
# Must be following the user otherwise status code 400:
# `message='recipient requires incoming messages to come from someone they follow'`
TO_HANDLE = 'testification.bsky.social'

def main() -> None:
    # create client instance and login
    client = Client()
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)  # use App Password with access to Direct Messages!

    # create client proxied to Bluesky Chat service
    dm_client = client.with_bsky_chat_proxy()
    # create shortcut to convo methods
    dm = dm_client.chat.bsky.convo

    convo_list = dm.list_convos()  # use limit and cursor to paginate
    print(f'Your conversations ({len(convo_list.convos)}):')
    for convo in convo_list.convos:
        members = ', '.join(member.display_name for member in convo.members)
        print(f'- ID: {convo.id} ({members})')

    # create resolver instance with in-memory cache
    id_resolver = IdResolver()
    # resolve DID (If you attempt to send a message to yourself you will get status code 400)
    chat_to = id_resolver.handle.resolve(TO_HANDLE)

    # create or get conversation with chat_to
    convo = dm.get_convo_for_members(
        models.ChatBskyConvoGetConvoForMembers.Params(members=[chat_to]),
    ).convo

    print(f'\nConvo ID: {convo.id}')
    print('Convo members:')
    for member in convo.members:
        print(f'- {member.display_name} ({member.did})')

    # send a message to the conversation
    dm.send_message(
        models.ChatBskyConvoSendMessage.Data(
            convo_id=convo.id,
            message=models.ChatBskyConvoDefs.MessageInput(
                text='Hello from Python SDK!',
            ),
        )
    )

    print('\nMessage sent!')


if __name__ == '__main__':
    main()
