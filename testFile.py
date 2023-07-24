import datetime
import math
import unittest
from datetime import date

import GPT
import main2
import test


class MyTestCase(unittest.TestCase):

    # def test_gpt(self):
    #     self.assertEqual(0, GPT.open_weather_file())
    #
    # def test_locationToTimeZone(self):
    #     self.assertEqual("Europe/Rome", main2.calculateTimezoneFromLocation("Iglesias, Sardinia"))
    #
    # def test_locationToTimeZone2(self):
    #     self.assertEqual("0", main2.calculateTimezoneFromLocation("Forfar, Scotland"))
    #
    # def test_latitude(self):
    #     self.assertEqual(56.46, round(main2.calculateLatitude("Dundee, Scotland"), 2))
    #
    # def test_timezoneDifferenceFromGreenwich(self):
    #     self.assertEqual(1, main2.calculateDifferenceCurrentAndGreenwichTime("Edinburgh"))
    #
    # def test_SolarTime(self):
    #     self.assertEqual(datetime.datetime(2023, 6, 17, 21, 3),
    #                      main2.addHours(datetime.datetime(2023, 6, 17, 19, 3), 2))
    #
    # # def test_sunAngle(self):
    # #     self.assertEqual(173.76077693189808,
    # #                      math.degrees(main2.calculateElevation(datetime.datetime(2023, 6, 15, 13), "Forfar, Scotland",
    # #                                                            [datetime.datetime(2023, 6, 15, 14, 0), datetime.datetime(2023, 6, 15, 15, 0)])))
    # #
    # # def test_sunAngle2(self):
    # #     self.assertEqual(0, math.degrees(
    # #         main2.calculateElevation(datetime.datetime(2023, 6, 15, 18), ("Forfar, Scotland"),
    # #                                                            [datetime.datetime(2023, 6, 15, 14, 0), datetime.datetime(2023, 6, 15, 15, 0)])))
    #
    # #
    # # def test_sunAngle3(self):
    # #     self.assertEqual(0, math.degrees(main2.calculateElevation(datetime.datetime(2023,6,16,12), "Forfar, Scotland")))
    # #
    # # def test_sunAngle4(self):
    # #     self.assertEqual(0, math.degrees(test.calculateElevation(datetime.datetime(2023,6,16,18), "Forfar, Scotland")))
    #
    # # def test_sunAngle5(self):
    # #     self.assertEqual(0, math.degrees(test.calculateElevation(datetime.datetime(2023,5,16,8), "Forfar, Scotland",
    # #                                                              [datetime.datetime(2023, 5, 16, 13, 30), datetime.datetime(2023, 5, 16, 14, 0)])))
    # #
    # # def test_sunAngle6(self):
    # #     self.assertEqual(0, math.degrees(test.calculateElevation(datetime.datetime(2023,5,16,17), "Forfar, Scotland",
    # #                                                              [datetime.datetime(2023, 5, 16, 13, 30), datetime.datetime(2023, 5, 16, 14, 0)])))
    #
    # # def test_peak(self):
    # #     self.assertEqual(0, main2.get_solar_noon(datetime.datetime(2023,5,16,2), datetime.datetime(2023,5,16,23),"Forfar, Scotland"))
    #
    #
    # def test_integral(self):
    #     self.assertEqual(2, main2.calculateIntegral(lambda x: math.sin(x), 0, math.pi))
    #
    # def test_calculateTimeOfDay(self):
    #     self.assertEqual(15.359330524576922, main2.calculateTimeOfDay(datetime.datetime(2023, 6, 18),
    #                                                                   main2.calculateLatitude(
    #                                                                       "Fiorano Modenese, Italy")))
    #
    # def test_dt(self):
    #     self.assertEqual(127.77530183262455, main2.calculateSolarConstant("Fiorano Modenese, Italy",
    #                                                                       datetime.datetime(2023, 6, 18)))
    #
    # def test_hourAdd(self):
    #     self.assertEqual(datetime.datetime(2023, 6, 7, 19), main2.addHours(datetime.datetime(2023, 6, 7, 17), 2))
    #
    # def test_hourSwap(self):
    #     self.assertEqual(datetime.datetime(2023, 6, 7, 19), main2.replace_hour(datetime.datetime(2023, 6, 7, 17), (
    #         datetime.datetime(2023, 6, 7, 19)).hour))
    #
    # def test_conversion(self):
    #     self.assertEqual(12.064562064443999 * 2, main2.convert_mj_to_kwh(43432423431.9983978))
    #
    # # def test_callAPI(self):
    # #     self.assertEqual(20, main2.callToWeatherAPI(datetime.datetime(2023, 7, 5, 2),
    # #                                                 datetime.datetime(2023, 7, 5, 23),
    # #                                                 "Dundee, Scotland"))
    #
    # # def test_mike(self):
    # #     self.assertEqual(0, main2.calculate_actual_solar_energy(datetime.datetime(2023, 5, 24, 1),
    # #                                                         datetime.datetime(2023, 5, 24, 23),
    # #                                                         "Forfar, Scotland", 97320, 20, 40, 2.5))
    #
    # # def test_mike2(self):
    # #     self.assertEqual(0, GPT.main())
    #
    # def test_convert_to_unix(self):
    #     self.assertEqual(1688518800, main2.convert_to_unix_time(datetime.datetime(2023, 7, 5, 2), "Dundee, Scotland"))
    #
    # # def test_testing(self):
    # #     self.assertEqual(0, main2.convert_mj_to_kwh(main2.calculate_actual_solar_energy(datetime.datetime(2023, 6, 3, 12),
    # #                                                                                   datetime.datetime(2023, 6, 3, 13),"Forfar, Scotland",97320,
    # #                                                                                   20,
    # #                                                                                   40, 2.5)))
    #
    # # def test_bing(self):
    # #     self.assertEqual(0, test.calculateDifferentialEnergy(datetime.datetime(2023, 6, 15, 12),datetime.datetime(2023, 6, 15, 13),"Forfar, Scotland", 97320
    # #                                                          ,[datetime.datetime(2023, 6, 15, 14, 0), datetime.datetime(2023, 6, 15, 15, 0)],40,2.5))
    #
    # # def test_altitude_average(self):
    # #     self.assertEqual(45, math.degrees(main2.calculate_average_altitude(datetime.datetime(2023, 5, 8, 11),
    # #                                                         datetime.datetime(2023, 5, 8, 12),
    # #                                                         "Forfar, Scotland")))
    #
    # # def test_diff_times(self):
    # #     self.assertEqual(3, main2.calculate_difference_between_times(datetime.datetime(2023, 6, 3, 17), datetime.datetime(2023, 6, 3, 20)))
    #
    # # def test_noon_angle(self):
    # #     self.assertEqual(60, main2.get_solar_noon(datetime.datetime(2023, 6, 15, 2), datetime.datetime(2023, 6, 15, 23),
    # #                                               "Forfar, Scotland"))
    #
    #     # 2kwh per hour
    #
    # def test_duplicate_list(self):
    #     self.assertEqual([1, 1, 2, 2, 3, 3], main2.duplicate_list([1, 2, 3]))
    #
    # def test_add_minutes(self):
    #     self.assertEqual(datetime.datetime(2023,7,13,12,30), main2.add_minutes_to_datetime(datetime.datetime(2023,7,13,12),30))
    #
    # # def test_kwh2(self):
    # #     self.assertEqual(0, main2.convert_mj_to_kwh(1234567))
    #
    #
    # # def test_weatherAPI(self):
    # #     self.assertEqual(0, GPT.callToWeatherAPI(datetime.datetime(2023,5,24,1),
    # #                                              datetime.datetime(2023,5,25,1),
    # #                                              ))
    #
    # def test_addHours2(self):
    #     self.assertEqual(24, GPT.calculate_difference_between_times(datetime.datetime(2023,5,24,0),datetime.datetime(2023,5,25,0)))

    def test_maingpt(self):
        self.assertEqual(0, GPT.main())

if __name__ == '__main__':
    unittest.main()
