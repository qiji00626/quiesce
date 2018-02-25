import asyncio
import json
import pytest

import numpy as np
from gameanalysis import rsgame

from egta import simsched


@pytest.fixture
def jgame():
    with open('cdasim/game.json') as f:
        return json.load(f)


@pytest.fixture
def conf(jgame):
    return jgame['configuration']


@pytest.fixture
def game(jgame):
    return rsgame.emptygame_json(jgame)


@pytest.mark.asyncio
async def test_basic_profile(conf, game):
    profs = game.random_profiles(20)
    cmd = ['python3', 'cdasim/sim.py', '--single', '1']

    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        assert rsgame.emptygame_copy(sched.game()) == game
        awaited = await asyncio.gather(*[
            sched.sample_payoffs(p) for p in profs])
        pays = np.stack(awaited)
    assert pays.shape == profs.shape
    assert np.allclose(pays[profs == 0], 0)
    assert np.any(pays != 0)


@pytest.mark.asyncio
async def test_delayed_fail(conf, game):
    prof = game.random_profile()
    cmd = ['bash', '-c', 'sleep 1 && false']

    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        with pytest.raises(AssertionError):
            await sched.sample_payoffs(prof)


@pytest.mark.asyncio
async def test_immediate_fail(conf, game):
    prof = game.random_profile()
    cmd = ['bash', '-c', 'false']

    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        with pytest.raises(BrokenPipeError):
            await asyncio.gather(sched.sample_payoffs(prof),
                                 sched.sample_payoffs(prof))


@pytest.mark.asyncio
async def test_early_exit(conf, game):
    profs = game.random_profiles(20)
    cmd = ['bash', '-c', 'while read line; do : ; done']

    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        # Schedule promises but don't await
        asyncio.ensure_future(asyncio.gather(*[
            sched.sample_payoffs(p) for p in profs]))
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_read_delay_fail(conf, game):
    cmd = ['bash', '-c', 'read line && sleep 0.1 && false']

    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        future = asyncio.ensure_future(sched.sample_payoffs(
            game.random_profile()))
        with pytest.raises(AssertionError):
            await future


@pytest.mark.asyncio
async def test_read_delay_schedule_fail(conf, game):
    cmd = ['bash', '-c', 'read line && sleep 0.2 && false']

    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        future = asyncio.ensure_future(sched.sample_payoffs(
            game.random_profile()))
        await asyncio.sleep(1)  # make sure process is dead
        with pytest.raises(AssertionError):
            # Since we're using asyncio, the future actually gets assigned the
            # error before this one kicks off.
            asyncio.ensure_future(sched.sample_payoffs(game.random_profile()))
            await future


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_ignore_terminate_fail(conf, game):
    cmd = ['bash', '-c', 'trap "" SIGTERM && sleep 20']
    with simsched.SimulationScheduler(game, conf, cmd):
        # Wait for term to be captured
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_json_decode_fail(conf, game):
    cmd = ['bash', '-c',
           'read line && echo "[" && while read line; do :; done']
    prof = game.random_profile()
    with simsched.SimulationScheduler(game, conf, cmd) as sched:
        with pytest.raises(json.decoder.JSONDecodeError):
            await asyncio.gather(sched.sample_payoffs(prof),
                                 sched.sample_payoffs(prof),
                                 sched.sample_payoffs(prof))


def test_bad_command_exit(conf, game):
    with pytest.raises(FileNotFoundError):
        with simsched.SimulationScheduler(game, conf, ['unknown']):
            pass  # pragma: no cover
