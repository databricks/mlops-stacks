import pytest
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

@pytest.fixture
def workspace_client():
    """Fixture to create a WorkspaceClient instance"""
    return WorkspaceClient()

@pytest.fixture
def test_messages():
    """Fixture with sample test messages"""
    return [ChatMessage(content="What is MLflow?", role=ChatMessageRole.USER)]

def test_endpoint_returns_response(workspace_client, test_messages):
    #TODO Replace with your actual endpoint name
    ENDPOINT_NAME = "endpoint_name"  
    
    response = workspace_client.serving_endpoints.query(
        name=ENDPOINT_NAME,
        messages=test_messages,
        temperature=1.0,
        stream=False,
    )
    
    # Basic assertions to verify response structure
    assert hasattr(response, 'choices'), "Response missing 'choices' field"
    assert len(response.choices) > 0, "No choices in response"
    
    first_choice = response.choices[0]
    assert hasattr(first_choice, 'message'), "Choice missing 'message' field"
    assert hasattr(first_choice.message, 'content'), "Message missing 'content' field"
    
    # Verify content is not empty
    assert isinstance(first_choice.message.content, str), "Content is not a string"
    assert len(first_choice.message.content.strip()) > 0, "Content is empty"
