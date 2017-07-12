from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        """

        """
        from django.conf import settings
        import stripe
        from stripe.error import InvalidRequestError

        stripe.api_key = settings.STRIPE_API_SECRET

        # First, check if any plans exist yet
        plans = stripe.Plan.list()

        if len(plans.data) > 0:
            return plans

        # Next, create basic plan
        try:
            stripe.Plan.retrieve("basic")
        except InvalidRequestError:
            stripe.Plan.create(
                id="basic",
                name="Basic Plan",
                amount=0,
                interval="day",
                currency="usd"
            )

        return stripe.Plan.list()
