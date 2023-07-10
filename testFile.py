import datetime
import math
import unittest
from datetime import date

import main2
import test


class MyTestCase(unittest.TestCase):

    def test_locationToTimeZone(self):
        self.assertEqual("Europe/Rome", main2.calculateTimezoneFromLocation("Iglesias, Sardinia"))

    def test_latitude(self):
        self.assertEqual(56.46 , round(main2.calculateLatitude("Dundee, Scotland"), 2))

    def test_timezoneDifferenceFromGreenwich(self):
        self.assertEqual(1, main2.calculateDifferenceCurrentAndGreenwichTime("Edinburgh"))

    def test_SolarTime(self):
        self.assertEqual(datetime.datetime(2023, 6, 17, 21, 3), main2.addHours(datetime.datetime(2023, 6, 17, 19, 3), 2))

    def test_sunAngle(self):
       self.assertEqual(173.76077693189808, math.degrees(main2.calculateElevation(datetime.datetime(2023,6,17,21,4),
                                                                                  "Fiorano Modenese, Italy")))

    def test_sunAngle2(self):
        self.assertEqual(0, math.degrees(test.calculateElevation(datetime.datetime(2023,6,17,13),
                                                                                  "Forfar, Scotland")))

    def test_integral(self):
        self.assertEqual(2, main2.calculateIntegral(lambda x: math.sin(x),0,math.pi))

    def test_calculateTimeOfDay(self):
        self.assertEqual(15.359330524576922, main2.calculateTimeOfDay(datetime.datetime(2023,6,18),
                                                                     main2.calculateLatitude("Fiorano Modenese, Italy")))

    def test_sun_position(self):
        self.assertEqual(-23.42556882386057, main2.calculate_sun_position(datetime.datetime(2023,12,24)))

    def test_dt(self):
        self.assertEqual(127.77530183262455, main2.calculateSolarConstant("Fiorano Modenese, Italy",
                                                                          datetime.datetime(2023,6,18)))

    def test_hourAdd(self):
        self.assertEqual(datetime.datetime(2023,6,7,19), main2.addHours(datetime.datetime(2023,6,7,17),2))

    def test_hourSwap(self):
        self.assertEqual(datetime.datetime(2023,6,7,19), main2.replace_hour(datetime.datetime(2023,6,7,17),(datetime.datetime(2023,6,7,19)).hour))

    def test_conversion(self):
        self.assertEqual(12.064562064443999, main2.convert_mj_to_kwh(43432423431.9983978))

    # def test_callAPI(self):
    #     self.assertEqual(20, main2.callToWeatherAPI(datetime.datetime(2023, 7, 5, 2),
    #                                                 datetime.datetime(2023, 7, 5, 23),
    #                                                 "Dundee, Scotland"))

    # def test_mike(self):
    #     self.assertEqual(0, main2.calculate_actual_solar_energy(datetime.datetime(2023, 5, 8, 2),
    #                                                         datetime.datetime(2023, 5, 8, 23),
    #                                                         "Forfar, Scotland", 97320, 20))

    def test_convert_to_unix(self):
        self.assertEqual(1688518800, main2.convert_to_unix_time(datetime.datetime(2023,7,5,2), "Dundee, Scotland"))

    def test_testing(self):
        self.assertEqual(0, main2.convert_mj_to_kwh(main2.calculateDifferentialEnergy(datetime.datetime(2023, 7, 6, 12),
                                                              datetime.datetime(2023, 7, 6, 14), "Forfar, Scotland", 97320)))

    # def test_altitude_average(self):
    #     self.assertEqual(45, math.degrees(main2.calculate_average_altitude(datetime.datetime(2023, 5, 8, 11),
    #                                                         datetime.datetime(2023, 5, 8, 12),
    #                                                         "Forfar, Scotland")))

    # def test_diff_times(self):
    #     self.assertEqual(3, main2.calculate_difference_between_times(datetime.datetime(2023, 6, 3, 17), datetime.datetime(2023, 6, 3, 20)))



        #2kwh per hour

if __name__ == '__main__':
    unittest.main()