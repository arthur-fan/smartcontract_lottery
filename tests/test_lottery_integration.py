from brownie import network
import pytest
from scripts.helpers import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
    get_contract,
)
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # account1 = get_account(index=1)
    # account2 = get_account(index=2)

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # lottery.enter({"from": account2, "value": lottery.getEntranceFee()})

    print(f"Account0 entered lottery: {account}")
    # print(f"Account1 entered lottery: {account1}")
    # print(f"Account2 entered lottery: {account2}")
    fund_with_link(lottery)
    prize_pool = lottery.balance()
    lottery.endLottery({"from": account})
    time.sleep(240)  # how to wait for event?

    print(f"{lottery.recentWinner()} won the lottery of {prize_pool}!")
    # assert lottery.recentWinner() == account
    assert lottery.balance() == 0
