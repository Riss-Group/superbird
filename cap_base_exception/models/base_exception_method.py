from odoo import api, models


class BaseExceptionMethod(models.AbstractModel):
    _inherit = "base.exception.method"


    def detect_exceptions(self):
        """List all exception_ids applied on self, modified to send only the one with the highest sequence
        for related exceptions."""
        # Call the original method to get all exceptions
        all_exception_ids = super().detect_exceptions()

        # Fetch all the exception rules for the returned IDs
        exception_rules = self.env["exception.rule"].search([('id', 'in', all_exception_ids)])

        # Filter rules with related_exception and keep only the highest sequence
        filtered_exception_ids = []
        if exception_rules:
            # Group by related_exception and find the one with the highest sequence in each group
            from collections import defaultdict

            exception_group_map = defaultdict(list)
            for rule in exception_rules:
                if rule.exception_group:  # Ensure exception_group is not False/None
                    exception_group_map[rule.exception_group.id].append(rule)

            filtered_exception_ids = []
            for group_id, rules in exception_group_map.items():
                if len(rules) > 1:  # Include only groups with more than one exception
                    filtered_exception_ids.extend(rule.id for rule in rules)

                filtered_exception_ids = []
                for group_id, rules in exception_group_map.items():
                    if len(rules) > 1:  # Only consider groups with more than one rule
                        # Sort rules by sequence (descending) and exclude the highest
                        sorted_rules = sorted(rules, key=lambda r: r.sequence, reverse=True)
                        filtered_exception_ids.extend(
                            rule.id for rule in sorted_rules[0])  # Keep all but the highest
                    else:
                        # For single-rule groups, include the rule
                        filtered_exception_ids.extend(rule.id for rule in rules)

                    # all_exception_ids.remove(filtered_exception_ids)
                    self.write({"exception_ids": [(6,0, filtered_exception_ids)]})

        return filtered_exception_ids