from typing import Any, Dict

def normalize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively converts MCP JSON Schema (Pydantic style) to Gemini protos.Schema format.
    """
    if not isinstance(schema, dict):
        return schema

    new_schema = {}

    # Map types
    if "type" in schema:
        # Handle Union[T, null] as nullable
        if isinstance(schema["type"], dict) and "anyOf" in schema:
             # Look for type and null
             types = [t.get("type") for t in schema["anyOf"] if "type" in t]
             if "null" in [t.get("type") for t in schema["anyOf"] if "type" in t]:
                 # It's nullable
                 actual_types = [t for t in types if t != "null"]
                 if actual_types:
                     new_schema["type_"] = _map_type(actual_types[0])
                     new_schema["nullable"] = True
             else:
                 new_schema["type_"] = _map_type(schema["type"])
        else:
             new_schema["type_"] = _map_type(schema["type"])

    # Map properties
    if "properties" in schema:
        new_schema["properties"] = {
            k: normalize_schema(v) for k, v in schema["properties"].items()
        }

    # Map items
    if "items" in schema:
        new_schema["items"] = normalize_schema(schema["items"])

    # Map description
    if "description" in schema:
        new_schema["description"] = schema["description"]

    # Map required (must be list of strings)
    if "required" in schema:
        new_schema["required"] = schema["required"]

    return new_schema

def _map_type(t: str) -> str:
    mapping = {
        "string": "STRING",
        "number": "NUMBER",
        "integer": "INTEGER",
        "boolean": "BOOLEAN",
        "array": "ARRAY",
        "object": "OBJECT",
    }
    return mapping.get(t, "STRING")
