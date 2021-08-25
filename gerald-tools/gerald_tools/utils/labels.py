from aenum import OrderedEnum


class GERALDLabels(OrderedEnum):
    # Main signals
    Hp_0 = 0
    Hp_0_HV = 1
    Hp_0_Ks = 2
    Hp_0_Sh = 3
    Hp_1 = 4
    Hp_2 = 5
    Vr_0 = 6
    Vr_1 = 7
    Vr_2 = 8
    Ks_1 = 9
    Ks_2 = 10
    # Mast signs
    Mast_Sign_WRW = 11
    Mast_Sign_WYWYW = 12
    Mast_Sign_Y_Triangle = 13
    # Electrical signs
    El_6 = 14
    # Secondary signals
    Ne_1 = 15
    Ne_2 = 16
    Ne_3_1 = 17
    Ne_3_2 = 18
    Ne_3_3 = 19
    Ne_3_4 = 20
    Ne_3_5 = 21
    Ne_4 = 22
    Ne_5 = 23
    Ne_6 = 24
    Ne_7a = 25
    Ne_7b = 26
    # Low speed signals
    Lf_2 = 27
    Lf_3 = 28
    Lf_6 = 29
    Lf_7 = 30
    # Shunting signals
    Ra_10 = 31
    # Protection signals
    Sh_0 = 32
    Sh_1 = 33
    Sh_2 = 34
    # Assignment signals
    So_20_Right = 35
    So_20_Left = 36
    # Switch signals
    Wn_1 = 37
    Wn_2 = 38
    # Additional signals
    Zs_2 = 39
    Zs_2v = 40
    Zs_3 = 41
    Zs_3v = 42
    Zs_6 = 43
    Zs_Off = 44
    # Other signals
    Hectometer_Sign = 45
    ICE = 46
    LZB = 47
    # Platform signals
    Platform_Display = 48
    Platform_Track_Sign = 49
    Platform_Warn_Sign = 50
    Platform_Text_Sign = 51
    Ride_Indicator_Off = 52
    Ride_Indicator_1 = 53
    Ride_Indicator_2 = 54
    # Other
    Sign_Back = 55
    Signal_Back = 56
    Signal_Off = 57
    Signal_Identifier_Sign = 58
    Signal_Invalid = 59
    Traffic_Sign = 60
    Traffic_Light = 61


class LightCondition(OrderedEnum):
    Unknown = 0
    Daylight = 1
    Twilight = 2
    Dark = 3


class WeatherCondition(OrderedEnum):
    Unknown = 0
    Sunny = 1
    Cloudy = 2
    Rainy = 3
    Snowy = 4
    Foggy = 5
