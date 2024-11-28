from odoo import api, models


class BaseExceptionMethod(models.AbstractModel):
    _inherit = "base.exception.method"


    def detect_exceptions(self):
        """List all exception_ids applied on self, modified to send only the one with the highest sequence
        for exceptions Group."""
        all_exception_ids = super().detect_exceptions()

        exception_rules = self.env["exception.rule"].search([('id', 'in', all_exception_ids)])

        if exception_rules:
            from collections import defaultdict

            exception_group_map = defaultdict(list)
            for rule in exception_rules:
                if rule.exception_group:
                    exception_group_map[rule.exception_group.id].append(rule)

            filtered_exception_ids = []
            for group_id, rules in exception_group_map.items():
                if len(rules) > 1:
                    filtered_exception_ids.extend(rule.id for rule in rules)

                filtered_exception_ids = []
                for group_id, rules in exception_group_map.items():
                    if len(rules) > 1:
                        sorted_rules = sorted(rules, key=lambda r: r.sequence, reverse=False)
                        filtered_exception_ids.extend(
                            rule.id for rule in sorted_rules[1:])

                    self.write({"exception_ids": [(3, id_to_remove) for id_to_remove in filtered_exception_ids]})
                    all_exception_ids = [eid for eid in all_exception_ids if eid not in filtered_exception_ids]

        return all_exception_ids