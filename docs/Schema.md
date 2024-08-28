
# Schema for FIREpyDAQ Config

Below is the schema used to validate configuration `.json` files used to import in the GUI.

```{jsonschema} firepydaq.acquisition.schema.schema
```

The following is the literal schema. Note that `Name`, `Experiment Name`, `Test Name`, `Sampling Rate`, `Formulae File`, `Experiment Type`, `Config File` are required parameters.
```{literalinclude} ../firepydaq/acquisition/schema.py
:start-after: start schema
:end-before: end schema
```

