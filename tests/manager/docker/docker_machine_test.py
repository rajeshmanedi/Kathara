import sys
from unittest import mock
from unittest.mock import Mock

import pytest

sys.path.insert(0, './')

from src.Kathara.model.Lab import Lab
from src.Kathara.model.Link import Link
from src.Kathara.model.Machine import Machine
from src.Kathara.manager.docker.DockerMachine import DockerMachine
from src.Kathara.exceptions import MachineNotFoundError, DockerPluginError, MachineBinaryError


#
# FIXTURE
#
@pytest.fixture()
@mock.patch("src.Kathara.manager.docker.DockerImage.DockerImage")
@mock.patch("docker.DockerClient")
def docker_machine(mock_docker_client, mock_docker_image):
    return DockerMachine(mock_docker_client, mock_docker_image)


@pytest.fixture()
@mock.patch("docker.models.containers.Container")
def default_device(mock_docker_container):
    device = Machine(Lab('Default scenario'), "test_device")
    device.add_meta("exec", "ls")
    device.add_meta("mem", "64m")
    device.add_meta("cpus", "2")
    device.add_meta("image", "kathara/test")
    device.add_meta("bridged", False)
    device.api_object = mock_docker_container
    device.api_object.id = "device_id"
    device.api_object.attrs = {"NetworkSettings": {"Networks": []}}
    device.api_object.labels = {"user": "user", "name": "test_device", "lab_hash": "lab_hash", "shell": "/bin/bash"}
    return device


@pytest.fixture()
def default_link(default_device):
    link = Link(default_device.lab, "A")
    link.api_object = Mock()
    link.api_object.connect = Mock(return_value=True)
    return link


@pytest.fixture()
def default_link_b(default_device):
    link = Link(default_device.lab, "B")
    link.api_object = Mock()
    link.api_object.connect = Mock(return_value=True)
    return link


#
# TEST: create
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.copy_files")
@mock.patch("src.Kathara.setting.Setting.Setting.get_instance")
@mock.patch("src.Kathara.utils.get_current_user_name")
def test_create(mock_get_current_user_name, mock_setting_get_instance, mock_copy_files,
                mock_get_machines_api_objects_by_filters, docker_machine, default_device):
    mock_get_machines_api_objects_by_filters.return_value = []
    mock_get_current_user_name.return_value = "test-user"

    setting_mock = Mock()
    setting_mock.configure_mock(**{
        'shared_cd': False,
        'device_prefix': 'dev_prefix',
        "device_shell": '/bin/bash',
        'enable_ipv6': False,
        'remote_url': None,
        'hosthome_mount': False,
        'shared_mount': False
    })
    mock_setting_get_instance.return_value = setting_mock
    docker_machine.create(default_device)
    docker_machine.client.containers.create.assert_called_once_with(
        image='kathara/test',
        name='dev_prefix_test-user_test_device_9pe3y6IDMwx4PfOPu5mbNg',
        hostname='test_device',
        cap_add=['NET_ADMIN', 'NET_RAW', 'NET_BROADCAST', 'NET_BIND_SERVICE', 'SYS_ADMIN'],
        privileged=False,
        network=None,
        network_mode='none',
        sysctls={'net.ipv4.conf.all.rp_filter': 0,
                 'net.ipv4.conf.default.rp_filter': 0,
                 'net.ipv4.conf.lo.rp_filter': 0,
                 'net.ipv4.ip_forward': 1,
                 'net.ipv4.icmp_ratelimit': 0
                 },
        environment={},
        mem_limit='64m',
        nano_cpus=2000000000,
        ports=None,
        tty=True,
        stdin_open=True,
        detach=True,
        volumes={},
        labels={'name': 'test_device', 'lab_hash': '9pe3y6IDMwx4PfOPu5mbNg', 'user': 'test-user', 'app': 'kathara',
                'shell': '/bin/bash'}
    )

    assert not mock_copy_files.called


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.copy_files")
@mock.patch("src.Kathara.setting.Setting.Setting.get_instance")
@mock.patch("src.Kathara.utils.get_current_user_name")
def test_create_ipv6(mock_get_current_user_name, mock_setting_get_instance, mock_copy_files,
                     mock_get_machines_api_objects_by_filters, docker_machine, default_device):
    mock_get_machines_api_objects_by_filters.return_value = []
    mock_get_current_user_name.return_value = "test-user"

    setting_mock = Mock()
    setting_mock.configure_mock(**{
        'shared_cd': False,
        'device_prefix': 'dev_prefix',
        "device_shell": '/bin/bash',
        'enable_ipv6': True,
        'remote_url': None,
        'hosthome_mount': False,
        'shared_mount': False
    })
    mock_setting_get_instance.return_value = setting_mock
    docker_machine.create(default_device)
    docker_machine.client.containers.create.assert_called_once_with(
        image='kathara/test',
        name='dev_prefix_test-user_test_device_9pe3y6IDMwx4PfOPu5mbNg',
        hostname='test_device',
        cap_add=['NET_ADMIN', 'NET_RAW', 'NET_BROADCAST', 'NET_BIND_SERVICE', 'SYS_ADMIN'],
        privileged=False,
        network=None,
        network_mode='none',
        sysctls={'net.ipv4.conf.all.rp_filter': 0,
                 'net.ipv4.conf.default.rp_filter': 0,
                 'net.ipv4.conf.lo.rp_filter': 0,
                 'net.ipv4.ip_forward': 1,
                 'net.ipv4.icmp_ratelimit': 0,
                 'net.ipv6.conf.all.forwarding': 1,
                 'net.ipv6.icmp.ratelimit': 0,
                 'net.ipv6.conf.default.disable_ipv6': 0,
                 'net.ipv6.conf.all.disable_ipv6': 0
                 },
        environment={},
        mem_limit='64m',
        nano_cpus=2000000000,
        ports=None,
        tty=True,
        stdin_open=True,
        detach=True,
        volumes={},
        labels={'name': 'test_device', 'lab_hash': '9pe3y6IDMwx4PfOPu5mbNg', 'user': 'test-user', 'app': 'kathara',
                'shell': '/bin/bash'}
    )

    assert not mock_copy_files.called


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.copy_files")
@mock.patch("src.Kathara.setting.Setting.Setting.get_instance")
@mock.patch("src.Kathara.utils.get_current_user_name")
def test_create_privileged(mock_get_current_user_name, mock_setting_get_instance, mock_copy_files,
                           mock_get_machines_api_objects_by_filters, docker_machine, default_device):
    mock_get_machines_api_objects_by_filters.return_value = []

    default_device.lab.add_option("privileged_machines", True)
    mock_get_current_user_name.return_value = "test-user"
    setting_mock = Mock()
    setting_mock.configure_mock(**{
        'shared_cd': False,
        'device_prefix': 'dev_prefix',
        "device_shell": '/bin/bash',
        "hosthome_mount": False,
        "shared_mount": False,
        'remote_url': None
    })
    mock_setting_get_instance.return_value = setting_mock
    docker_machine.create(default_device)
    docker_machine.client.containers.create.assert_called_once_with(
        image='kathara/test',
        name='dev_prefix_test-user_test_device_9pe3y6IDMwx4PfOPu5mbNg',
        hostname='test_device',
        cap_add=None,
        privileged=True,
        network=None,
        network_mode='none',
        sysctls={'net.ipv4.conf.all.rp_filter': 0,
                 'net.ipv4.conf.default.rp_filter': 0,
                 'net.ipv4.conf.lo.rp_filter': 0,
                 'net.ipv4.ip_forward': 1,
                 'net.ipv4.icmp_ratelimit': 0,
                 'net.ipv6.conf.all.forwarding': 1,
                 'net.ipv6.icmp.ratelimit': 0,
                 'net.ipv6.conf.default.disable_ipv6': 0,
                 'net.ipv6.conf.all.disable_ipv6': 0},
        environment={},
        mem_limit='64m',
        nano_cpus=2000000000,
        ports=None,
        tty=True,
        stdin_open=True,
        detach=True,
        volumes={},
        labels={'name': 'test_device', 'lab_hash': '9pe3y6IDMwx4PfOPu5mbNg', 'user': 'test-user', 'app': 'kathara',
                'shell': '/bin/bash'}
    )
    assert not mock_copy_files.called


#
# TEST: start
#
def test_start(docker_machine, default_device, default_link, default_link_b):
    # add two interfaces because interace 0 is excluded
    default_device.add_interface(default_link)
    default_device.add_interface(default_link_b)
    default_device.add_meta("num_terms", 3)
    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = ("cmd_stdout", "cmd_stderr")
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 0}
    default_device.api_object.start.return_value = True

    docker_machine.start(default_device)

    default_device.api_object.start.assert_called_once()
    docker_machine.client.api.exec_create.assert_called_once()
    docker_machine.client.api.exec_start.assert_called_once()
    docker_machine.client.api.exec_inspect.assert_called_once()
    default_link_b.api_object.connect.assert_called_once()


def test_start_plugin_error_endpoint_start(default_device, docker_machine):
    default_device.api_object.start.side_effect = DockerPluginError("endpoint does not exists")
    with pytest.raises(DockerPluginError):
        docker_machine.start(default_device)


def test_start_plugin_error_network_start(default_device, docker_machine):
    default_device.api_object.start.side_effect = DockerPluginError("network does not exists")
    with pytest.raises(DockerPluginError):
        docker_machine.start(default_device)


def test_start_plugin_error_endpoint_connect(default_device, default_link, default_link_b, docker_machine):
    default_device.add_interface(default_link)
    default_device.add_interface(default_link_b)
    default_link_b.api_object.connect.side_effect = DockerPluginError("endpoint does not exists")
    with pytest.raises(DockerPluginError):
        docker_machine.start(default_device)


def test_start_plugin_error_network_connect(default_device, default_link, default_link_b, docker_machine):
    default_device.add_interface(default_link)
    default_device.add_interface(default_link_b)
    default_link_b.api_object.connect.side_effect = DockerPluginError("network does not exists")
    with pytest.raises(DockerPluginError):
        docker_machine.start(default_device)


#
# TEST: _deploy_and_start_machine
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.start")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.create")
def test_deploy_and_start_machine(mock_create, mock_start, docker_machine, default_device):
    machine_item = ("", default_device)
    mock_create.return_value = True
    mock_start.return_value = True
    docker_machine._deploy_and_start_machine(machine_item)
    mock_create.assert_called_once()
    mock_start.assert_called_once()


#
# TEST: deploy_machines
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._deploy_and_start_machine")
def test_deploy_machines(mock_deploy_and_start, docker_machine):
    lab = Lab("Default scenario")
    lab.get_or_new_machine("pc1", **{'image': 'kathara/test1'})
    lab.get_or_new_machine("pc2", **{'image': 'kathara/test2'})
    docker_machine.docker_image.check_from_list.return_value = None
    mock_deploy_and_start.return_value = None
    docker_machine.deploy_machines(lab)
    docker_machine.docker_image.check_from_list.assert_called_once_with({'kathara/test1', 'kathara/test2'})
    assert mock_deploy_and_start.call_count == 2


#
# TEST: connect_to_link
#
def test_connect_to_link(docker_machine, default_device, default_link, default_link_b):
    default_device.api_object.attrs["NetworkSettings"] = {}
    default_device.api_object.attrs["NetworkSettings"]["Networks"] = ["A"]
    default_link.api_object.name = "A"

    default_device.add_interface(default_link)
    default_device.add_interface(default_link_b)

    docker_machine.connect_to_link(default_device, default_link_b)

    assert not default_link.api_object.connect.called
    default_link_b.api_object.connect.assert_called_once()


def test_connect_to_link_plugin_error_network(default_device, default_link, docker_machine):
    default_device.add_interface(default_link)
    default_link.api_object.connect.side_effect = DockerPluginError("network does not exists")
    with pytest.raises(DockerPluginError):
        docker_machine.connect_to_link(default_device, default_link)


def test_connect_to_link_plugin_error_endpoint(default_device, default_link, docker_machine):
    default_device.add_interface(default_link)
    default_link.api_object.connect.side_effect = DockerPluginError("endpoint does not exists")
    with pytest.raises(DockerPluginError):
        docker_machine.connect_to_link(default_device, default_link)


#
# TEST: disconnect_from_link
#
def test_disconnect_from_link(docker_machine, default_device, default_link, default_link_b):
    default_device.api_object.attrs["NetworkSettings"] = {}
    default_device.api_object.attrs["NetworkSettings"]["Networks"] = ["A", "B"]
    default_link.api_object.name = "A"
    default_link_b.api_object.name = "B"
    default_device.add_interface(default_link)
    default_device.add_interface(default_link_b)

    docker_machine.disconnect_from_link(default_device, default_link_b)

    assert not default_link.api_object.disconnect.called
    default_link_b.api_object.disconnect.assert_called_once()


#
# TEST: undeploy
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._undeploy_machine")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_undeploy_one_device(mock_get_machines_api_objects_by_filters, mock_undeploy_machine, docker_machine,
                             default_device):
    default_device.api_object.labels = {'name': "test_device"}
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object]
    mock_undeploy_machine.return_value = None
    docker_machine.undeploy("lab_hash", selected_machines={default_device.name})
    mock_get_machines_api_objects_by_filters.assert_called_once()
    mock_undeploy_machine.assert_called_once_with(default_device.api_object)


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._undeploy_machine")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_undeploy_three_devices(mock_get_machines_api_objects_by_filters, mock_undeploy_machine, docker_machine,
                                default_device):
    default_device.api_object.labels = {'name': "test_device"}
    # fill the list with more devices
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object,
                                                             default_device.api_object, default_device.api_object]
    mock_undeploy_machine.return_value = None
    docker_machine.undeploy("lab_hash")
    mock_get_machines_api_objects_by_filters.assert_called_once()
    assert mock_undeploy_machine.call_count == 3


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._undeploy_machine")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_undeploy_no_devices(mock_get_machines_api_objects_by_filters, mock_undeploy_machine, docker_machine):
    mock_get_machines_api_objects_by_filters.return_value = []
    mock_undeploy_machine.return_value = None
    docker_machine.undeploy("lab_hash")
    mock_get_machines_api_objects_by_filters.assert_called_once()
    assert not mock_undeploy_machine.called


#
# TEST: wipe
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._undeploy_machine")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_wipe_one_device(mock_get_machines_api_objects_by_filters, mock_undeploy_machine, docker_machine,
                         default_device):
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object]
    mock_undeploy_machine.return_value = None
    docker_machine.wipe()
    mock_undeploy_machine.assert_called_once()


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._undeploy_machine")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_wipe_no_devices(mock_get_machines_api_objects_by_filters, mock_undeploy_machine, docker_machine):
    mock_get_machines_api_objects_by_filters.return_value = []
    mock_undeploy_machine.return_value = None
    docker_machine.wipe()
    assert not mock_undeploy_machine.called


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._undeploy_machine")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_wipe_three_devices(mock_get_machines_api_objects_by_filters, mock_undeploy_machine, docker_machine,
                            default_device):
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object, default_device.api_object,
                                                             default_device.api_object]
    mock_undeploy_machine.return_value = None
    docker_machine.wipe()
    assert mock_undeploy_machine.call_count == 3


#
# TEST: _undeploy_machine
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine._delete_machine")
def test_undeploy_machine(mock_delete_machine, docker_machine, default_device):
    mock_delete_machine.return_value = None
    docker_machine._undeploy_machine(default_device.api_object)
    mock_delete_machine.assert_called_once()


#
# TEST: exec
#
@mock.patch("src.Kathara.setting.Setting.Setting.get_instance")
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_exec(mock_get_machines_api_objects_by_filters, mock_setting_get_instance, docker_machine, default_device):
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object]

    setting_mock = Mock()
    setting_mock.configure_mock(**{
        'shared_cd': False,
        'device_prefix': 'dev_prefix',
        "device_shell": '/bin/bash',
        'enable_ipv6': False,
        'remote_url': None,
        'hosthome_mount': False,
        'shared_mount': False
    })
    mock_setting_get_instance.return_value = setting_mock

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = iter([("cmd_stdout", "cmd_stderr")])
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 0}
    result = docker_machine.exec(default_device.lab.hash, "test_device", "kathara --help", tty=False)
    output = next(result)

    assert output == ('cmd_stdout', 'cmd_stderr')


#
# TEST: _exec_run
#
def test_exec_run_demux(docker_machine, default_device):
    output_iter = ("cmd_stdout", "cmd_stderr")

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_iter
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 0}
    result = docker_machine._exec_run(
        default_device.api_object,
        "kathara --help",
        demux=True
    )

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "kathara --help", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=True
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")
    assert result == {'exit_code': 0, 'output': output_iter}


def test_exec_run_demux_stream(docker_machine, default_device):
    output_gen = map(lambda x: x, [("cmd_stdout", "cmd_stderr")])

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_gen
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": None}
    result = docker_machine._exec_run(
        default_device.api_object,
        "kathara --help",
        stream=True,
        demux=True
    )

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "kathara --help", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=True, socket=False, demux=True
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")
    assert result == {'exit_code': None, 'output': output_gen}


def test_exec_run_oci_runtime_error_1_no_demux(docker_machine, default_device):
    output_str = b"OCI runtime exec failed: exec failed: unable to start container process: exec: \"exe\": " \
                 b"executable file not found in $PATH: unknown"

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_str
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 126}

    with pytest.raises(MachineBinaryError) as e:
        docker_machine._exec_run(
            default_device.api_object,
            "exe",
        )

        assert e.binary == "exe"

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "exe", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=False
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")


def test_exec_run_oci_runtime_error_1_demux(docker_machine, default_device):
    output_str = (b"OCI runtime exec failed: exec failed: unable to start container process: exec: \"exe\": "
                  b"executable file not found in $PATH: unknown", b"")

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_str
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 126}

    with pytest.raises(MachineBinaryError) as e:
        docker_machine._exec_run(
            default_device.api_object,
            "exe",
            demux=True
        )

        assert e.binary == "exe"

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "exe", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=True
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")


def test_exec_run_oci_runtime_error_1_stream(docker_machine, default_device):
    output_gen = map(lambda x: x, [b"OCI runtime exec failed: exec failed: unable to start container process: "
                                   b"exec: \"exe\": executable file not found in $PATH: unknown"])

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_gen
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": None}

    result = docker_machine._exec_run(
        default_device.api_object,
        "exe",
        demux=True
    )

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "exe", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=True
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")
    assert result == {'exit_code': None, 'output': output_gen}


def test_exec_run_oci_runtime_error_2_no_demux(docker_machine, default_device):
    output_str = b"OCI runtime exec failed: exec failed: unable to start container process: exec: \"exe1\": " \
                 b"stat exe1: no such file or directory: unknown"

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_str
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 126}

    with pytest.raises(MachineBinaryError) as e:
        docker_machine._exec_run(
            default_device.api_object,
            "exe1",
        )

        assert e.binary == "exe1"

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "exe1", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=False
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")


def test_exec_run_oci_runtime_error_2_demux(docker_machine, default_device):
    output_str = (b"OCI runtime exec failed: exec failed: unable to start container process: exec: \"exe1\": " \
                  b"stat exe1: no such file or directory: unknown", b"")

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_str
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 126}

    with pytest.raises(MachineBinaryError) as e:
        docker_machine._exec_run(
            default_device.api_object,
            "exe1",
            demux=True
        )

        assert e.binary == "exe1"

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "exe1", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=True
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")


def test_exec_run_oci_runtime_error_2_stream(docker_machine, default_device):
    output_gen = map(lambda x: x, [b"OCI runtime exec failed: exec failed: unable to start container process: "
                                   b"exec: \"exe1\": stat exe1: no such file or directory: unknown"])

    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = output_gen
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": None}

    result = docker_machine._exec_run(
        default_device.api_object,
        "exe1",
        demux=True
    )

    docker_machine.client.api.exec_create.assert_called_once_with(
        default_device.api_object.id, "exe1", stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='', environment=None, workdir=None
    )
    docker_machine.client.api.exec_start.assert_called_once_with(
        "1234", detach=False, tty=False, stream=False, socket=False, demux=True
    )
    docker_machine.client.api.exec_inspect.assert_called_once_with("1234")
    assert result == {'exit_code': None, 'output': output_gen}


#
# TEST: get_machines_api_objects
#
def test_get_machines_api_objects_by_filters(docker_machine):
    docker_machine.client.containers.list.return_value = ["test_device"]
    docker_machine.get_machines_api_objects_by_filters("lab_hash_value", "test_device", "user_name_value")
    filters = {"label": ["app=kathara", "user=user_name_value", "lab_hash=lab_hash_value", "name=test_device"]}
    docker_machine.client.containers.list.assert_called_once_with(all=True, filters=filters)


def test_get_machines_api_objects_by_filters_empty_filters(docker_machine):
    docker_machine.client.containers.list.return_value = None
    docker_machine.get_machines_api_objects_by_filters()
    filters = {"label": ["app=kathara"]}
    docker_machine.client.containers.list.assert_called_once_with(all=True, filters=filters)


def test_get_machines_api_objects_by_filters_lab_hash_filter(docker_machine):
    docker_machine.client.containers.list.return_value = None
    docker_machine.get_machines_api_objects_by_filters("lab_hash_value", None, None)
    filters = {"label": ["app=kathara", "lab_hash=lab_hash_value"]}
    docker_machine.client.containers.list.assert_called_once_with(all=True, filters=filters)


def test_get_machines_api_objects_by_filters_lab_device_name_filter(docker_machine):
    docker_machine.client.containers.list.return_value = ["test_device"]
    docker_machine.get_machines_api_objects_by_filters(None, "test_device", None)
    filters = {"label": ["app=kathara", "name=test_device"]}
    docker_machine.client.containers.list.assert_called_once_with(all=True, filters=filters)


def test_get_machines_api_objects_by_filters_user_filter(docker_machine):
    docker_machine.client.containers.list.return_value = None
    docker_machine.get_machines_api_objects_by_filters(None, None, "user_name_value")
    filters = {"label": ["app=kathara", "user=user_name_value"]}
    docker_machine.client.containers.list.assert_called_once_with(all=True, filters=filters)


#
# TEST: get_container_name
#
@mock.patch("src.Kathara.setting.Setting.Setting.get_instance")
@mock.patch("src.Kathara.utils.get_current_user_name")
def test_get_container_name_lab_hash(mock_get_current_user_name, mock_setting_get_instance):
    mock_get_current_user_name.return_value = "kathara-user"

    setting_mock = Mock()
    setting_mock.configure_mock(**{
        'shared_cd': False,
        'device_prefix': 'dev_prefix'
    })
    mock_setting_get_instance.return_value = setting_mock

    assert "dev_prefix_kathara-user_test_device_lab_hash" == DockerMachine.get_container_name("test_device", "lab_hash")


@mock.patch("src.Kathara.setting.Setting.Setting.get_instance")
@mock.patch("src.Kathara.utils.get_current_user_name")
def test_get_container_name_lab_hash_shared_cd(mock_get_current_user_name, mock_setting_get_instance):
    mock_get_current_user_name.return_value = "kathara-user"

    setting_mock = Mock()
    setting_mock.configure_mock(**{
        'shared_cd': True,
        'device_prefix': 'dev_prefix'
    })
    mock_setting_get_instance.return_value = setting_mock


#
# TEST: delete_machine
#
def test_delete_machine_running(docker_machine, default_device):
    docker_machine.client.api.exec_create.return_value = {"Id": "1234"}
    docker_machine.client.api.exec_start.return_value = ("cmd_stdout", "cmd_stderr")
    docker_machine.client.api.exec_inspect.return_value = {"ExitCode": 0}
    default_device.api_object.remove.return_value = None
    default_device.api_object.status = "running"

    docker_machine._delete_machine(default_device.api_object)
    docker_machine.client.api.exec_create.assert_called_once()
    docker_machine.client.api.exec_start.assert_called_once()
    docker_machine.client.api.exec_inspect.assert_called_once()
    default_device.api_object.remove.assert_called_once_with(force=True)


def test_delete_machine_not_running(docker_machine, default_device):
    default_device.api_object.exec_run.return_value = None
    default_device.api_object.remove.return_value = None
    default_device.api_object.status = "stop"

    docker_machine._delete_machine(default_device.api_object)
    assert not default_device.api_object.exec_run.called
    default_device.api_object.remove.assert_called_once_with(force=True)


#
# TEST: get_machines_stats
#
@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_get_machines_stats_lab_hash(mock_get_machines_api_objects_by_filters, docker_machine, default_device):
    default_device.api_object.name = "test_device"
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object]
    default_device.api_object.stats.return_value = iter([{'pids_stats': {}, 'cpu_stats': {}, 'memory_stats': {}}])
    next(docker_machine.get_machines_stats(lab_hash="lab_hash"))

    mock_get_machines_api_objects_by_filters.assert_called_once_with(lab_hash="lab_hash", machine_name=None, user=None)
    default_device.api_object.stats.assert_called_once()


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_get_machines_stats_lab_hash_device_name(mock_get_machines_api_objects_by_filters, docker_machine,
                                                 default_device):
    default_device.api_object.name = "test_device"
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object]
    default_device.api_object.stats.return_value = iter([{'pids_stats': {}, 'cpu_stats': {}, 'memory_stats': {}}])
    next(docker_machine.get_machines_stats(lab_hash="lab_hash", machine_name="test_device", user="user"))

    mock_get_machines_api_objects_by_filters.assert_called_once_with(lab_hash="lab_hash", machine_name="test_device",
                                                                     user="user")
    default_device.api_object.stats.assert_called_once()


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_get_machines_stats_lab_hash_device_name_user(mock_get_machines_api_objects_by_filters, docker_machine,
                                                      default_device):
    default_device.api_object.name = "test_device"
    mock_get_machines_api_objects_by_filters.return_value = [default_device.api_object]
    default_device.api_object.stats.return_value = iter([{'pids_stats': {}, 'cpu_stats': {}, 'memory_stats': {}}])
    next(docker_machine.get_machines_stats(lab_hash="lab_hash", machine_name="test_device"))

    mock_get_machines_api_objects_by_filters.assert_called_once_with(lab_hash="lab_hash", machine_name="test_device",
                                                                     user=None)
    default_device.api_object.stats.assert_called_once()


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_get_machines_stats_lab_hash_device_not_found(mock_get_machines_api_objects_by_filters, docker_machine,
                                                      default_device):
    mock_get_machines_api_objects_by_filters.return_value = []
    with pytest.raises(MachineNotFoundError):
        next(docker_machine.get_machines_stats(lab_hash="lab_hash"))

    mock_get_machines_api_objects_by_filters.assert_called_once_with(lab_hash="lab_hash", machine_name=None,
                                                                     user=None)
    assert not default_device.api_object.stats.called


@mock.patch("src.Kathara.manager.docker.DockerMachine.DockerMachine.get_machines_api_objects_by_filters")
def test_get_machines_stats_lab_hash_and_name_device_not_found(mock_get_machines_api_objects_by_filters, docker_machine,
                                                               default_device):
    mock_get_machines_api_objects_by_filters.return_value = []
    with pytest.raises(MachineNotFoundError):
        next(docker_machine.get_machines_stats(lab_hash="lab_hash", machine_name="test_device"))

    mock_get_machines_api_objects_by_filters.assert_called_once_with(lab_hash="lab_hash", machine_name="test_device",
                                                                     user=None)
    assert not default_device.api_object.stats.called
