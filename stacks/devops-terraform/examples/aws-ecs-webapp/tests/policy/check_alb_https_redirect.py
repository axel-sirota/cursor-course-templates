"""Custom checkov check: ALB HTTP listeners must redirect to HTTPS.

This is the validation-first check for modules/alb — written before the
aws_lb_listener resources existed, and left in place as a regression guard.
"""
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ALBHttpsRedirect(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Ensure ALB HTTP listener redirects to HTTPS",
            id="CKV_ACME_1",
            categories=[CheckCategories.NETWORKING],
            supported_resources=["aws_lb_listener"],
        )

    def scan_resource_conf(self, conf):
        if conf.get("port") == [80]:
            actions = conf.get("default_action", [{}])
            if actions and actions[0].get("type") == ["redirect"]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.PASSED


check = ALBHttpsRedirect()
