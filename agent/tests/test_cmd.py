import asyncio
from unittest.mock import MagicMock

import asynctest
import pytest

import balrogagent.cmd


@asynctest.patch("balrogagent.client.request")
@asynctest.patch("balrogagent.cmd.telemetry_is_ready")
@asynctest.patch("balrogagent.cmd.time_is_ready")
class TestRunAgent(asynctest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    async def _runAgent(self, scheduled_changes, request):
        def side_effect(balrog_api_root, endpoint, loop, auth0_secrets, method="GET"):
            if "required_signoffs" in endpoint:
                endpoint = "/".join(endpoint.split("/")[-2:])
            else:
                endpoint = endpoint.split("/")[-1]
            changes = scheduled_changes.get(endpoint) or []
            if method != "GET":
                body = ""
            else:
                body = {"count": len(changes), "scheduled_changes": changes}
            return body

        request.side_effect = side_effect

        return await balrogagent.cmd.run_agent(self.loop, "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    async def testNoChanges(self, time_is_ready, telemetry_is_ready, request):
        sc = {}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 0)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("time.time")
    async def testTimeBasedNotReadyRules(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 0
        time_is_ready.return_value = False
        sc = {"rules": [{"priority": None, "sc_id": 4, "when": 23456789, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("time.time")
    async def testTimeBasedNotReadyReleases(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 0
        time_is_ready.return_value = False
        sc = {"releases": [{"sc_id": 4, "when": 23456789, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("time.time")
    async def testTimeBasedNotReadyPermissions(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 0
        time_is_ready.return_value = False
        sc = {"permissions": [{"sc_id": 4, "when": 23456789, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("time.time")
    async def testTimeBasedIsNotReadyRequiredSignoffs(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 0
        time_is_ready.return_value = False
        sc = {
            "required_signoffs/product": [{"sc_id": 4, "when": 23456789, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
            "required_signoffs/permissions": [{"sc_id": 4, "when": 23456789, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 2)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("time.time")
    async def testTimeBasedIsReadyRules(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {"rules": [{"priority": None, "sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 9)

    @asynctest.patch("time.time")
    async def testTimeBasedIsReadyReleases(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {"releases": [{"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 9)

    @asynctest.patch("time.time")
    async def testTimeBasedIsReadyPermissions(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {"permissions": [{"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 9)

    @asynctest.patch("time.time")
    async def testTimeBasedIsReadyRequiredSignoffs(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {
            "required_signoffs/product": [{"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
            "required_signoffs/permissions": [{"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 2)
        self.assertEqual(request.call_count, 10)

    @asynctest.patch("balrogagent.cmd.get_telemetry_uptake")
    async def testTelemetryBasedNotReady(self, get_telemetry_uptake, time_is_ready, telemetry_is_ready, request):
        telemetry_is_ready.return_value = False
        get_telemetry_uptake.return_value = 0
        sc = {"rules": [{"priority": None, "sc_id": 4, "when": None, "telemetry_uptake": 1000, "telemetry_product": "foo", "telemetry_channel": "bar"}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 1)
        self.assertEqual(time_is_ready.call_count, 0)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("balrogagent.cmd.get_telemetry_uptake")
    async def testTelemetryBasedIsReady(self, get_telemetry_uptake, time_is_ready, telemetry_is_ready, request):
        telemetry_is_ready.return_value = True
        get_telemetry_uptake.return_value = 20000
        sc = {"rules": [{"priority": None, "sc_id": 4, "when": None, "telemetry_uptake": 1000, "telemetry_product": "foo", "telemetry_channel": "bar"}]}
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 1)
        self.assertEqual(time_is_ready.call_count, 0)
        self.assertEqual(request.call_count, 9)

    @asynctest.patch("time.time")
    async def testMultipleEndpointsAtOnce(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {
            "releases": [{"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
            "rules": [{"priority": None, "sc_id": 5, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
            "permissions": [{"sc_id": 6, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None}],
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 3)
        self.assertEqual(request.call_count, 11)

    @asynctest.patch("time.time")
    async def testMultipleChangesOneEndpoint(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {
            "releases": [
                {"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 5, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 6, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
            ]
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 3)
        self.assertEqual(request.call_count, 11)
        called_endpoints = [call[0][1] for call in request.call_args_list]
        self.assertIn("/scheduled_changes/releases", called_endpoints)
        self.assertIn("/scheduled_changes/permissions", called_endpoints)
        self.assertIn("/scheduled_changes/rules", called_endpoints)
        self.assertIn("/scheduled_changes/emergency_shutoff", called_endpoints)
        self.assertIn("/scheduled_changes/releases/4/enact", called_endpoints)
        self.assertIn("/scheduled_changes/releases/5/enact", called_endpoints)
        self.assertIn("/scheduled_changes/releases/6/enact", called_endpoints)

    @asynctest.patch("time.time")
    async def testSignoffsPresent(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {
            "permissions": [
                {
                    "sc_id": 4,
                    "when": 234,
                    "telemetry_uptake": None,
                    "telemetry_product": None,
                    "telemetry_channel": None,
                    "signoffs": {"bill": "releng", "mary": "relman"},
                    "required_signoffs": {"releng": 1, "relman": 1},
                }
            ]
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 9)

    @asynctest.patch("time.time")
    async def testSignoffsAbsent(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {
            "permissions": [
                {
                    "sc_id": 4,
                    "when": 234,
                    "telemetry_uptake": None,
                    "telemetry_product": None,
                    "telemetry_channel": None,
                    "signoffs": {"mary": "relman"},
                    "required_signoffs": {"releng": 1, "relman": 1},
                }
            ]
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 1)
        self.assertEqual(request.call_count, 8)

    @asynctest.patch("time.time")
    async def testRightEnactOrderForMultipleEndpointsAtOnce(self, time, time_is_ready, telemetry_is_ready, request):
        time.return_value = 999999999
        time_is_ready.return_value = True
        sc = {
            "releases": [
                {"sc_id": 4, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 5, "when": 234, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 6, "when": 378, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 7, "when": 187, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
            ],
            "rules": [
                {"priority": 100, "sc_id": 1, "when": 23400, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"priority": None, "sc_id": 2, "when": 7000, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"priority": 70, "sc_id": 4, "when": 7000, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"priority": 50, "sc_id": 3, "when": 329, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
            ],
            "permissions": [
                {"sc_id": 8, "when": 45400, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 9, "when": 98000, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
                {"sc_id": 10, "when": 5000, "telemetry_uptake": None, "telemetry_product": None, "telemetry_channel": None},
            ],
        }
        await self._runAgent(sc, request)
        self.assertEqual(telemetry_is_ready.call_count, 0)
        self.assertEqual(time_is_ready.call_count, 11)
        self.assertEqual(request.call_count, 19)
        called_endpoints = [call[0][1] for call in request.call_args_list]
        self.assertLess(called_endpoints.index("/scheduled_changes/rules"), called_endpoints.index("/scheduled_changes/releases"))
        self.assertLess(called_endpoints.index("/scheduled_changes/rules/1/enact"), called_endpoints.index("/scheduled_changes/rules/4/enact"))
        self.assertLess(called_endpoints.index("/scheduled_changes/rules/4/enact"), called_endpoints.index("/scheduled_changes/rules/2/enact"))
        self.assertLess(called_endpoints.index("/scheduled_changes/rules/2/enact"), called_endpoints.index("/scheduled_changes/rules/3/enact"))


@pytest.mark.asyncio
async def test_v2_releases_no_changes(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {"name": "Firefox-64.0-build1", "product": None, "data_version": None, "read_only": None, "rule_info": {}, "scheduled_changes": []}
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(return_value=False)
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 0
    assert verify_signoffs.call_count == 0
    # Once for each v1 endpoint, once for each v2 endpoint
    assert fr.call_count == 8


@pytest.mark.asyncio
async def test_v2_releases_one_change(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {
                        "name": "Firefox-64.0-build1",
                        "product": None,
                        "data_version": None,
                        "read_only": None,
                        "rule_info": {},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-64.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    }
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 1
    assert verify_signoffs.call_count == 1
    # Once for each v1 endpoint, once for each v2 endpoint, once to enact
    assert fr.call_count == 9
    called_endpoints = [call[0][1] for call in fr.call_args_list]
    assert "/v2/releases/Firefox-64.0-build1/enact" in called_endpoints


@pytest.mark.asyncio
async def test_v2_releases_multiple_changes_one_release(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {
                        "name": "Firefox-64.0-build1",
                        "product": None,
                        "data_version": None,
                        "read_only": None,
                        "rule_info": {},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-64.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Linux_x86-gcc3.locales.en-US",
                                "data_version": 1,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    }
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 3
    assert verify_signoffs.call_count == 3
    # Once for each v1 endpoint, once for each v2 endpoint, once to enact
    assert fr.call_count == 9
    called_endpoints = [call[0][1] for call in fr.call_args_list]
    assert "/v2/releases/Firefox-64.0-build1/enact" in called_endpoints


@pytest.mark.asyncio
async def test_v2_releases_multiple_changes_multiple_releases(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {
                        "name": "Firefox-64.0-build1",
                        "product": None,
                        "data_version": None,
                        "read_only": None,
                        "rule_info": {},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-64.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Linux_x86-gcc3.locales.en-US",
                                "data_version": 1,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    },
                    {
                        "name": "Firefox-66.0-build1",
                        "product": "Firefox",
                        "data_version": 1,
                        "read_only": False,
                        "rule_info": {"3": {"product": "Firefox", "channel": "release"}},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-66.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "update",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-66.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 6,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "update",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    },
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 5
    assert verify_signoffs.call_count == 5
    # Once for each v1 endpoint, once for each v2 endpoint, once to enact each release's scheduled changes
    assert fr.call_count == 10
    called_endpoints = [call[0][1] for call in fr.call_args_list]
    assert "/v2/releases/Firefox-64.0-build1/enact" in called_endpoints
    assert "/v2/releases/Firefox-66.0-build1/enact" in called_endpoints


@pytest.mark.asyncio
async def test_v2_releases_multiple_changes_not_all_ready(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {
                        "name": "Firefox-64.0-build1",
                        "product": None,
                        "data_version": None,
                        "read_only": None,
                        "rule_info": {},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-64.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Linux_x86-gcc3.locales.en-US",
                                "data_version": 1,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    }
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(side_effect=[True, False, True])
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 3
    # One less here, because the final call is skipped after time_is_ready return False
    assert verify_signoffs.call_count == 2
    # Once for each v1 endpoint, once for each v2 endpoint
    assert fr.call_count == 8
    called_endpoints = [call[0][1] for call in fr.call_args_list]
    assert "/v2/releases/Firefox-64.0-build1/enact" not in called_endpoints


@pytest.mark.asyncio
async def test_v2_releases_multiple_changes_one_release_one_part_not_ready(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {
                        "name": "Firefox-64.0-build1",
                        "product": None,
                        "data_version": None,
                        "read_only": None,
                        "rule_info": {},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-64.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Linux_x86-gcc3.locales.en-US",
                                "data_version": 1,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    },
                    {
                        "name": "Firefox-66.0-build1",
                        "product": "Firefox",
                        "data_version": 1,
                        "read_only": False,
                        "rule_info": {"3": {"product": "Firefox", "channel": "release"}},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-66.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "update",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                            {
                                "name": "Firefox-66.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 6,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "update",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {"bill": "releng"},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    },
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(side_effect=[True, True, True, True, False])
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 5
    # One less here, because the final call is skipped after time_is_ready return False
    assert verify_signoffs.call_count == 4
    # Once for each v1 endpoint, once for each v2 endpoint, once to enact the one release that was ready
    assert fr.call_count == 9
    called_endpoints = [call[0][1] for call in fr.call_args_list]
    assert "/v2/releases/Firefox-64.0-build1/enact" in called_endpoints
    assert "/v2/releases/Firefox-66.0-build1/enact" not in called_endpoints


@pytest.mark.asyncio
async def test_v2_releases_signoff_requirements_not_met(monkeypatch, fake_request):
    fr = fake_request(
        {
            "v2/releases": {
                "releases": [
                    {
                        "name": "Firefox-64.0-build1",
                        "product": None,
                        "data_version": None,
                        "read_only": None,
                        "rule_info": {},
                        "scheduled_changes": [
                            {
                                "name": "Firefox-64.0-build1",
                                "product": "Firefox",
                                "data_version": 1,
                                "read_only": False,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Darwin_x86_64-gcc3-u-i386-x86_64.locales.en-US",
                                "data_version": 1,
                                "sc_id": 1,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {},
                            },
                            {
                                "name": "Firefox-64.0-build1",
                                "path": ".platforms.Linux_x86-gcc3.locales.en-US",
                                "data_version": 1,
                                "sc_id": 2,
                                "scheduled_by": "bob",
                                "when": 2222222222000,
                                "change_type": "insert",
                                "sc_data_version": 1,
                                "complete": False,
                                "signoffs": {},
                            },
                        ],
                        "product_required_signoffs": {"releng": 1},
                        "required_signoffs": {"releng": 1},
                    }
                ]
            }
        }
    )
    monkeypatch.setattr(balrogagent.cmd.client, "request", fr)
    time_is_ready = MagicMock(return_value=True)
    monkeypatch.setattr(balrogagent.cmd, "time_is_ready", time_is_ready)
    verify_signoffs = MagicMock(return_value=False)
    monkeypatch.setattr(balrogagent.cmd, "verify_signoffs", verify_signoffs)
    await balrogagent.cmd.run_agent(asyncio.get_event_loop(), "http://balrog.fake", "telemetry", auth0_secrets={}, once=True, raise_exceptions=True)

    # Once per scheduled change
    assert time_is_ready.call_count == 3
    assert verify_signoffs.call_count == 3
    # Once for each v1 endpoint, once for each v2 endpoint
    assert fr.call_count == 8
