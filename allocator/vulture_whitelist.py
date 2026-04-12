# Vulture whitelist for false positives
# These are variables/functions that appear unused but are actually needed

# sklearn API compatibility - sample_weight parameter required for fit() signature
sample_weight  # noqa
