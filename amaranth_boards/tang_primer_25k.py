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
            0, rx="B3", tx="C3", attrs=Attrs(PULLMODE="UP", IO_TYPE="LVCMOS33")
        ),
        *SPIFlashResources(
            0,
            cs_n="E6",
            clk="E7",
            cipo="D6",
            copi="E5",
            attrs=Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP"),
        ),
    ]
    connectors = [
        Connector(
            "J1",
            0,
            {
                "S1": "-",  # GND
                "S2": "L9", "S3": "K9",
                "S4": "J8", "S5": "K8",
                "S6": "F7", "S7": "F6",
                "S8": "-",  # GND
                "S9": "E8", "S10": "B3",
                "S11": "C3", "S12": "E3",
                "S13": "D7", "S14": "-",  # GND
                "S15": "-", "S16": "-",  # VCCIO6/7 Input
                "S17": "J11", "S18": "D7",
                "S19": "J10", "S20": "H11",
                "S21": "H10", "S22": "G11",
                "S23": "G10", "S24": "-",  # GND
                "S25": "D11", "S26": "D10",
                "S27": "C11", "S28": "C10",
                "S29": "B11", "S30": "B10",
                "S31": "-",  # GND
            },
        ),
        Connector(
            "J1",
            1,
            {
                "S1": "-",  # GND
                "S2": "H5", "S3": "J5",
                "S4": "L5", "S5": "K5",
                "S6": "H8", "S7": "H7",
                "S8": "G7", "S9": "G8",
                "S10": "F5", "S11": "G5",
                "S12": "-", "S13": "-",  # VCCIO0/1
                "S14": "-",  # GND
                "S15": "L6", "S16": "K6",
                "S17": "K7", "S18": "J7",
                "S19": "L7", "S20": "L8",
                "S21": "L10", "S22": "K10",
                "S23": "K11", "S24": "L11",
                "S25": "-",  # GND
                "S26": "E11", "S27": "E10",
                "S28": "A11", "S29": "A10",
                "S30": "-",  # GND
            },
        ),
        Connector(
            "J2",
            0,
            {
                "S1": "-",  # GND
                "S2": "B2", "S3": "C2",
                "S4": "F2", "S5": "F1",
                "S6": "A1", "S7": "DB",
                "S8": "E1", "S9": "D1",
                "S10": "-",  # GND
                "S11": "C1", "S12": "B1",
                "S13": "A2", "S14": "A3",
                # MIPI D-PHY Pairs
                "S15": "-",  # GND
                "D0P": "D3", "D0N": "D3",
                "S18": "-",  # GND
                "D1P": "CK", "D1N": "CK",
                "S21": "-",  # GND
                "D2P": "D2", "D2N": "D2",
                "S24": "-",  # GND
                "D3P": "D1", "D3N": "D1",
                "S27": "-",  # GND
                "D4P": "D0", "D4N": "D0",
                "S30": "-",  # GND
            },
        ),
        Connector(
            "J2",
            1,
            {
                "S1": "-", "S2": "-",  # VCCIO2/3
                "S3": "L2", "S4": "L1",
                "S5": "K1", "S6": "K2",
                "S7": "J4", "S8": "K4",
                "S9": "G2", "S10": "G1",
                "S11": "L4", "S12": "L3",
                "S13": "J1", "S14": "J2",
                "S15": "G4", "S16": "H4",
                "S17": "H1", "S18": "H2",
                "S19": "-", "S20": "-",  # 1V8
                "S21": "-", "S22": "-",  # 2V5
                "S23": "-", "S24": "-",  # 3V3
                "S25": "-",  # 3V3
                "S26": "-",  # 5V
                "S27": "-", "S28": "-",  # 5V
                "S29": "-", "S30": "-",  # 5V
            },
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


class TangPrimer25kDockPlatform(TangPrimer25kPlatform):
    resources = TangPrimer25kPlatform.resources + [
        *ButtonResources(
            pins={0: "S21", 1: "S20"},
            invert=True,
            conn=("J1", 0),
            attrs=Attrs(
                IO_TYPE="LVCMOS33", PULLMODE="DOWN", DRIVE="OFF", BANK_VCCIO="3.3"
            ),
        ),
        *LEDResources(
            pins={0: "S9", 1: "S13"},
            invert=False,
            conn=("J1", 0),
            attrs=Attrs(IO_TYPE="LVCMOS33"),
        ),
        Resource(
            "usb",
            0,
            Subsignal("d_p", Pins("S15", conn=("J1", 1), dir="io")),
            Subsignal("d_n", Pins("S16", conn=("J1", 1), dir="io")),
            Subsignal("pullup", Pins("S9", dir="o", conn=("J1", 0))),
            Attrs(IO_TYPE="LVCMOS33", DRIVE="4", PULLMODE="NONE"),
        ),
    ]
    connectors = TangPrimer25kPlatform.connectors + [
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


if __name__ == "__main__":
    from .test.blinky import *

    TangPrimer25kDockPlatform().build(Blinky(), do_program=True)
