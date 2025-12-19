from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway

from bot import config


def get_gateway(name: str):
    """Get payment gateway instance"""
    gateways = {
        "payme": lambda: PaymeGateway(
            payme_id=config.PAYME_ID,
            payme_key=config.PAYME_KEY,
            is_test_mode=config.IS_TEST_MODE,
        ),
        "click": lambda: ClickGateway(
            service_id=config.CLICK_SERVICE_ID,
            merchant_id=config.CLICK_MERCHANT_ID,
            merchant_user_id=config.CLICK_MERCHANT_USER_ID,
            secret_key=config.CLICK_SECRET_KEY,
            is_test_mode=config.IS_TEST_MODE,
        ),
        "atmos": lambda: AtmosGateway(
            consumer_key=config.ATMOS_CONSUMER_KEY,
            consumer_secret=config.ATMOS_CONSUMER_SECRET,
            store_id=config.ATMOS_STORE_ID,
            terminal_id=config.ATMOS_TERMINAL_ID,
            is_test_mode=config.IS_TEST_MODE,
        ),
    }
    factory = gateways.get(name)
    return factory() if factory else None
