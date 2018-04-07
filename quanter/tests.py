from django.test import TestCase
from quanter.views import buy_when_large_departure


# Create your tests here.
# a separate TestClass for each model or view
# a separate test method for each set of conditions you want to test
class TestWhenLargeDeparture(TestCase):
    def test_is_yin_xian(self):
        self.assertIs(buy_when_large_departure.is_yin_xian(9.5, 9.4), False)
        self.assertIs(buy_when_large_departure.is_yin_xian(9.5, 9.5), False)
        self.assertIs(buy_when_large_departure.is_yin_xian(9.5, 9.6), True)

    def test_is_yang_xian(self):
        self.assertIs(buy_when_large_departure.is_yang_xian(9.5, 9.4), True)
        self.assertIs(buy_when_large_departure.is_yang_xian(9.5, 9.5), False)
        self.assertIs(buy_when_large_departure.is_yang_xian(9.5, 9.6), False)

    def test_is_sell_state(self):
        self.assertIs(buy_when_large_departure.is_sell_state(-1.0), False)
        self.assertIs(buy_when_large_departure.is_sell_state(-0.5), True)
        self.assertIs(buy_when_large_departure.is_sell_state(1), True)

    def test_is_buy_state(self):
        self.assertIs(buy_when_large_departure.is_buy_state(9.5, 9.6, 9.6, 9.7, 10.0, 10.1, -1), False)
        self.assertIs(buy_when_large_departure.is_buy_state(9.5, 9.6, 9.6, 9.7, 9.7, 9.8, -1), False)
        self.assertIs(buy_when_large_departure.is_buy_state(9.5, 9.6, 9.6, 9.3, 9.5, 9.5, -1), False)
        self.assertIs(buy_when_large_departure.is_buy_state(9.5, 9.6, 9.6, 9.3, 9.5, 9.5, -3), True)
        self.assertIs(buy_when_large_departure.is_buy_state(9.5, 9.6, 9.6, 9.3, 9.5, 9.5, -4), True)

