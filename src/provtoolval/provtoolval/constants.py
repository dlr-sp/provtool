report_schema = {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["entity", "valid", "used_by"],
    "properties": {
      "entity": {"type": "string"},
      "valid": {"type": "boolean"},
      "used_by": {
        "type": "array",
        "items": {"type": ["string", "null"]}
      },
      "used": {
        "type": "array",
        "items": {"type": ["string", "null"]}
      }
    }
  }
}
