# derived from amaranth.cli

from amaranth.hdl.ir import Fragment
from amaranth.back import rtlil, cxxrtl, verilog
from amaranth.sim import Simulator


def main_runner_by_sporniket(parser, args, design, platform=None, name="top", ports=(), prepareVerification=None, prepareSimulation=None):
    if args.action == "generate":
        if not prepareVerification is None:
            prepareVerification(design)
        fragment = Fragment.get(design, platform)
        generate_type = args.generate_type
        if generate_type is None and args.generate_file:
            if args.generate_file.name.endswith(".il"):
                generate_type = "il"
            if args.generate_file.name.endswith(".cc"):
                generate_type = "cc"
            if args.generate_file.name.endswith(".v"):
                generate_type = "v"
        if generate_type is None:
            parser.error("Unable to auto-detect language, specify explicitly with -t/--type")
        if generate_type == "il":
            output = rtlil.convert(fragment, name=name, ports=ports, emit_src=args.emit_src)
        if generate_type == "cc":
            output = cxxrtl.convert(fragment, name=name, ports=ports, emit_src=args.emit_src)
        if generate_type == "v":
            output = verilog.convert(fragment, name=name, ports=ports, emit_src=args.emit_src)
        if args.generate_file:
            args.generate_file.write(output)
        else:
            print(output)

    if args.action == "simulate":
        fragment = Fragment.get(design, platform)
        sim = Simulator(fragment)
        sim.add_clock(args.sync_period)
        if not prepareSimulation is None:
            prepareSimulation(sim, design)
        with sim.write_vcd(vcd_file=args.vcd_file, gtkw_file=args.gtkw_file, traces=ports):
            sim.run_until(args.sync_period * args.sync_clocks, run_passive=True)
