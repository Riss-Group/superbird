import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Set access rule to support multi-company fields
    """
    # Initialize m2m table for preserving old restrictions
    env.cr.execute(
        """
        INSERT INTO account_payment_term_company_rel
        (account_payment_term_id, res_company_id)
        SELECT id, company_id
        FROM account_payment_term
        WHERE company_id IS NOT NULL
        """
    )
