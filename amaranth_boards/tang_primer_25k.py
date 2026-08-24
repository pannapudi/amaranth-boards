import os
import subprocess

from amaranth.build import *
from amaranth.vendor import GowinPlatform

from .resources import *

__all__ = ["TangPrimer25kDockPlatform"]


class TangPrimer25kDockPlatform(GowinPlatform):
    part = "GW5A-LV25MG121NC1/I0"
    family = "GW5A-25A"
    default_clk = "clk27"
    resources = [
        Resource(
            "clk27", 0, Pins("E2", dir="i"), Clock(27e6), Attrs(IO_TYPE="LVCMOS33")
        ),
        UARTResource(
            0, rx="B3", tx="C3", attrs=Attrs(PULL_MODE="UP", IO_TYPE="LVCMOS33")
        ),
        *SPIFlashResources(
            0,
            cs_n="E6",
            clk="E7",
            cipo="D6",
            copi="E5",
            attrs=Attrs(IO_TYPE="LVCMOS33"),
        ),
        *ButtonResources(pins={0: "H10"}, invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
        *ButtonResources(pins={1: "H11"}, invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
        *LEDResources(pins="E8 D7", invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
    ]
    connectors = [
        #                     -   -   -   -   GRD 3V3 -   -   -   -   GND 3V3
        Connector("pmod", 0, "G11 D11 B11 C11 -   -   G10 D10 B10 C10 -   -"),
        Connector("pmod", 1, "A11 E11 K11 L5  -   -   A10 E10 L11 K5  -   -"),
        Connector("pmod", 2, "F5  G7  H8  H5  -   -   G5  G8  H7  J5  -   -"),
        Connector(
            "gpio",
            0,
            " K2  K1  L1  L2  K4  J4  G1  G2  L3  L4"  #   ( 0 - 10)
            # 5V  GND -   -   -   -   -   -   -   -        (11 - 20)
            " -   -   C2  B2  F1  F2  A1  E1  D1  E3"
            " J2  J1  H4  G4  H2  H1  J7  K7  L8  L7"  #   (21 - 30)
            " K10 L10 K9  L9  K8  J8  F6  F7  J10 J11",  # (31 - 40)
        ),
    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "nextpnr_opts": "--vopt sspi_as_gpio--vopt ready_as_gpio --vopt done_as_gpio",
            "gowin_pack_opts": "--sspi_as_gpio --ready_as_gpio --done_as_gpio",
        }

        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, products, name):
        with products.extract("{}.fs".format(name)) as bitstream_filename:
            subprocess.check_call(
                ["openFPGALoader", "-b", "tangprimer25k", bitstream_filename]
            )


if __name__ == "__main__":
    from .test.blinky import *

    TangPrimer25kDockPlatform().build(Blinky(), do_program=True)
