
schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "Name": {
                    "type": "string"
                },
                "Experiment Name": {
                    "type": "string"
                },
                "Test Name": {
                    "type": "string"
                },
                "Sampling Rate": {
                    "type": "number",
                    "minimum": 0
                },
                "Formulae File": {
                    "type": "string"
                },
                "Experiment Type": {
                    "type": "string"
                },
                "Config File": {
                    "type": "string"
                },
                "Devices": {
                    "type": "object",
                "properties": {
                    "Lasers": {
                        "type": "object",
                            "patternProperties": {
                                "^[a-zA-Z0-9_-]+$": {
                                    "type": "object",
                                    "properties": {
                                            "COMPORT": {
                                                "type": "string"
                                            },
                                            "P": {
                                                "type": "number"
                                            },
                                            "I": {
                                                "type": "number"
                                            },
                                            "D": {
                                                "type": "number"
                                            },
                                            "Laser Rate": {
                                                "type": "number"
                                            },
                                            "Tec Rate": {
                                                "type": "number"
                                            }
                                        },
                                    "required": ["COMPORT", "P", "I", "D", "Laser Rate", "Tec Rate"]
                                    }
                                }
                            },
                    "MFCs": {
                        "type": "object",
                            "patternProperties": {
                                "^[a-zA-Z0-9_-]+$": {
                                "type": "object",
                                "properties": {
                                    "COMPORT": {
                                        "type": "string"
                                    },
                                    "Gas": {
                                        "type": "string"
                                    },
                                    "Rate": {
                                        "type": "number"
                                    },
                                    "Type": {
                                        "type": "string"
                                    }
                                },
                                "required": ["COMPORT", "Gas", "Rate", "Type"]
                            }
                        }
                    }
                }
            }
        },
      "required": ["Name", "Experiment Name", "Test Name", "Sampling Rate", "Formulae File", "Experiment Type", "Config File"],
    }
"""Schema for FIREpyDAQ configuration file
"""
