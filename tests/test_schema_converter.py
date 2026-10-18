from app.schema_converter import normalize_schema
import google.generativeai as genai

def test_schema_converter():
    mcp_schema = {
        'properties': {
            'location': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Location'},
            'max_price': {'anyOf': [{'type': 'number'}, {'type': 'null'}], 'default': None, 'title': 'Max Price'}
        },
        'title': 'search_campgroundsArguments',
        'type': 'object'
    }

    normalized = normalize_schema(mcp_schema)

    # Should not have 'title'
    assert 'title' not in normalized
    # Should have 'properties'
    assert 'properties' in normalized
    # Should have 'type_'
    assert normalized['type_'] == 'OBJECT'

    # Verify it can construct a proto
    # Constructing a proto Schema is complex with the SDK.
    # Let's verify it can at least be passed to a FunctionDeclaration dict (which the SDK might accept)

    declaration = {
        "name": "test_tool",
        "description": "test description",
        "parameters": normalized
    }

    # This should not raise ValueError: Unknown field for Schema: title
    try:
        genai.protos.FunctionDeclaration(**declaration)
    except Exception as e:
        pytest.fail(f"Failed to create FunctionDeclaration: {e}")

if __name__ == "__main__":
    test_schema_converter()
    print("Schema converter test passed!")
