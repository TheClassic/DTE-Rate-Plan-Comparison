from energy_comparison import energy_comparison as e
from energy_comparison import additionalInfo

import pytest
import unittest
assertions = unittest.TestCase('__init__')

offPeak = 0.01184 + 0.03403 + 0.06879
midPeak = 0.05486 + 0.03403 + 0.06879
peak = 0.12658 + 0.03403 + 0.06879


def test_dynamic_price():
  assert e.dynamic_price_per_kWH(e.SUNDAY, 16, 0) == offPeak, "Offpeak pricing"
  
  assert e.dynamic_price_per_kWH(e.MONDAY, 0, 0) == offPeak, "Offpeak pricing"
  assert e.dynamic_price_per_kWH(e.MONDAY, 6, 0) == offPeak, "Offpeak pricing"
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.MONDAY, 7, 0), midPeak )
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.MONDAY, 8, 0), midPeak )
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.MONDAY, 14, 0), midPeak )
  assert e.dynamic_price_per_kWH(e.MONDAY, 15, 0) == peak, "Peak pricing"
  assert e.dynamic_price_per_kWH(e.MONDAY, 18, 0) == peak, "Peak pricing"
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.MONDAY, 19, 0), midPeak )
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.MONDAY, 22, 0), midPeak )
  assert e.dynamic_price_per_kWH(e.MONDAY, 23, 0) == offPeak, "Offpeak pricing"

  assert e.dynamic_price_per_kWH(e.FRIDAY, 0, 0) == offPeak, "Offpeak pricing"
  assert e.dynamic_price_per_kWH(e.FRIDAY, 6, 0) == offPeak, "Offpeak pricing"
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.FRIDAY, 7, 0), midPeak )
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.FRIDAY, 8, 0), midPeak )
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.FRIDAY, 14, 0), midPeak )
  assert e.dynamic_price_per_kWH(e.FRIDAY, 15, 0) == peak, "Peak pricing"
  assert e.dynamic_price_per_kWH(e.FRIDAY, 18, 0) == peak, "Peak pricing"
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.FRIDAY, 19, 0), midPeak )
  assertions.assertAlmostEqual(e.dynamic_price_per_kWH(e.FRIDAY, 22, 0), midPeak )
  assert e.dynamic_price_per_kWH(e.FRIDAY, 23, 0) == offPeak, "Offpeak pricing"

  assert e.dynamic_price_per_kWH(e.SATURDAY, 16, 0) == offPeak, "Offpeak pricing"

flatLower = .04405+.03945+.06879
flatHigher = .06347+.03945+.06879

def test_flat_price():

  additionalInfo.kWHUsedSoFarToday = 0
  assert e.flat_price_per_kWH(e.SUNDAY, 16, additionalInfo) == flatLower, "Lower price"

  additionalInfo.kWHUsedSoFarToday = 17
  assert e.flat_price_per_kWH(e.SUNDAY, 16, additionalInfo) == flatLower, "Lower price"

  additionalInfo.kWHUsedSoFarToday = 18
  assert e.flat_price_per_kWH(e.SUNDAY, 16, additionalInfo) == flatHigher, "Lower price"
  
if __name__ == '__main__':
    pytest.main()

# Aug 20 - Sep 21
# Bill 574.81 (520.7 without tax)
# current calc is 503.9
