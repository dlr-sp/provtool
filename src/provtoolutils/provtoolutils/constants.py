model_encoding = 'utf-8'

config_schema = {
    "definitions": {
        "agents": {
            "anyOf": [
                {
                    "type": "object",
                    "required": ["family_name", "given_name", "type"],
                    "properties": {
                        "family_name": {"type": "string"},
                        "given_name": {"type": "string"},
                        "type": {"const": "person"},
                        "acted_on_behalf_of": {"$ref": "#/definitions/agents"}
                    }
                },
                {
                    "type": "object",
                    "required": ["label", "type"],
                    "properties": {
                        "label": {"type": "string"},
                        "type": {"const": "organization"}
                    }
                },
                {
                    "type": "object",
                    "required": ["type", "creator", "version", "location", "label"],
                    "properties": {
                        "type": {"const": "software"},
                        "creator": {"type": "string"},
                        "version": {"type": "string"},
                        "location": {"type": "string"},
                        "label": {"type": "string"},
                        "acted_on_behalf_of": {"$ref": "#/definitions/agents"}
                    }
                }
            ]
        }
    },
    "type": "object",
    "required": ["activity"],
    "properties": {
        "activity": {
            "type": "object",
            "required": ["location", "label", "means"],
            "properties": {
                "location": {"type": "string"},
                "label": {"type": "string"},
                "means": {"type": "string"},
            }
        },
        "agent": {"$ref": "#/definitions/agents"}
    }
}
agent_schema = {
    "definitions": {
        "agents": {
            "anyOf": [
                {
                    "type": "object",
                    "required": ["family_name", "given_name", "type"],
                    "properties": {
                        "family_name": {"type": "string"},
                        "given_name": {"type": "string"},
                        "type": {"const": "person"},
                        "acted_on_behalf_of": {"$ref": "#/definitions/agents"}
                    }
                },
                {
                    "type": "object",
                    "required": ["label", "type"],
                    "properties": {
                        "label": {"type": "string"},
                        "type": {"const": "organization"}
                    }
                },
                {
                    "type": "object",
                    "required": ["type", "creator", "version", "location", "label", "acted_on_behalf_of"],
                    "properties": {
                        "type": {"const": "software"},
                        "creator": {"type": "string"},
                        "version": {"type": "string"},
                        "location": {"type": "string"},
                        "label": {"type": "string"},
                        "acted_on_behalf_of": {"$ref": "#/definitions/agents"}
                    }
                }
            ]
        }
    },
    "type": "object",
    "required": ["agent"],
    "properties": {
        "agent": {"$ref": "#/definitions/agents"}
    }
}

# Activity, agent, entity does not hav an explicit prov:id mentioned here, because the json
# serialization of the W3C prov model stores each of the three elements in a subobject, which
# has the prov:id as key.
prov_schema = {
    "type": "object",
    "required": ["activity", "agent", "entity", "prefix"],
    "properties": {
        "activity": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "required": ["prov:startTime", "prov:endTime", "prov:label", "prov:location", "provtool:means"],
                    "properties": {
                        "prov:startTime": {"type": "string"},
                        "prov:endTime": {"type": "string"},
                        "prov:label": {"type": "string"},
                        "prov:location": {"type": "string"},
                        "provtool:means": {"type": "string"}
                    }
                }
            }
        },
        "agent": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                ".*": {
                    "anyOf": [
                        {
                            "type": "object",
                            "required": ["person:familyName", "person:givenName", "prov:label", "prov:type"],
                            "properties": {
                                "person:familyName": {"type": "string"},
                                "person:givenName": {"type": "string"},
                                "prov:label": {"type": "string"},
                                "prov:type": {"const": "prov:Person"}
                            }
                        },
                        {
                            "type": "object",
                            "required": ["prov:label", "prov:type"],
                            "properties": {
                                "prov:label": {"type": "string"},
                                "prov:type": {"const": "prov:Organization"}
                            }
                        },
                        {
                            "type": "object",
                            "required": ["prov:type", "creative:creator", "software:softwareVersion",
                                         "prov:location", "prov:label"],
                            "properties": {
                                "prov:type": {"const": "prov:SoftwareAgent"},
                                "creative:creator": {"type": "string"},
                                "software:softwareVersion": {"type": "string"},
                                "prov:location": {"type": "string"},
                                "prov:label": {"type": "string"}
                            }
                        }
                    ]
                }
            }
        },
        "entity": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "required": ["prov:label", "prov:type", "provtool:datahash"],
                    "properties": {
                        "prov:label": {"type": "string"},
                        "prov:type": {"type": "string"},
                        "provtool:datahash": {"type": "string"}
                    }
                }
            }
        },
        "prefix": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                ".*": {"type": "string"}
            }
        },
        "used": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "not": {"type": "array"},
                    "required": ["prov:activity", "prov:entity"],
                    "properties": {
                        "prov:activity": {"type": "string"},
                        "prov:entity": {"type": "string"}
                    }
                }
            }
        }
    }
}
