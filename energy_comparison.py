# Dynamic peak pricing according to
# https://www.newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES
# ref 23639801/PDF/2-23/RES
# as of Apr 28, 2023

import datetime
import argparse
import csv

class additionalInfo:
  kWHUsedSoFarToday = 0
  criticalPeakHoursUsage = {
    15:[],
    16:[],
    17:[],
    18:[]
  }

class plan_comparison:
  MONDAY = 0
  FRIDAY = 4
  SATURDAY = 5
  SUNDAY = 6

  plans = {
    'timeOfDay3p7p':{
      'name': 'Time of Day 3 p.m. - 7 p.m.',
      'runningTotal': 0
    },
    'timeOfDay11a7p': {
      'name': 'Time of Day 11 a.m. - 7 p.m.',
      'runningTotal': 0
    },
    'dynamic': {
      'name': 'Dynamic',
      'criticalPeakTotal': 0,
      'noteKey': '*',
      'noteValue': 'Note, dynamic price plan will have up to 14 unknown days with "critical" peak rates. The amount here is an estimate based on 14 days of average usage at the critical peak rate.',
      'runningTotal': 0
    },
    'fixed': {
      'name': 'Fixed price (deprecated)',
      'runningTotal': 0
    }
  }

  def compare():
    plan_comparison.calc_costs(plan_comparison.get_csv_reader(args.filename))

    print("{:<30} {}".format("PLAN", "COST"))
    print("{0:<30} {0}".format("-"*30))
    
    notes = []
    
    for plan in plan_comparison.plans.keys():
      line = "{:<30} ${:.0f}".format(plan_comparison.plans[plan]['name'], plan_comparison.plans[plan]['runningTotal'])
      if 'criticalPeakTotal' in plan_comparison.plans[plan]:
        line += " + ~${:.0f}".format(plan_comparison.plans[plan]['criticalPeakTotal'])
      if 'noteKey' in plan_comparison.plans[plan] and 'noteValue' in plan_comparison.plans[plan]:
        line += plan_comparison.plans[plan]['noteKey']
        notes.append(plan_comparison.plans[plan]['noteKey'] + ' ' + plan_comparison.plans[plan]['noteValue'])
      print(line)
    
    for note in notes:
      print("""\n"""+note)

  def get_csv_reader(file):
    args.filename.seek(0)
    return csv.DictReader(args.filename)
  
  def calc_costs(csvReader):
    dailyTotal = 0.
    
    for row in csvReader:
        month = datetime.datetime.strptime(row['Day'], "%m/%d/%Y").month
        day = datetime.datetime.strptime(row['Day'], "%m/%d/%Y").weekday()
        hour = datetime.datetime.strptime(row['Hour of Day'], "%I:%M %p").hour

        hourlyTotal = row['Hourly Total']
        if(hourlyTotal == 'No Data'):
            hourlyTotal = 0
          
        kwh = float(hourlyTotal)

        dailyTotal = plan_comparison.accumulate_daily_total(hour, kwh, dailyTotal)
        additionalInfo.kWHUsedSoFarToday = dailyTotal
        for plan in plan_comparison.plans.keys():
          plan_comparison.plans[plan]['runningTotal'] += kwh * plan_comparison.calc_price_per_kWH(plan, hour=hour, day=day, month=month)
        plan_comparison.accumulate_critical_peak(hour, day, kwh)

    for plan in plan_comparison.plans.keys():
      if 'criticalPeakTotal' in plan_comparison.plans[plan]:
        plan_comparison.plans[plan]['criticalPeakTotal'] = plan_comparison.calc_critical_peak_estimate()

    return

  def accumulate_daily_total(hour, hourlyTotal, dailyTotal):
    if(hour==0):
        dailyTotal = 0
    dailyTotal += hourlyTotal
    return dailyTotal
  
  def accumulate_critical_peak(hour, day, kwh):
    if plan_comparison.is_weekday(day) and hour in additionalInfo.criticalPeakHoursUsage.keys():
      additionalInfo.criticalPeakHoursUsage[hour].append(kwh)
    return

  def is_weekday(day):
    return day != plan_comparison.SATURDAY and day != plan_comparison.SUNDAY

  def calc_price_per_kWH(plan, **kwargs):
    price = 0
    if plan == 'timeOfDay3p7p':
      # https://solutions.dteenergy.com/dte/en/Products/Time-of-Day-3-p-m---7-p-m-/p/TOD-3-7
      # Time of Day 3 p.m. – 7 p.m. Standard Base Rate (D1.11)
      # On-peak hours: Monday-Friday 3 p.m. to 7 p.m.
      if plan_comparison.is_weekday(kwargs['day']) and kwargs['hour'] >= 15 and kwargs['hour'] < 19:
        if kwargs['month'] >= 6 and kwargs['month'] <= 9: #June through September
          price = .07941 + .06160
        else:
          price = .05560 + .04313
      else: #off-peak
          price = .04828 + .03746

      price += .06879 # distribution
    elif plan == 'timeOfDay11a7p':
      # https://solutions.dteenergy.com/dte/en/Products/Time-of-Day-11-a-m---7-p-m-/p/TOD-11-7
      # Time of Day 11 a.m. - 7 p.m. Rate (D1.2)
      # On-peak hours: Monday-Friday 11 a.m. to 7 p.m.
      if plan_comparison.is_weekday(kwargs['day']) and kwargs['hour'] >= 11 and kwargs['hour'] < 19:
        if kwargs['month'] >= 6 and kwargs['month'] <= 10: #June through October
          price = .11033
        else:
          price = .08682
      else: #off-peak
        if kwargs['month'] >= 6 and kwargs['month'] <= 10: #June through October
          price = .00991
        else:
          price = .00792

      price += .04105 # non-capacity
      price += .06879 # distribution
    elif plan == 'dynamic':
      # https://solutions.dteenergy.com/dte/en/c/Dynamic-Peak-Pricing/p/DPP
      # Dynamic Peak Pricing Rate (D1.8)
      # This rate features three price tiers, as well as, Critical Peak prices
      # for days when Critical Peak Events are called. It requires your
      # home to have the advanced electric meter and may not be
      # combined with any other tariff, rider, or separately metered
      # service, other than Rider 18 (if available)
      price = 0.01184 #off-peak
    
      if plan_comparison.is_weekday(kwargs['day']):
        if kwargs['hour'] >= 15 and kwargs['hour'] < 19:
          price = .12658 #peak between 3 and 7
        elif (kwargs['hour'] >= 7 and kwargs['hour'] < 15) or (kwargs['hour'] >= 19 and kwargs['hour'] < 23):
          price = .05486 #mid-peak

      price += .03403 # non-capacity
      price += .06879 # distribution
    elif plan == 'fixed':
      price = .04405
      nonCapacity = .03945
      if additionalInfo.kWHUsedSoFarToday > 17:
        price = .06347
        nonCapacity = .03945

      price += nonCapacity
      price +=  .06879 # distribution
    return price
  
  def calc_critical_peak_estimate():
    # https://solutions.dteenergy.com/dte/en/c/Dynamic-Peak-Pricing/p/DPP
    # Dynamic Peak Pricing Rate (D1.8)
    # Critical peak events occur no more than 14 weekdays per year
    # from 3 p.m. to 7p.m.
    price = 0.91597
    nonCapacity = 0.03403
    distribution = 0.06879
    price += nonCapacity + distribution
    cost = 0
    for hour in additionalInfo.criticalPeakHoursUsage.keys():
      avgKwh = sum(additionalInfo.criticalPeakHoursUsage[hour]) / len(additionalInfo.criticalPeakHoursUsage[hour])
      # Regular dynamic pricing is already calculated for all dates, so this estimate should be the critical rate minus the regular dynamic rate
      additionalPrice = price - plan_comparison.calc_price_per_kWH('dynamic', hour=hour, day=plan_comparison.MONDAY)
      cost += avgKwh * additionalPrice
    cost = cost * 14
    return cost

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calculate energy cost')
    parser.add_argument('filename', type=argparse.FileType('r'),
                        help='input data file')

    args = parser.parse_args()

    plan_comparison.compare()

