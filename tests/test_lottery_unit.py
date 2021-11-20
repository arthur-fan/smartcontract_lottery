from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # $50 * (1 ETH / $4000) = 0.0125 ETH
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.0125, "ether")
    # Assert
    assert entrance_fee == expected_entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lottery_state() == 2  # CALCULATING_WINNER


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account0 = get_account()
    account1 = get_account(index=1)
    account2 = get_account(index=2)
    # Act
    lottery.startLottery({"from": account0})
    lottery.enter({"from": account0, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account1, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account2, "value": lottery.getEntranceFee()})

    print(f"Account0 entered lottery: {account0}")
    print(f"Account1 entered lottery: {account1}")
    print(f"Account2 entered lottery: {account2}")

    fund_with_link(lottery)
    tx = lottery.endLottery({"from": account0})

    request_id = tx.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 888
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account0}
    )

    starting_balance_of_account = account0.balance()
    balance_of_lottery = lottery.balance()
    # 888 % 3 = 0
    print(f"{lottery.recentWinner()} won the lottery of {account0.balance()}!")
    print(type(lottery.recentWinner()))
    print(type(account0))
    assert lottery.recentWinner() == account0
    assert lottery.balance() == 0
    assert account0.balance() == starting_balance_of_account + balance_of_lottery
