# OnePlus 10 Pro (NE2213) charging test

Date: 26 October 2026.

The phone was on Android 16

- V16.0.3
- Software Version NE2213_16.0.3.530
- Model NE2213EEA

## The short version

- The phone limits its own charging current.
- The adapter and the cable do not seem to be the problem.
- I expected 80W from an 80W adapter, and the phone never got there.
- It peaked at about 30W for a few seconds and then settled near 21W. While not going over the thermal caps

## Setup

The phone started at 11% charge with an 80W SVOOC adapter.
The charger reported 10V the whole time. (Charger voltage : 10000)
While charging i was cooling the phone using a peltier phone cooler.
Any battery and charging related settings which would suggest charging limitations have been deactivated.
"High performance mode" was active.

I logged three things:

- `dumpsys battery` every 30 seconds. ( Script: `./scripts/battery_log.ps1` )
- The `BatteryChargeControl` logcat lines, which show the per-cell limits. ( Script: `./scripts/logcat.bat`)
- The wall power using a tasmota smart plug logging to Home Assistant.

I swapped the cable partway through to check for a broken cable. ( From the official cable to a off-brand one, which apparently has the svooc control pin on USB-A. )
It came out at 21:14:49 and the other in at 21:15:19. The old and new cables gave the same plateau.

## What the phone did

| Level     | Pack current            | Battery power (est.)        | Per-cell limit    | Notes                             |
| --------- | ----------------------- | --------------------------- | ----------------- | --------------------------------- |
| 11%       | about 3.5 A             | about 29.5 W                | 7.3 A, then 4.2 A | Peak, lasted about 10 seconds     |
| 14 to 21% | about 3.0 A             | about 25 W                  | 3.5 A, then 3.0 A | Stepping down                     |
| 21 to 44% | about 2.5 A             | about 21 to 22 W            | 2.5 A             | Long plateau, same on both cables |
| 44 to 67% | 2.5 A, falling to 1.2 A | about 13 W, falling to 10 W | 2.0 A, then 1.5 A | Two more steps down               |
| 67 to 90% | about 1.0 A             | about 4W                    | 1.0 A             | Slowest part of the charge        |

The plug read 25 to 30W at the start, which matches the battery estimate.

The phone warmed to about 23 °C and then cooled to about 18 °C. That's far below the 37 °C threshold where the SVOOC thermal table starts to cap current, so heat didn't cause the steps.

## Why the phone holds back

Three things point to the phone's own charge logic.

The charger was identified as normal SVOOC. The logs show no abnormal-adapter or cable-refusal messages.

`BatteryChargeControl` sets a maximum current for each cell and then picks a charge current under it.
Each value it chose was sent to the charger. The maximum drops as the charge goes up, and that matches the steps in the table.

## What the firmware has

I compared five builds: Android 11, Android 15, and three Android 16 builds, two of them with different model codes.

- All five have the 30W and 65W VOOC current tables. None has an 80W table.
- Android 15 added an 80 W abnormal-adapter check, which is in every later build.
- Android 15 also added an app flag, `unsupport_smartcharge_80w`.

## Disclaimer

I am not an Android firmware developer, nor a operating systems engineer.

So, this _research_ has been LLM-Assisted.

- It did the Firmware extracting and searching/comparing the firmware versions, including using ghidra to get more information.
- And it wrote the scripts and python notebook.
- Also writing the initial draft of this markdown file. (corrected and edited by me.)
