![ScreenShot](/screenshot.png)

### Purpose
This script is useful for using historical usage data to compare DTE Electric Rate Plans.

*Disclaimer:* I don't know Python well. And I don't know common coding style for Python. I will happily accept any style improvements to this project and learn from them.

*Disclaimer:* I can't guarantee the correctness of the results. More units tests will help (called out below). I have verified results of this against my own usage data (see details below) and had enough confidence to change my own plan.

### How to Use
- Download data from https://usage.dteenergy.com for desired period as csv
- Pass path to data file to script as a parameter e.g. `python energy_comparison.py electric_usage_report_09-01-2021_to_09-14-2022.csv`
- Change plan with DTE, if it makes sense
- Savings

### Potential Future Features
1. Better testing (e.g. ensure days of week and months are correctly interpreted, may require refactoring into better units)
1. End-to-end verification
1. ~~Peak pricing simulation~~
1. Auto-download data from DTE

### Data Source
[DTE Electric Rate Card](https://newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES) w/ ref 23639801/PDF/2-23/RES		

### Other Notes
My bill has some volumetric charges not mentioned on the rate card:
- Power Supply Cost Recovery @ 0.006650
- Other Delivery Volumetric Surcharges 
- Sales Tax

### Verification
I compared a recent month of my Fixed Rate plan to the calculated value from this script. The variance was less than $3 (0.5%).

I created an Excel sheet to calculate time-of-day cost for a month of data and compared it to the value calculated by the script and the value matched within a fraction of a cent.
