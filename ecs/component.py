COMPONENT_REGISTRY = {}

def component(cls):
    COMPONENT_REGISTRY[cls.__name__] = cls
    return cls