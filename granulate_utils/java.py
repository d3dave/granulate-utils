import re
from typing import Iterable, List

NATIVE_FRAMES_REGEX = re.compile(r"^Native frames:[^\n]*\n(.*?)\n\n", re.MULTILINE | re.DOTALL)
"""
See VMError::print_native_stack.
Example:
    Native frames: (J=compiled Java code, j=interpreted, Vv=VM code, C=native code)
    C  [libc.so.6+0x18e4e1]
    C  [libasyncProfiler.so+0x1bb4e]  Profiler::dump(std::ostream&, Arguments&)+0xce
    C  [libasyncProfiler.so+0x1bcae]  Profiler::runInternal(Arguments&, std::ostream&)+0x9e
    C  [libasyncProfiler.so+0x1c242]  Profiler::run(Arguments&)+0x212
    C  [libasyncProfiler.so+0x48d81]  Agent_OnAttach+0x1e1
    V  [libjvm.so+0x7ea65b]
    V  [libjvm.so+0x2f5e62]
    V  [libjvm.so+0xb08d2f]
    V  [libjvm.so+0xb0a0fa]
    V  [libjvm.so+0x990552]
    C  [libpthread.so.0+0x76db]  start_thread+0xdb
"""

SIGINFO_REGEX = re.compile(r"^siginfo: ([^\n]*)", re.MULTILINE | re.DOTALL)
"""
See os::print_siginfo
Example:
    siginfo: si_signo: 11 (SIGSEGV), si_code: 0 (SI_USER), si_pid: 537787, si_uid: 0
"""

CONTAINER_INFO_REGEX = re.compile(r"^container \(cgroup\) information:\n(.*?)\n\n", re.MULTILINE | re.DOTALL)
"""
See os::Linux::print_container_info
Example:
    container (cgroup) information:
    container_type: cgroupv1
    cpu_cpuset_cpus: 0-15
    cpu_memory_nodes: 0
    active_processor_count: 16
    cpu_quota: -1
    cpu_period: 100000
    cpu_shares: -1
    memory_limit_in_bytes: -1
    memory_and_swap_limit_in_bytes: -2
    memory_soft_limit_in_bytes: -1
    memory_usage_in_bytes: 26905034752
    memory_max_usage_in_bytes: 27891224576
"""

VM_INFO_REGEX = re.compile(r"^vm_info: ([^\n]*)", re.MULTILINE | re.DOTALL)
"""
This is the last line printed in VMError::report.
Example:
    vm_info: OpenJDK 64-Bit Server VM (25.292-b10) for linux-amd64 JRE (1.8.0_292-8u292-b10-0ubuntu1~18.04-b10), ...
"""


def locate_hotspot_error_file(nspid: int, cmdline: List[str]) -> Iterable[str]:
    """
    Locate a fatal error log written by the Hotspot JVM, if one exists.
    See https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/felog001.html.

    :return: Candidate paths (relative to process working directory) ordered by dominance.
    """
    for arg in cmdline:
        if arg.startswith("-XX:ErrorFile="):
            _, error_file = arg.split("=", maxsplit=1)
            yield error_file.replace("%p", str(nspid))
            break
    default_error_file = f"hs_err_pid{nspid}.log"
    yield default_error_file
    yield f"/tmp/{default_error_file}"