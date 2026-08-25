import os
import subprocess

from amaranth.build import *
from amaranth.vendor import GowinPlatform

from .resources import *

__all__ = ["TangPrimer25kPlatform", "TangPrimer25kDockPlatform"]

# Specification: https://api.dl.sipeed.com/file/download?verify_code=6xhl&file_url=TANG/Primer_25K/01_Specification/Tang_Primer_25K_Specification_V1.0_en.pdf
# Board schematic: https://dl.sipeed.com/fileList/TANG/Primer_25K/02_Schematic/Tang_Primer_25K_Dock_60033_Schematic.pdf


class TangPrimer25kPlatform(GowinPlatform):
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
    ]
    connectors = [
        Connector(
            "J1",
            0,
            # GND                         GND
            " -   L9  K9  J8  K8  F7  F6  -   E8  B3 "
            #             GND
            " C3  E3  D7  -   -   -   J11 J10 H11 H10"
            #         GND                         GND
            " G11 G10 -   D11 D10 C11 C10 B11 B10 -",
        ),
        Connector(
            "J1",
            1,
            # GND
            " -   H5  J5  L5  K5  H8  H7  G7  G8  F5 "
            #             GND
            " G5  -   -   -   L6  K6  K7  J7  L7  L8 "
            #                 GND                 GND
            " L10 K10 K11 L11 -   E11 E10 A11 A10 -",
        ),
        Connector(
            "J2",
            0,
            # GND                                 GND
            " -   B2  C2  F2  F1  A1  DB  E1  D1  - "
            #                 GND         GND
            " C1  B1  A2  A3  -   -   -   -   -   -"
            # GND         GND         GND         GND
            " -   -   -   -   -   -   -   -   -   -",
        ),
        Connector(
            "J2",
            1,
            # GND GND GND GND GND GND
            " -   -   L2  L1  K1  K2  J4  K4  G2  G1"
            #                                 1V8 1V8
            " L4  L3  J1  J2  G4  H4  H1  H2  -   -"
            # 2V5 2V5 3V3 3V3 3V3 5V  5V  5V  5V  5V
            " -   -   -   -   -   -   -   -   -   -",
        ),
    ]


class TangPrimer25kDockPlatform(TangPrimer25kPlatform):
    resources = TangPrimer25kPlatform.resources + [
        *ButtonResources(pins={0: "H10"}, invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
        *ButtonResources(pins={1: "H11"}, invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
        *LEDResources(pins="E8 D7", invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
    ]
    connectors = [
        #                     3V3 3V3 GND GND
        Connector("pmod", 0, "-   -   -   -   C11 C10 B11 B10 D11 D10 G11 G10"),
        Connector("pmod", 1, "-   -   -   -   L5  K5  K11 L11 E11 E10 A11 A10 "),
        Connector("pmod", 2, "-   -   -   -   H5  J5  H8  H7  G7  G8  F5  G5"),
        Connector(
            "gpio",
            0,
            " K2  K1  L1  L2  K4  J4  G1  G2  L3  L4"  #   ( 1 - 10)
            # 5V  GND -   -   -   -   -   -   -   -        (11 - 20)
            " -   -   C2  B2  F1  F2  A1  E1  D1  E3"
            " J2  J1  H4  G4  H2  H1  J7  K7  L8  L7"  #   (21 - 30)
            " K10 L10 K9  L9  K8  J8  F6  F7  J10 J11",  # (31 - 40)
        ),
    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "nextpnr_opts": "--vopt sspi_as_gpio",
            "gowin_pack_opts": "--sspi_as_gpio --mspi_as_gpio --ready_as_gpio --done_as_gpio --cpu_as_gpio",
        }

        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, products, name):
        with products.extract("{}.fs".format(name)) as bitstream_filename:
            subprocess.check_call(
                ["openFPGALoader", "-b", "tangprimer25k", "-m", bitstream_filename]
            )


if __name__ == "__main__":
    from .test.blinky import *

    TangPrimer25kDockPlatform().build(Blinky(), do_program=True)
