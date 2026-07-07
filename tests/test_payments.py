"""Payments and Stars: Bot methods, update parsing, shortcuts, and handlers."""
from __future__ import annotations

from moonlygram import (
    Invoice,
    LabeledPrice,
    Message,
    OrderInfo,
    PreCheckoutQuery,
    RefundedPayment,
    ShippingOption,
    ShippingQuery,
    StarAmount,
    StarTransactions,
    SuccessfulPayment,
    TransactionPartner,
    Update,
)
from moonlygram.ext import PreCheckoutQueryHandler, ShippingQueryHandler
from conftest import fake_bot


def _pre_checkout_raw(**extra):
    d = {
        "id": "pcq1",
        "from": {"id": 7, "is_bot": False, "first_name": "Ann"},
        "currency": "USD",
        "total_amount": 500,
        "invoice_payload": "order-1",
    }
    d.update(extra)
    return d


def _shipping_raw(**extra):
    d = {
        "id": "sq1",
        "from": {"id": 8, "is_bot": False, "first_name": "Bo"},
        "invoice_payload": "order-2",
        "shipping_address": {
            "country_code": "US",
            "state": "CA",
            "city": "SF",
            "street_line1": "1 Main St",
            "street_line2": "",
            "post_code": "94000",
        },
    }
    d.update(extra)
    return d


class TestPaymentMethods:
    async def test_send_invoice_serializes_prices(self):
        bot, session = fake_bot(
            result={"message_id": 1, "chat": {"id": 5, "type": "private"}}
        )
        await bot.send_invoice(
            5,
            "Sub",
            "Monthly",
            "order-1",
            "USD",
            [LabeledPrice("Base", 500), LabeledPrice("Tax", 50)],
            need_shipping_address=True,
            is_flexible=True,
        )
        method, params = session.calls[-1]
        assert method == "sendInvoice"
        assert params["prices"] == [
            {"label": "Base", "amount": 500},
            {"label": "Tax", "amount": 50},
        ]
        assert params["need_shipping_address"] is True
        assert params["is_flexible"] is True
        assert "provider_token" not in params  # None params are dropped

    async def test_create_invoice_link_returns_url(self):
        bot, session = fake_bot(result="https://t.me/invoice/xyz")
        link = await bot.create_invoice_link(
            "Stars", "Ten stars", "order-3", "XTR", [LabeledPrice("Stars", 10)]
        )
        assert link == "https://t.me/invoice/xyz"
        method, params = session.calls[-1]
        assert method == "createInvoiceLink"
        assert params["currency"] == "XTR"
        assert params["prices"] == [{"label": "Stars", "amount": 10}]

    async def test_answer_shipping_query_serializes_options(self):
        bot, session = fake_bot(result=True)
        ok = await bot.answer_shipping_query(
            "sq1",
            True,
            shipping_options=[
                ShippingOption("fast", "Fast", [LabeledPrice("Ship", 200)])
            ],
        )
        assert ok is True
        method, params = session.calls[-1]
        assert method == "answerShippingQuery"
        assert params["ok"] is True
        assert params["shipping_options"] == [
            {"id": "fast", "title": "Fast", "prices": [{"label": "Ship", "amount": 200}]}
        ]

    async def test_answer_pre_checkout_query_reject(self):
        bot, session = fake_bot(result=True)
        await bot.answer_pre_checkout_query("pcq1", False, error_message="Sold out")
        method, params = session.calls[-1]
        assert method == "answerPreCheckoutQuery"
        assert params["ok"] is False
        assert params["error_message"] == "Sold out"


class TestPaymentUpdates:
    def test_update_parses_pre_checkout_query(self):
        update = Update.from_dict(
            {"update_id": 1, "pre_checkout_query": _pre_checkout_raw(
                shipping_option_id="fast", order_info={"name": "Ann"})}
        )
        query = update.pre_checkout_query
        assert isinstance(query, PreCheckoutQuery)
        assert query.total_amount == 500
        assert query.shipping_option_id == "fast"
        assert isinstance(query.order_info, OrderInfo) and query.order_info.name == "Ann"
        assert update.effective_user_id == 7

    def test_update_parses_shipping_query(self):
        update = Update.from_dict({"update_id": 2, "shipping_query": _shipping_raw()})
        query = update.shipping_query
        assert isinstance(query, ShippingQuery)
        assert query.invoice_payload == "order-2"
        assert query.shipping_address.city == "SF"
        assert update.effective_user_id == 8

    def test_message_parses_payment_fields(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "invoice": {
                    "title": "Sub",
                    "description": "Monthly",
                    "start_parameter": "s",
                    "currency": "USD",
                    "total_amount": 500,
                },
                "successful_payment": {
                    "currency": "USD",
                    "total_amount": 500,
                    "invoice_payload": "order-1",
                    "telegram_payment_charge_id": "tg1",
                    "provider_payment_charge_id": "pv1",
                    "order_info": {"name": "Ann"},
                },
                "refunded_payment": {
                    "currency": "USD",
                    "total_amount": 500,
                    "invoice_payload": "order-1",
                    "telegram_payment_charge_id": "tg1",
                },
            }
        )
        assert isinstance(msg.invoice, Invoice) and msg.invoice.total_amount == 500
        assert isinstance(msg.successful_payment, SuccessfulPayment)
        assert msg.successful_payment.order_info.name == "Ann"
        assert isinstance(msg.refunded_payment, RefundedPayment)
        assert msg.refunded_payment.provider_payment_charge_id is None

    async def test_pre_checkout_query_answer_shortcut(self):
        bot, session = fake_bot(result=True)
        update = Update.from_dict({"update_id": 1, "pre_checkout_query": _pre_checkout_raw()})
        update.set_bot(bot)
        await update.pre_checkout_query.answer(True)
        method, params = session.calls[-1]
        assert method == "answerPreCheckoutQuery"
        assert params["pre_checkout_query_id"] == "pcq1"
        assert params["ok"] is True
        assert update.pre_checkout_query.from_user._bot is bot

    async def test_shipping_query_answer_shortcut(self):
        bot, session = fake_bot(result=True)
        update = Update.from_dict({"update_id": 2, "shipping_query": _shipping_raw()})
        update.set_bot(bot)
        await update.shipping_query.answer(
            True, shipping_options=[ShippingOption("f", "Fast", [LabeledPrice("S", 1)])]
        )
        method, params = session.calls[-1]
        assert method == "answerShippingQuery"
        assert params["shipping_query_id"] == "sq1"
        assert params["shipping_options"][0]["title"] == "Fast"


class TestPaymentHandlers:
    async def _noop(self, update, context):
        return None

    def test_shipping_query_handler_matches(self):
        handler = ShippingQueryHandler(self._noop)
        assert handler.check_update(
            Update.from_dict({"update_id": 1, "shipping_query": _shipping_raw()})
        )
        assert not handler.check_update(
            Update.from_dict({"update_id": 2, "pre_checkout_query": _pre_checkout_raw()})
        )

    def test_pre_checkout_query_handler_matches(self):
        handler = PreCheckoutQueryHandler(self._noop)
        assert handler.check_update(
            Update.from_dict({"update_id": 1, "pre_checkout_query": _pre_checkout_raw()})
        )
        assert not handler.check_update(Update(update_id=2))


class TestStars:
    async def test_get_star_transactions(self):
        bot, session = fake_bot(result={"transactions": []})
        result = await bot.get_star_transactions(offset=5, limit=10)
        assert isinstance(result, StarTransactions)
        method, params = session.calls[-1]
        assert method == "getStarTransactions"
        assert params == {"offset": 5, "limit": 10}

    async def test_get_my_star_balance(self):
        bot, session = fake_bot(result={"amount": 42, "nanostar_amount": 500})
        balance = await bot.get_my_star_balance()
        assert isinstance(balance, StarAmount)
        assert balance.amount == 42 and balance.nanostar_amount == 500
        assert session.calls[-1][0] == "getMyStarBalance"

    async def test_refund_star_payment(self):
        bot, session = fake_bot(result=True)
        ok = await bot.refund_star_payment(9, "tg-charge-1")
        assert ok is True
        assert session.calls[-1] == (
            "refundStarPayment",
            {"user_id": 9, "telegram_payment_charge_id": "tg-charge-1"},
        )

    async def test_edit_user_star_subscription(self):
        bot, session = fake_bot(result=True)
        await bot.edit_user_star_subscription(9, "tg-charge-1", True)
        method, params = session.calls[-1]
        assert method == "editUserStarSubscription"
        assert params["is_canceled"] is True

    def test_star_transaction_parses_partner_union(self):
        result = StarTransactions.from_dict(
            {
                "transactions": [
                    {
                        "id": "tx1",
                        "amount": 100,
                        "date": 1700000000,
                        "source": {
                            "type": "user",
                            "transaction_type": "invoice_payment",
                            "user": {"id": 9, "is_bot": False, "first_name": "Z"},
                            "affiliate": {"commission_per_mille": 50, "amount": 5},
                            "gift": {"id": "g1"},
                            "paid_media": [{"type": "photo"}],
                        },
                    }
                ]
            }
        )
        tx = result.transactions[0]
        assert tx.amount == 100
        assert isinstance(tx.source, TransactionPartner)
        assert tx.source.type == "user" and tx.source.user.id == 9
        assert tx.source.affiliate.commission_per_mille == 50
        # Types from later batches degrade to raw dicts, not parsed objects.
        assert tx.source.gift == {"id": "g1"}
        assert tx.source.paid_media == [{"type": "photo"}]

    def test_fragment_partner_withdrawal_state(self):
        partner = TransactionPartner.from_dict(
            {
                "type": "fragment",
                "withdrawal_state": {
                    "type": "succeeded",
                    "date": 1700000001,
                    "url": "https://example/withdraw",
                },
            }
        )
        assert partner.type == "fragment"
        assert partner.withdrawal_state.type == "succeeded"
        assert partner.withdrawal_state.url == "https://example/withdraw"
