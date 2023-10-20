CONSTRUCT_HELM_OVERRIDED_VALUES = """
You will be provided the default values of a helm chart, and a user query describing a deployment task.

Output overrided values(in yaml) for the helm installation to satisfy the user query.
You don't need to include values that are the same as the default values.
If no values are overrided, output an empty yaml.


USER QUERY:
{query}

DEFAULT VALUES:
{default_values}

OVERRIDED VALUES:
"""

CONSTRUCT_HELM_UPGRADE_VALUES = """
You will be provided the default values of a helm chart, previous values of a helm release, and a user query describing an upgrade task.

Output values(in yaml) used for the helm upgrade to satisfy the user query.
Keep the previous values in the output unlesss it need to be changed according to the user query.
If you are not sure about some values, use the default.

USER QUERY:
{query}

DEFAULT VALUES:
{default_values}

PREVIOUS VALUES:
{previous_values}

VALUES FOR UPGRADE:
"""
