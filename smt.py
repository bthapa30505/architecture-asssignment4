import m5
from m5.objects import *

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '2GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Configure an Out-of-Order CPU (O3CPU) with SMT
system.cpu = O3CPU()

# Enable SMT (Two Threads per Core)
system.cpu.numThreads = 2  
system.cpu.smt = True  

# Configure Superscalar Execution
system.cpu.fetchWidth = 4   # Fetch up to 4 instructions per cycle
system.cpu.decodeWidth = 4  # Decode up to 4 instructions per cycle
system.cpu.issueWidth = 4   # Issue up to 4 instructions per cycle
system.cpu.commitWidth = 4  # Commit up to 4 instructions per cycle
system.cpu.dispatchWidth = 4 # Dispatch width

# Branch Prediction (Important for SMT)
system.cpu.branchPred = TournamentBP()

# Cache and Memory System
system.membus = SystemXBar()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

# Memory Controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Assign Multiple Workloads (Two Threads for SMT)
binary1 = 'tests/test-progs/hello/bin/x86/linux/hello'
binary2 = 'tests/test-progs/hello/bin/x86/linux/hello'

process1 = Process()
process1.cmd = [binary1]

process2 = Process()
process2.cmd = [binary2]

# Assign Workloads to Different Threads
system.cpu.workload = [process1, process2]
system.cpu.createThreads()

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation with SMT enabled!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))
