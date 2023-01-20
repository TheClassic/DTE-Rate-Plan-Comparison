# Dynamic peak pricing according to
# https://www.newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES
# as of Sept 18, 2022

import datetime
import argparse
import csv

class additionalInfo:
    month = 0
    kWHUsedSoFarToday = 0

class energy_comparison:
  MONDAY = 0
  FRIDAY = 4
  SATURDAY = 5
  SUNDAY = 6

  def compare():

    csvreader = energy_comparison.get_csv_reader(args.filename)

    dynamicPrice = energy_comparison.calc_cost(energy_comparison.get_csv_reader(args.filename), energy_comparison.dynamic_price_per_kWH)
    fixedPrice = energy_comparison.calc_cost(energy_comparison.get_csv_reader(args.filename), energy_comparison.flat_price_per_kWH)
    timeofDayPrice = energy_comparison.calc_cost(energy_comparison.get_csv_reader(args.filename), energy_comparison.timeofday_price_per_kWH)
    futureDefault = energy_comparison.calc_cost(energy_comparison.get_csv_reader(args.filename), energy_comparison.flat_price_replacement)

    print("Dynamic price:          ${:.0f}*".format(dynamicPrice))
    print("Fixed price (default):  ${:.0f}".format(fixedPrice))
    print("Time of Day price:      ${:.0f}".format(timeofDayPrice))
    print("Future default:         ${:.0f}".format(futureDefault))

    print("""\n*Note, dynamic price plan will have peak days with additional charges not calculated here, that could be as much as $25 a day for multiple days a year. Please dive deeper, consider this, and plan accordingly.""")

  def calc_cost(csvreader, pricingPlan):
    cost = 0.
    dailyTotal = 0.
    
    for row in csvreader:
        month = datetime.datetime.strptime(row['Day'], "%m/%d/%Y").month
        day = datetime.datetime.strptime(row['Day'], "%m/%d/%Y").weekday()
        hour = datetime.datetime.strptime(row['Hour of Day'], "%I:%M %p").hour

        hourlyTotal = row['Hourly Total']
        if(hourlyTotal == 'No Data'):
            hourlyTotal = 0
          
        kwh = float(hourlyTotal)

        dailyTotal = energy_comparison.accumulateDailyTotal(hour, kwh, dailyTotal)
        additionalInfo.kWHUsedSoFarToday = dailyTotal
        additionalInfo.month = month
        cost += kwh*pricingPlan(day, hour, additionalInfo)
    return cost

  def accumulateDailyTotal(hour, hourlyTotal, dailyTotal):
    if(hour==0):
        dailyTotal = 0
    dailyTotal += hourlyTotal
    return dailyTotal

  def get_csv_reader(file):
    args.filename.seek(0)
    return csv.DictReader(args.filename)

  def dynamic_price_per_kWH(day, hour, additionalInfo):
  # peak Mon-Fri 3pm to 7pm
    price = 0.01184 #offpeak
    
    if day != energy_comparison.SATURDAY and day != energy_comparison.SUNDAY:
      if hour >= 15 and hour < 19:
        price = .12658 #peak between 3 and 7
      elif hour >= 7 and hour < 15 or hour >= 19 and hour < 23:
        price = .05486 #midpeak

    price += .03403 # non-capacity (note that the rate card indicates a different rate for midpeak, but I believe it to be a typo)
    price += .06879 # distribution
    
    return price

  def timeofday_price_per_kWH(day, hour, additionalInfo):
  # peak Mon-Fri 3pm to 7pm (D1.2)
    price = 0
    if day != energy_comparison.SATURDAY and day != energy_comparison.SUNDAY and hour >= 11 and hour < 19:
      if additionalInfo.month >= 6 and additionalInfo.month <= 10: #June through October
        price = .11033
      else:
        price = .08682
    else: #offpeak
      if additionalInfo.month >= 6 and additionalInfo.month <= 10: #June through October
        price = .00991
      else:
        price = .00792

    price += .04105 # non-capacity
    price +=  .06611 # distribution

    return price

  def flat_price_per_kWH(day, hour, additionalInfo):
  # D1
    price = .04405
    noncapacity = .03945
    if additionalInfo.kWHUsedSoFarToday > 17:
      price = .06347
      noncapacity = .03945

    price += noncapacity
    price +=  .06879 # distribution
    return price

  def flat_price_replacement(day, hour, additionalInfo):
  # https://solutions.dteenergy.com/dte/en/Products/Time-of-Day-3-p-m---7-p-m-/p/TOD-3-7?_ga=2.259465164.775611877.1673536052-1020470228.1671801533&_gl=1*1z6xuy*_ga*MTAyMDQ3MDIyOC4xNjcxODAxNTMz*_ga_J2R5W9DWE4*MTY3MzUzNjA1Mi40LjEuMTY3MzUzNjYwNS4wLjAuMA..
  # peak Mon-Fri 3pm to 7pm (D1.2)
    price = 0
    if day != energy_comparison.SATURDAY and day != energy_comparison.SUNDAY and hour >= 15 and hour < 19:
      if additionalInfo.month >= 6 and additionalInfo.month <= 9: #June through September
        price = .2098
      else:
        price = .1675
    else: #offpeak
        price = .1545

    return price

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calcuate energy cost')
    parser.add_argument('filename', type=argparse.FileType('r'),
                        help='input data file')


    args = parser.parse_args()

    energy_comparison.compare()

