"""Dispatch running-header policy; explicit local settings retain precedence."""
def resolve(model):
    from era_registry import for_unit
    return model["style"].get("running_matter") or for_unit(model["unit"]).running_matter(model)
