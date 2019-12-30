class ProcessingError(Exception):
    pass


class ValueProcessorBase(object):

    def process_value(self, value, context):
        raise NotImplementedError


class VariableSubstitutionProcessor(ValueProcessorBase):

    def process_value(self, value, context):
        if isinstance(value, dict):
            return {k: self.process_value(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process_value(v, context) for v in value]
        elif isinstance(value, str):
            return value % context
        return value


class StringToBoolProcessor(ValueProcessorBase):

    def process_value(self, value, context):
        if not isinstance(value, str):
            raise ProcessingError("Value is not a string")
        return value.strip() != ""
