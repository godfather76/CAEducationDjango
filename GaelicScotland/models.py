from django.contrib.gis.db import models


class Shape(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    lat = models.FloatField()
    long = models.FloatField()
    geometry = models.MultiPolygonField()

class AdultLifestage(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_16 = models.IntegerField()
    total_16_to_24 = models.IntegerField()
    _16_to_24_no_dependent = models.IntegerField()
    _16_to_24_with_dependents = models.IntegerField()
    total_25_to_34 = models.IntegerField()
    _25_to_34_no_dependent = models.IntegerField()
    _25_to_34_youngest_0_to_4 = models.IntegerField()
    _25_to_34_youngest_5_to_10 = models.IntegerField()
    _25_to_34_youngest_11_to_15 = models.IntegerField()
    _25_to_34_youngest_16_to_18 = models.IntegerField()
    total_35_to_54 = models.IntegerField()
    _35_to_54_no_dependents = models.IntegerField()
    _35_to_54_youngest_0_to_4 = models.IntegerField()
    _35_to_54_youngest_5_to_10 = models.IntegerField()
    _35_to_54_youngest_11_to_15 = models.IntegerField()
    _35_to_54_youngest_16_to_18 = models.IntegerField()
    total_55_to_64 = models.IntegerField()
    _55_to_64_one_person = models.IntegerField()
    _55_to_64_two_or_more_no_dependents = models.IntegerField()
    _55_to_64_with_dependents = models.IntegerField()
    total_65_to_74 = models.IntegerField()
    _65_to_74_one_person = models.IntegerField()
    _65_to_74_two_or_more_no_dependents = models.IntegerField()
    _65_to_74_with_dependents = models.IntegerField()
    total_75_and_over = models.IntegerField()
    _75_and_over_one_person = models.IntegerField()
    _75_and_over_two_or_more_no_dependents = models.IntegerField()


class ArmedForcesVeterans(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_16 = models.IntegerField()
    UK_veteran = models.IntegerField()
    not_UK_veteran = models.IntegerField()


class EconomicActivity(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_16 = models.IntegerField()
    economically_active_not_student_total = models.IntegerField()
    not_student_employee_total = models.IntegerField()
    not_student_employee_parttime = models.IntegerField()
    not_student_employee_fulltime = models.IntegerField()
    not_student_selfemploy_w_employees_total = models.IntegerField()
    not_student_selfemploy_w_employees_parttime = models.IntegerField()
    not_student_selfemploy_w_employees_fulltime = models.IntegerField()
    not_student_selfemploy_no_employees_total = models.IntegerField()
    not_student_selfemploy_no_employees_parttime = models.IntegerField()
    not_student_selfemploy_no_employees_fulltime = models.IntegerField()
    not_student_unemployed_available = models.IntegerField()
    fulltime_student_total = models.IntegerField()
    fulltime_student_employee_total = models.IntegerField()
    fulltime_student_employee_parttime = models.IntegerField()
    fulltime_student_employee_fulltime = models.IntegerField()
    fulltime_student_selfemploy_w_employees_total = models.IntegerField()
    fulltime_student_selfemploy_w_employees_parttime = models.IntegerField()
    fulltime_student_selfemploy_w_employees_fulltime = models.IntegerField()
    fulltime_student_selfemploy_no_employees_total = models.IntegerField()
    fulltime_student_selfemploy_no_employees_parttime = models.IntegerField()
    fulltime_student_selfemploy_no_employees_fulltime = models.IntegerField()
    fulltime_student_unemployed_available = models.IntegerField()
    economically_inactive_total = models.IntegerField()
    retired = models.IntegerField()
    economically_inactive_student = models.IntegerField()
    home_or_family_care = models.IntegerField()
    long_term_sick_disabled = models.IntegerField()
    economically_inactive_other = models.IntegerField()


class GaelicLanguageScottish(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_3 = models.IntegerField()
    understands_only = models.IntegerField()
    speak_read_write = models.IntegerField()
    speak_only = models.IntegerField()
    speak_read_no_write = models.IntegerField()
    read_only = models.IntegerField()
    other_gaelic_skill = models.IntegerField()
    no_gaelic = models.IntegerField()


class GeneralHealth(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(
        max_length=50, blank=True, null=True
    )  # Added since constituency is present in pivoted output shape
    all_people = models.IntegerField()
    bad = models.IntegerField()
    fair = models.IntegerField()
    good = models.IntegerField()
    very_bad = models.IntegerField()
    very_good = models.IntegerField()


class HighestQualification(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_16 = models.IntegerField()
    no_quals = models.IntegerField()
    lower_school = models.IntegerField()
    upper_school = models.IntegerField()
    apprenticeships = models.IntegerField()
    subdegree_higher_ed = models.IntegerField()
    degree_level_above = models.IntegerField()


class HoursWorked(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    employed_population_over_16 = models.IntegerField()
    _0_to_15 = models.IntegerField()
    _16_to_30 = models.IntegerField()
    _31_to_48 = models.IntegerField()
    _49_or_more = models.IntegerField()


class Industry(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    employed_population_over_16 = models.IntegerField()
    ag_forestry_fishing = models.IntegerField()
    mining_quarrying = models.IntegerField()
    manufacturing = models.IntegerField()
    elec_gas_steam_ac = models.IntegerField()
    water_sewage_waste_mgmt = models.IntegerField()
    construction = models.IntegerField()
    wholesale_retail_vehicle_repair = models.IntegerField()
    transport_storage = models.IntegerField()
    accomodation_food_service = models.IntegerField()
    info_comms = models.IntegerField()
    financial_and_insurance = models.IntegerField()
    real_estate = models.IntegerField()
    professional_science_and_tech = models.IntegerField()
    admin_support_services = models.IntegerField()
    public_admin_defence = models.IntegerField()
    education = models.IntegerField()
    human_health_and_social_work = models.IntegerField()
    arts_entertainment_recreation = models.IntegerField()
    other_service_activities = models.IntegerField()
    household_as_employer = models.IntegerField()
    extraterrestrial_activity = models.IntegerField()


class LongTermHealthConditions(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population = models.IntegerField()
    deaf_or_partial_hear_impaired = models.IntegerField()
    blind_or_partial_vision_impaired = models.IntegerField()
    loss_of_voice = models.IntegerField()
    learning_disability_dev_disorder = models.IntegerField()
    physical_disability = models.IntegerField()
    mental_health_condition = models.IntegerField()
    longterm_illness_or_condition = models.IntegerField()


class LongTermHealthProblemOrDisability(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population = models.IntegerField()
    limited_a_lot = models.IntegerField()
    limited_a_little = models.IntegerField()
    not_limited = models.IntegerField()


class MaritalCivilPartnershipStatus(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(
        max_length=50, blank=True, null=True
    )  # Added to align with standard pattern
    divorced = models.IntegerField()
    married = models.IntegerField()
    never_married = models.IntegerField()
    population_over_16 = models.IntegerField()
    separated = models.IntegerField()
    widowed = models.IntegerField()


class Occupation(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    employed_population_over_16 = models.IntegerField()
    managers_senior_officials = models.IntegerField()
    corporate_managers_directors = models.IntegerField()
    other_manager_proprietor = models.IntegerField()
    professional_total = models.IntegerField()
    STEM_professionals = models.IntegerField()
    health_professionals = models.IntegerField()
    teaching_education_professionals = models.IntegerField()
    business_media_professionals = models.IntegerField()
    associate_professional_technical_total = models.IntegerField()
    STEM_associate_professionals = models.IntegerField()
    health_social_care_associate_professionals = models.IntegerField()
    protective_service = models.IntegerField()
    culture_media_sports = models.IntegerField()
    business_public_service_associate_professionals = models.IntegerField()
    admin_secretary = models.IntegerField()
    administrative = models.IntegerField()
    secretarial_related = models.IntegerField()
    skilled_trade_total = models.IntegerField()
    skilled_agriculture_related = models.IntegerField()
    skilled_metal_electric_electronic = models.IntegerField()
    skilled_construction = models.IntegerField()
    skilled_textiles_printing = models.IntegerField()
    caring_leisure_service_total = models.IntegerField()
    caring_personal_service = models.IntegerField()
    leisure_travel_related_service = models.IntegerField()
    community_civil_enforcement = models.IntegerField()
    sales_cust_svc_total = models.IntegerField()
    sales = models.IntegerField()
    cust_svc = models.IntegerField()
    process_plant_machine_total = models.IntegerField()
    process_plant_machine_operatives = models.IntegerField()
    transport_machines_drivers = models.IntegerField()
    elementary_occupations_total = models.IntegerField()
    elementary_trades = models.IntegerField()
    elementary_admin_service = models.IntegerField()


class SexualOrientation(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_16 = models.IntegerField()
    heterosexual = models.IntegerField()
    gay_lesbian = models.IntegerField()
    bisexual = models.IntegerField()
    other = models.IntegerField()
    not_answered = models.IntegerField()


class TransStatus(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_16 = models.IntegerField()
    no_trans_history = models.IntegerField()
    yes_trans_history = models.IntegerField()
    not_answered = models.IntegerField()


class TravelToStudy(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_4 = models.IntegerField()
    mainly_from_home = models.IntegerField()
    less_than_2k = models.IntegerField()
    _2km_to_5km = models.IntegerField()
    _5km_to_10km = models.IntegerField()
    _10km_to_20km = models.IntegerField()
    _20km_to_30km = models.IntegerField()
    _30km_to_40km = models.IntegerField()
    _40km_to_60km = models.IntegerField()
    _60km_and_over = models.IntegerField()
    no_study_or_study_abroad = models.IntegerField()


class TravelToWork(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    employed_population_over_16 = models.IntegerField()
    mainly_from_home = models.IntegerField()
    _2km_and_under = models.IntegerField()
    _2km_to_5km = models.IntegerField()
    _5km_to_10km = models.IntegerField()
    _10km_to_20km = models.IntegerField()
    _20km_to_30km = models.IntegerField()
    _30km_to_40km = models.IntegerField()
    _40km_to_60km = models.IntegerField()
    _60km_and_over = models.IntegerField()
    no_work_or_work_abroad = models.IntegerField()


class UnpaidCare(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population_over_3 = models.IntegerField()
    no = models.IntegerField()
    all_unpaid_carers = models.IntegerField()
    _1_to_19_hours_week = models.IntegerField()
    _20_to_34_hours_week = models.IntegerField()
    _35_to_49_hours_week = models.IntegerField()
    _50_or_more_hours_week = models.IntegerField()


class YearArrivalUK(models.Model):
    constituency_id = models.IntegerField(primary_key=True)
    constituency = models.CharField(max_length=50)
    population = models.IntegerField()
    born_in_UK = models.IntegerField()
    Before_1941 = models.IntegerField()
    _1941_1950 = models.IntegerField()
    _1951_1960 = models.IntegerField()
    _1961_1970 = models.IntegerField()
    _1971_1980 = models.IntegerField()
    _1981_1990 = models.IntegerField()
    _1991_2000 = models.IntegerField()
    _2001_2010 = models.IntegerField()
    _2011_2013 = models.IntegerField()
    _2014_2016 = models.IntegerField()
    _2017_2019 = models.IntegerField()
    _2020_2022 = models.IntegerField()
