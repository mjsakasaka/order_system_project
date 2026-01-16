from tests_api.conftest import auth_header


def transition(client, token, order_id: int, action: str):
    return client.post(
        f"/api/v1/orders/{order_id}/transition",
        json={"action": action},
        headers=auth_header(token),
    )


def assert_error(resp, status_code: int, error_code: str):
    assert resp.status_code == status_code, resp.text
    data = resp.json()
    assert data["error_code"] == error_code
    assert "trace_id" in data and data["trace_id"]
    return data


def test_trace_id_header_exists_on_success(client, cs_token, make_order):
    order_id = make_order()
    resp = transition(client, cs_token, order_id, "PAY")
    assert resp.status_code == 200, resp.text
    assert "X-Trace-Id" in resp.headers
    assert resp.headers["X-Trace-Id"]


def test_happy_path_created_to_paid(client, cs_token, make_order):
    order_id = make_order()
    resp = transition(client, cs_token, order_id, "PAY")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["from_status"] == "CREATED"
    assert data["to_status"] == "PAID"


def test_wh_cannot_pay(client, wh_token, make_order):
    order_id = make_order()
    resp = transition(client, wh_token, order_id, "PAY")
    assert_error(resp, 403, "AUTH_FORBIDDEN")


def test_cannot_cancel_after_paid(client, cs_token, make_order):
    order_id = make_order()

    resp1 = transition(client, cs_token, order_id, "PAY")
    assert resp1.status_code == 200, resp1.text

    resp2 = transition(client, cs_token, order_id, "CANCEL")
    assert_error(resp2, 409, "ORDER_STATE_INVALID")


def test_unknown_action_should_be_invalid(client, admin_token, make_order):
    order_id = make_order()
    resp = transition(client, admin_token, order_id, "NOT_A_REAL_ACTION")
    assert_error(resp, 409, "ORDER_STATE_INVALID")


def test_terminal_status_cannot_transition(client, admin_token, make_order):
    """
    走到 COMPLETED 后，再尝试任何动作都应该失败（终态不可流转）
    """
    order_id = make_order()

    # CREATED -> PAID
    resp = transition(client, admin_token, order_id, "PAY")
    assert resp.status_code == 200, resp.text

    # PAID -> PACKED
    resp = transition(client, admin_token, order_id, "PACK")
    assert resp.status_code == 200, resp.text

    # PACKED -> SHIPPED
    resp = transition(client, admin_token, order_id, "SHIP")
    assert resp.status_code == 200, resp.text

    # SHIPPED -> COMPLETED
    resp = transition(client, admin_token, order_id, "COMPLETE")
    assert resp.status_code == 200, resp.text
    assert resp.json()["to_status"] == "COMPLETED"

    # COMPLETED -> PAY (illegal, terminal)
    resp = transition(client, admin_token, order_id, "PAY")
    assert_error(resp, 409, "ORDER_STATE_INVALID")
